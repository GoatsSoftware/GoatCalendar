import { authApi } from "../api.js";
import { DEMO_PASSWORD } from "../config.js";
import { $, $all, setFeedback } from "../dom.js";
import { getSession } from "../session.js";

const loginForm = $("#login-form");
const feedback = $("#login-feedback");
const emailInput = $("#email");
const passwordInput = $("#password");

if (getSession()?.tokens?.access_token) {
  window.location.href = "./dashboard.html";
}

$all("[data-demo-user]").forEach((button) => {
  button.addEventListener("click", () => {
    emailInput.value = button.dataset.demoUser;
    passwordInput.value = DEMO_PASSWORD;
    emailInput.focus();
  });
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setFeedback(feedback, "Signing in...");

  try {
    await authApi.login(emailInput.value, passwordInput.value);
    setFeedback(feedback, "Signed in. Redirecting...", "success");
    window.location.href = "./dashboard.html";
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});
