export function $(selector, scope = document) {
  return scope.querySelector(selector);
}

export function $all(selector, scope = document) {
  return [...scope.querySelectorAll(selector)];
}

export function setFeedback(element, message, type = "") {
  if (!element) {
    return;
  }

  element.textContent = message;
  element.classList.remove("error", "success");

  if (type) {
    element.classList.add(type);
  }
}

export function empty(element) {
  element.replaceChildren();
}

export function createElement(tag, className, text) {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  if (text !== undefined) {
    element.textContent = text;
  }

  return element;
}

export function formDataToObject(form) {
  return Object.fromEntries(
    [...new FormData(form).entries()].filter(([, value]) => String(value).trim() !== ""),
  );
}

export function formatUser(user) {
  if (!user) {
    return "Unknown user";
  }

  return `${user.first_name ?? ""} ${user.last_name ?? ""}`.trim() || user.email_address;
}

export function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("fr-FR").format(new Date(value));
}
