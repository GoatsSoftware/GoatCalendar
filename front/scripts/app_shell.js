import { authApi } from "./api.js";
import { $, formatUser, setFeedback } from "./dom.js";
import { clearSession, getSession } from "./session.js";

export async function hydrateShell(feedbackElement = null) {
  const session = getSession();
  const userChip = $("#current-user");

  if (session?.user && userChip) {
    userChip.textContent = formatUser(session.user);
  }

  $("#logout-button")?.addEventListener("click", () => {
    clearSession();
    window.location.href = "./index.html";
  });

  try {
    const user = await authApi.me();

    if (userChip) {
      userChip.textContent = formatUser(user);
    }

    return user;
  } catch (error) {
    setFeedback(feedbackElement, error.message, "error");
    return null;
  }
}
