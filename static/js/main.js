// main.js — navigation, mobile menu, custom cursor

document.addEventListener("DOMContentLoaded", () => {
  /* ---------- Mobile nav toggle ---------- */
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      navLinks.classList.toggle("is-open");
    });

    navLinks.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => navLinks.classList.remove("is-open"));
    });
  }

  /* ---------- Active nav link highlighting ---------- */
  const setActiveNavLink = () => {
    const navLinksContainer = document.getElementById("navLinks");
    if (!navLinksContainer) return;

    const navLinks = navLinksContainer.querySelectorAll(".nav-link:not(.nav-link--cta)");
    const currentPath = window.location.pathname;

    navLinks.forEach((link) => {
      link.classList.remove("nav-link--active");
      const href = link.getAttribute("href");
      
      // Match exact path or root path
      if (currentPath === href || (currentPath === "/" && href === "/")) {
        link.classList.add("nav-link--active");
      }
    });
  };

  // Set active link on page load
  setActiveNavLink();

  // Also handle popstate for browser back/forward
  window.addEventListener("popstate", setActiveNavLink);

  /* ---------- Navbar hide on scroll down / show on scroll up ---------- */
  const navbar = document.getElementById("navbar");
  let lastScroll = 0;

  if (navbar) {
    window.addEventListener("scroll", () => {
      const current = window.scrollY;
      if (current > lastScroll && current > 120) {
        navbar.classList.add("navbar--hidden");
      } else {
        navbar.classList.remove("navbar--hidden");
      }
      lastScroll = current;
    });
  }

  /* ---------- Custom cursor (desktop only) ---------- */
  const cursorDot = document.getElementById("cursorDot");
  const cursorRing = document.getElementById("cursorRing");
  const isTouch = window.matchMedia("(hover: none) and (pointer: coarse)").matches;

  if (cursorDot && cursorRing && !isTouch) {
    let ringX = 0, ringY = 0, mouseX = 0, mouseY = 0;

    window.addEventListener("mousemove", (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursorDot.style.left = `${mouseX}px`;
      cursorDot.style.top = `${mouseY}px`;
    });

    const animateRing = () => {
      ringX += (mouseX - ringX) * 0.18;
      ringY += (mouseY - ringY) * 0.18;
      cursorRing.style.left = `${ringX}px`;
      cursorRing.style.top = `${ringY}px`;
      requestAnimationFrame(animateRing);
    };
    animateRing();

    document.querySelectorAll("a, button, .card, .skill-chip").forEach((el) => {
      el.addEventListener("mouseenter", () => {
        cursorRing.style.transform = "translate(-50%, -50%) scale(1.6)";
      });
      el.addEventListener("mouseleave", () => {
        cursorRing.style.transform = "translate(-50%, -50%) scale(1)";
      });
    });
  } else if (cursorDot && cursorRing) {
    cursorDot.style.display = "none";
    cursorRing.style.display = "none";
  }
});
