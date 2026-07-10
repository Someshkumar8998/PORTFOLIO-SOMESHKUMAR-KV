"""
Plain Python WSGI web application — replaces Django's urls.py + views.py +
forms.py + settings TEMPLATES + admin messages framework.

Uses only:
  - Python's standard library (wsgiref, http.cookies, urllib.parse, hmac, mimetypes)
  - Jinja2, used strictly as a templating library (no web framework behaviour)

Run directly for local dev:  python run.py
Run in production:           gunicorn app:application
"""

import hmac
import hashlib
import json
import base64
import re
import mimetypes
import os
import secrets
import logging
from http import cookies
from urllib.parse import parse_qs, urlencode

from jinja2 import Environment, FileSystemLoader, select_autoescape

import config
import db
from data import (
    PROFILE, DEFAULT_SKILLS, DEFAULT_SERVICES, DEFAULT_PROJECTS,
    DEFAULT_EXPERIENCE, DEFAULT_CERTIFICATIONS,
)
from mailer import send_contact_notification, EmailConfigError

logger = logging.getLogger("portfolio")
logging.basicConfig(level=logging.INFO)

db.init_db()

# --------------------------------------------------------------------------
# Templating (Jinja2 used purely as a template renderer)
# --------------------------------------------------------------------------

jinja_env = Environment(
    loader=FileSystemLoader(str(config.TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)

URL_MAP = {
    "index": "/",
    "about": "/about/",
    "projects": "/projects/",
    "services": "/services/",
    "skills": "/skills/",
    "experience": "/experience/",
    "resume": "/resume/",
    "resume_pdf_view": "/resume/view-pdf/",
    "download_resume": "/resume/download/",
    "contact": "/contact/",
}

jinja_env.globals["static"] = lambda path: "/static/" + path.lstrip("/")
jinja_env.globals["url"] = lambda name: URL_MAP.get(name, "/")


def render(template_name, **context):
    template = jinja_env.get_template(template_name)
    return template.render(**context)


# --------------------------------------------------------------------------
# Data helpers — DB first, fall back to defaults (same behaviour as before)
# --------------------------------------------------------------------------

def get_skills():
    rows = db.get_skills()
    return rows if rows else [{"name": s} for s in DEFAULT_SKILLS]


def get_services():
    rows = db.get_services()
    return rows if rows else DEFAULT_SERVICES


def get_projects():
    rows = db.get_projects()
    return rows if rows else DEFAULT_PROJECTS


def get_experience():
    rows = db.get_experience()
    return rows if rows else DEFAULT_EXPERIENCE


def get_certifications():
    rows = db.get_certifications()
    return rows if rows else [{"title": c} for c in DEFAULT_CERTIFICATIONS]


# --------------------------------------------------------------------------
# Request / Response helpers
# --------------------------------------------------------------------------

class Request:
    def __init__(self, environ):
        self.environ = environ
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.path = environ.get("PATH_INFO", "/") or "/"
        self.GET = {k: v[0] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()}
        self.cookies = cookies.SimpleCookie()
        if environ.get("HTTP_COOKIE"):
            self.cookies.load(environ["HTTP_COOKIE"])
        self.POST = {}
        if self.method == "POST":
            try:
                length = int(environ.get("CONTENT_LENGTH") or 0)
            except ValueError:
                length = 0
            body = environ["wsgi.input"].read(length) if length else b""
            self.POST = {k: v[0] for k, v in parse_qs(body.decode("utf-8")).items()}

    def cookie(self, name, default=None):
        morsel = self.cookies.get(name)
        return morsel.value if morsel else default


class Response:
    def __init__(self, body="", status="200 OK", content_type="text/html; charset=utf-8"):
        self.body = body.encode("utf-8") if isinstance(body, str) else body
        self.status = status
        self.headers = [("Content-Type", content_type)]
        self.cookies_to_set = []

    def set_cookie(self, name, value, max_age=None, http_only=True, path="/"):
        parts = [f"{name}={value}", f"Path={path}"]
        if max_age is not None:
            parts.append(f"Max-Age={max_age}")
        if http_only:
            parts.append("HttpOnly")
        parts.append("SameSite=Lax")
        self.headers.append(("Set-Cookie", "; ".join(parts)))

    def delete_cookie(self, name, path="/"):
        self.headers.append(("Set-Cookie", f"{name}=; Path={path}; Max-Age=0"))


def redirect(path, status="303 See Other"):
    resp = Response("", status=status)
    resp.headers.append(("Location", path))
    return resp


def not_found():
    return Response("<h1>404 Not Found</h1>", status="404 Not Found")


# --------------------------------------------------------------------------
# CSRF (stateless double-submit-cookie pattern — no server-side session needed)
# --------------------------------------------------------------------------

def _sign(value: str) -> str:
    mac = hmac.new(config.SECRET_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()
    return f"{value}.{mac}"


def _get_or_create_csrf_token(request: Request):
    existing = request.cookie("csrf_token")
    if existing and _verify_signed(existing):
        return existing
    raw = secrets.token_hex(16)
    return _sign(raw)


def _verify_signed(signed_value: str) -> bool:
    if "." not in signed_value:
        return False
    raw, _, mac = signed_value.rpartition(".")
    expected = hmac.new(config.SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, expected)


def csrf_valid(request: Request) -> bool:
    cookie_token = request.cookie("csrf_token")
    form_token = request.POST.get("csrf_token")
    if not cookie_token or not form_token:
        return False
    return hmac.compare_digest(cookie_token, form_token) and _verify_signed(cookie_token)


# --------------------------------------------------------------------------
# Flash messages (one-time, stored signed in a short-lived cookie)
# --------------------------------------------------------------------------

def _encode_flash(messages_list):
    payload = json.dumps(messages_list).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii")


def _decode_flash(raw):
    try:
        return json.loads(base64.urlsafe_b64decode(raw.encode("ascii")))
    except Exception:
        return []


def pop_messages(request: Request, response: Response):
    raw = request.cookie("flash")
    if not raw:
        return []
    response.delete_cookie("flash")
    return _decode_flash(raw)


# --------------------------------------------------------------------------
# Simple email/field validation (replaces Django's ModelForm validation)
# --------------------------------------------------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_contact_form(data):
    errors = {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not name:
        errors["name"] = "This field is required."
    elif len(name) > 150:
        errors["name"] = "Name is too long."

    if not email:
        errors["email"] = "This field is required."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."

    if not message:
        errors["message"] = "This field is required."

    return errors, {"name": name, "email": email, "subject": subject, "message": message}


# --------------------------------------------------------------------------
# View handlers (mirrors the original Django views.py)
# --------------------------------------------------------------------------

def base_context(request, response, page_title):
    return {
        "profile": PROFILE,
        "page_title": page_title,
        "messages": pop_messages(request, response),
        "csrf_token": _get_or_create_csrf_token(request),
    }


def view_index(request, response):
    ctx = base_context(request, response, "Home")
    ctx.update(projects=get_projects()[:3], skills=get_skills())
    return Response(render("index.html", **ctx))


def view_about(request, response):
    ctx = base_context(request, response, "About")
    ctx.update(skills=get_skills(), certifications=get_certifications())
    return Response(render("about.html", **ctx))


def view_projects(request, response):
    ctx = base_context(request, response, "Projects")
    ctx.update(projects=get_projects())
    return Response(render("projects.html", **ctx))


def view_services(request, response):
    ctx = base_context(request, response, "Services")
    ctx.update(services=get_services())
    return Response(render("services.html", **ctx))


def view_skills(request, response):
    ctx = base_context(request, response, "Skills")
    ctx.update(skills=get_skills())
    return Response(render("skills.html", **ctx))


def view_experience(request, response):
    ctx = base_context(request, response, "Experience")
    ctx.update(experience=get_experience())
    return Response(render("experience.html", **ctx))


def view_resume(request, response):
    ctx = base_context(request, response, "Resume")
    ctx.update(
        certifications=get_certifications(),
        resume_pdf_exists=config.RESUME_PDF_PATH.is_file(),
    )
    return Response(render("resume.html", **ctx))


def _serve_resume_pdf(as_attachment: bool):
    if not config.RESUME_PDF_PATH.is_file():
        logger.error("Resume PDF not found at: %s", config.RESUME_PDF_PATH)
        return not_found()
    try:
        data = config.RESUME_PDF_PATH.read_bytes()
    except OSError as e:
        logger.error("Could not open resume PDF: %s", e)
        return not_found()

    resp = Response(data, content_type="application/pdf")
    disposition = "attachment" if as_attachment else "inline"
    resp.headers.append(("Content-Disposition", f'{disposition}; filename="resume.pdf"'))
    return resp


def view_resume_pdf(request, response):
    return _serve_resume_pdf(as_attachment=False)


def view_download_resume(request, response):
    return _serve_resume_pdf(as_attachment=True)


def view_contact(request, response):
    if request.method == "POST":
        if not csrf_valid(request):
            ctx = base_context(request, response, "Contact")
            ctx.update(form_data=request.POST, form_errors={"__all__": "Form expired, please try again."})
            return Response(render("contact.html", **ctx), status="400 Bad Request")

        errors, cleaned = validate_contact_form(request.POST)
        if not errors:
            db.save_contact_message(cleaned["name"], cleaned["email"], cleaned["subject"], cleaned["message"])

            flash_messages = []
            try:
                send_contact_notification(
                    name=cleaned["name"], email=cleaned["email"],
                    subject=cleaned["subject"], message=cleaned["message"],
                )
                flash_messages.append({"tags": "success", "text": "Thanks for reaching out! I'll get back to you soon."})
            except EmailConfigError as e:
                logger.error("[CONTACT EMAIL ERROR] %s", e)
                flash_messages.append({
                    "tags": "warning",
                    "text": "Your message was received, but the email notification couldn't be sent right now.",
                })
            except Exception as e:
                logger.error("[CONTACT EMAIL ERROR] %s", e)
                flash_messages.append({
                    "tags": "warning",
                    "text": "Your message was received, but the email notification couldn't be sent right now.",
                })

            redirect_resp = redirect(URL_MAP["contact"])
            redirect_resp.set_cookie("flash", _encode_flash(flash_messages), max_age=30)
            # Preserve/refresh CSRF cookie on redirect too
            redirect_resp.set_cookie("csrf_token", ctx_csrf_token(request), max_age=3600)
            return redirect_resp

        ctx = base_context(request, response, "Contact")
        ctx.update(form_data=cleaned, form_errors=errors)
        return Response(render("contact.html", **ctx), status="400 Bad Request")

    ctx = base_context(request, response, "Contact")
    ctx.update(form_data={}, form_errors={})
    return Response(render("contact.html", **ctx))


def ctx_csrf_token(request):
    return _get_or_create_csrf_token(request)


# --------------------------------------------------------------------------
# Static file serving (development convenience — use nginx/whitenoise-style
# static hosting in real production, but this keeps everything self-contained)
# --------------------------------------------------------------------------

def serve_static(request, response):
    rel_path = request.path[len("/static/"):]
    # Prevent path traversal
    if ".." in rel_path.split("/"):
        return not_found()
    file_path = config.STATIC_DIR / rel_path
    if not file_path.is_file():
        return not_found()

    content_type, _ = mimetypes.guess_type(str(file_path))
    resp = Response(file_path.read_bytes(), content_type=content_type or "application/octet-stream")
    return resp


# --------------------------------------------------------------------------
# Routing
# --------------------------------------------------------------------------

ROUTES = [
    (r"^/$", view_index),
    (r"^/about/$", view_about),
    (r"^/projects/$", view_projects),
    (r"^/services/$", view_services),
    (r"^/skills/$", view_skills),
    (r"^/experience/$", view_experience),
    (r"^/resume/$", view_resume),
    (r"^/resume/view-pdf/$", view_resume_pdf),
    (r"^/resume/download/$", view_download_resume),
    (r"^/contact/$", view_contact),
]
ROUTES = [(re.compile(pattern), handler) for pattern, handler in ROUTES]


def dispatch(request: Request) -> Response:
    if request.path.startswith("/static/"):
        return serve_static(request, Response())

    for pattern, handler in ROUTES:
        if pattern.match(request.path):
            response = Response()
            result = handler(request, response)
            # Make sure the CSRF cookie always gets (re)issued on GET pages
            if request.method == "GET" and not any(h[0] == "Set-Cookie" and "csrf_token" in h[1] for h in result.headers):
                result.set_cookie("csrf_token", ctx_csrf_token(request), max_age=3600)
            return result

    return not_found()


# --------------------------------------------------------------------------
# WSGI entrypoint
# --------------------------------------------------------------------------

def application(environ, start_response):
    request = Request(environ)
    try:
        response = dispatch(request)
    except Exception:
        logger.exception("Unhandled error while processing %s %s", request.method, request.path)
        response = Response("<h1>500 Internal Server Error</h1>", status="500 Internal Server Error")

    start_response(response.status, response.headers)
    return [response.body]


# Vercel's Python runtime loads app.py as the entrypoint (it's first in its
# search order) and requires the WSGI callable to be exposed as `app`.
app = application