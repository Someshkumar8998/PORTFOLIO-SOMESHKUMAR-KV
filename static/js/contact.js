// contact.js — simple client-side validation before the Django form
// handles the real (server-side) validation and saving.

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("contactForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const name = form.querySelector("#id_name");
    const email = form.querySelector("#id_email");
    const message = form.querySelector("#id_message");

    let valid = true;
    const errors = [];

    if (name && !name.value.trim()) {
      valid = false;
      errors.push("Please enter your name.");
    }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
      valid = false;
      errors.push("Please enter a valid email address.");
    }
    if (message && message.value.trim().length < 10) {
      valid = false;
      errors.push("Message should be at least 10 characters.");
    }

    if (!valid) {
      e.preventDefault();
      alert(errors.join("\n"));
    }
  });
});
