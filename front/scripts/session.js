const SESSION_KEY = "goatcalendar.session";

export function saveSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function getSession() {
  const rawSession = localStorage.getItem(SESSION_KEY);

  if (!rawSession) {
    return null;
  }

  try {
    return JSON.parse(rawSession);
  } catch {
    clearSession();
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

export function requireSession() {
  const session = getSession();

  if (!session?.tokens?.access_token) {
    window.location.href = "./index.html";
    return null;
  }

  return session;
}

export function getAccessToken() {
  return getSession()?.tokens?.access_token ?? null;
}
