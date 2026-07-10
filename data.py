"""
Static profile data + default fallback content for the portfolio site.
This replaces the hard-coded dictionaries that used to live in Django's views.py.
"""

PROFILE = {
    "name": "Someshkumar KV",
    "email": "someshkumarkv8998@gmail.com",
    "phone": "+91 9384108526",
    "tagline": "Passionate Python Full Stack Developer building responsive, scalable and modern web applications.",
    "description": (
        "Python Full Stack Developer with hands-on experience building responsive web "
        "applications using React.js, Flask, Django and MySQL. BCA Graduate (2026) from "
        "Bharathiar University, Coimbatore."
    ),
    "role_short": "Python Full Stack Developer",
    "role_detailed": "Python • React.js • Flask • Django • MySQL",
    "based_in": "Coimbatore, Tamil Nadu",
    "availability": "Open to Full-Time Opportunities",
    "available": True,
    "badge_text": "🔍 Seeking Full-Time & Internship",
    "bio": (
        "I'm Someshkumar KV, a passionate Python Full Stack Developer and BCA graduate "
        "from Bharathiar University. I have hands-on experience in developing responsive "
        "web applications using Python, React.js, Flask, Django, JavaScript, HTML5, CSS3, "
        "Bootstrap, and MySQL. During my internship at IDM TechPark, I worked on full-stack "
        "web development, database integration, and modern frontend technologies. I enjoy "
        "solving real-world problems, learning new technologies, and building scalable, "
        "user-friendly applications."
    ),
    "stats": [
        {"value": "4+", "label": "Projects"},
        {"value": "1", "label": "Internship"},
        {"value": "2026", "label": "Graduate"},
    ],
    "socials": [
        {"label": "GitHub", "href": "https://github.com/Someshkumar8998"},
        {"label": "LinkedIn", "href": "https://www.linkedin.com/in/somesh-kumar-kv-8193b42a2"},
    ],
}

DEFAULT_SKILLS = [
    "Python", "React.js", "Flask", "Django", "JavaScript", "HTML5",
    "CSS3", "Bootstrap", "MySQL", "Git", "GitHub", "REST API",
]

DEFAULT_SERVICES = [
    {
        "icon": "code",
        "title": "Full Stack Web Development",
        "description": "End-to-end web applications built with Python, Django, Flask and React.js — from database design to a polished, responsive UI.",
    },
    {
        "icon": "server",
        "title": "Backend & API Development",
        "description": "REST APIs and server-side logic using Django and Flask, with clean architecture and MySQL data modelling.",
    },
    {
        "icon": "layout",
        "title": "Responsive Frontend Development",
        "description": "Modern, mobile-first interfaces using React.js, HTML5, CSS3, Bootstrap and JavaScript.",
    },
    {
        "icon": "database",
        "title": "Database Design & Integration",
        "description": "Schema design, query optimisation and integration of MySQL databases into full-stack applications.",
    },
]

DEFAULT_PROJECTS = [
    {
        "title": "MedCare Hub",
        "subtitle": "Healthcare Management System",
        "project_type": "Django Full Stack",
        "link": "https://github.com/Someshkumar8998/MedCare-Hub",
        "description": "A healthcare management system developed using Django, Python and MySQL with patient registration, appointment booking, prescriptions, doctor management and admin dashboard.",
        "image": "medcare.png",
        "video": None,
        "tech_list": ["Python", "Django", "MySQL", "HTML", "CSS", "Bootstrap", "JavaScript"],
    },
    {
        "title": "GitHub Profile Analyzer",
        "subtitle": "React.js Dashboard",
        "project_type": "Web Application",
        "link": "https://github.com/Someshkumar8998/GitHub-Profile-Analyzer",
        "image": "github-analyzer.png",
        "video": None,
        "tech_list": ["React.js", "Bootstrap", "Chart.js", "GitHub API"],
        "description": "A React-based web application that analyzes GitHub user profiles and visualizes repositories, followers, following, and contribution statistics using interactive charts.",
    },
    {
        "title": "Energy Forecasting System",
        "subtitle": "Machine Learning + IoT",
        "project_type": "ML Application",
        "link": "https://github.com/Someshkumar8998/Energy-Consumption",
        "image": "energy-forecast.png",
        "video": None,
        "tech_list": ["Python", "Flask", "Machine Learning", "IoT", "MySQL"],
        "description": "Machine learning-based energy forecasting system integrated with IoT sensors for monitoring, visualization and prediction of future energy consumption.",
    },
    {
        "title": "Online Bug Tracking System",
        "subtitle": "PHP + MySQL",
        "project_type": "Web Application",
        "link": "https://github.com/Someshkumar8998/online-bug-tracking-system",
        "image": "bug-tracker.png",
        "video": None,
        "tech_list": ["HTML", "CSS", "JavaScript", "PHP", "MySQL", "XAMPP"],
        "description": "A web application for tracking and managing software bugs, implemented with PHP and MySQL.",
    },
    {
        "title": "Table Reservation System",
        "subtitle": "PHP + MySQL",
        "project_type": "Web Application",
        "link": "https://github.com/Someshkumar8998/SOMESHKUMAR-KV",
        "image": "restaurant-reservation.jpeg",
        "video": None,
        "tech_list": ["HTML", "CSS", "JavaScript", "PHP", "MySQL", "XAMPP"],
        "description": "A web application for managing restaurant table reservations, implemented with PHP and MySQL.",
    },
]

DEFAULT_EXPERIENCE = [
    {
        "role": "Python Full Stack Developer Intern",
        "company": "IDM TechPark",
        "location": "Coimbatore, Tamil Nadu",
        "period_start": "Jan 2026",
        "period_end": "Present",
        "description": "Worked as a Python Full Stack Developer Intern developing modern web applications using React.js, Flask and MySQL.",
        "bullet_list": [
            "Developed responsive web applications using React.js, Flask and MySQL.",
            "Built frontend interfaces with HTML5, CSS3, JavaScript and Bootstrap.",
            "Integrated backend APIs and performed database operations using MySQL.",
            "Collaborated using Git and GitHub for version control.",
        ],
        "tech_list": ["Python", "React.js", "Flask", "MySQL", "Bootstrap", "Git", "GitHub"],
    },
]

DEFAULT_CERTIFICATIONS = [
    "AWS Cloud Practitioner",
    "Oracle Cloud Machine Learning",
    "Google Cybersecurity",
    "Microsoft Security Analyst",
]
