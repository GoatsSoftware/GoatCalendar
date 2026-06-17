import { API_CONFIG } from "./config.js";
import { clearSession, getAccessToken, getSession, saveSession } from "./session.js";

async function readResponse(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function request(baseUrl, path, options = {}) {
  const headers = new Headers(options.headers ?? {});
  const token = getAccessToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
  });
  const payload = await readResponse(response);

  if (!response.ok) {
    const detail = typeof payload === "object" && payload !== null ? payload.detail : payload;
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return payload;
}

function jsonBody(data) {
  return JSON.stringify(data);
}

export const authApi = {
  async login(email, password) {
    const formData = new URLSearchParams();
    formData.set("username", email);
    formData.set("password", password);

    const tokens = await request(API_CONFIG.authBaseUrl, "/authentication/auth", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });
    const session = { tokens, user: null };
    saveSession(session);

    const user = await this.me();
    saveSession({ tokens, user });

    return { tokens, user };
  },

  me() {
    return request(API_CONFIG.authBaseUrl, "/authentication/me");
  },

  refresh() {
    const refreshToken = getSession()?.tokens?.refresh_token;

    if (!refreshToken) {
      clearSession();
      throw new Error("No refresh token available");
    }

    return request(
      API_CONFIG.authBaseUrl,
      `/authentication/refresh-access-token?refresh_token=${encodeURIComponent(refreshToken)}`,
      { method: "POST" },
    );
  },

  users() {
    return request(API_CONFIG.authBaseUrl, "/users");
  },

  searchUsers(query) {
    return request(API_CONFIG.authBaseUrl, `/users/search?q=${encodeURIComponent(query)}`);
  },

  updateMe(data) {
    return request(API_CONFIG.authBaseUrl, "/users/me", {
      method: "PUT",
      body: jsonBody(data),
    });
  },

  health() {
    return request(API_CONFIG.authBaseUrl, "/auth_monitoring/health");
  },
};

export const boardApi = {
  health() {
    return request(API_CONFIG.boardBaseUrl, "/board_monitoring/health");
  },

  boards() {
    return request(API_CONFIG.boardBaseUrl, "/boards");
  },

  board(boardId) {
    return request(API_CONFIG.boardBaseUrl, `/boards/${boardId}`);
  },

  createBoard(data) {
    return request(API_CONFIG.boardBaseUrl, "/boards", {
      method: "POST",
      body: jsonBody(data),
    });
  },

  updateBoard(boardId, data) {
    return request(API_CONFIG.boardBaseUrl, `/boards/${boardId}`, {
      method: "PUT",
      body: jsonBody(data),
    });
  },

  deleteBoard(boardId) {
    return request(API_CONFIG.boardBaseUrl, `/boards/${boardId}`, { method: "DELETE" });
  },

  columns(boardId) {
    return request(API_CONFIG.boardBaseUrl, `/board-columns/board/${boardId}`);
  },

  createColumn(data) {
    return request(API_CONFIG.boardBaseUrl, "/board-columns", {
      method: "POST",
      body: jsonBody(data),
    });
  },

  deleteColumn(columnId) {
    return request(API_CONFIG.boardBaseUrl, `/board-columns/${columnId}`, { method: "DELETE" });
  },

  rows(boardId) {
    return request(API_CONFIG.boardBaseUrl, `/board-rows/board/${boardId}`);
  },

  createRow(boardId) {
    return request(API_CONFIG.boardBaseUrl, "/board-rows", {
      method: "POST",
      body: jsonBody({ board_id: boardId }),
    });
  },

  deleteRow(rowId) {
    return request(API_CONFIG.boardBaseUrl, `/board-rows/${rowId}`, { method: "DELETE" });
  },

  createTask(data) {
    return request(API_CONFIG.boardBaseUrl, "/board-row-tasks", {
      method: "POST",
      body: jsonBody(data),
    });
  },

  updateTask(taskId, data) {
    return request(API_CONFIG.boardBaseUrl, `/board-row-tasks/${taskId}`, {
      method: "PUT",
      body: jsonBody(data),
    });
  },

  deleteTask(taskId) {
    return request(API_CONFIG.boardBaseUrl, `/board-row-tasks/${taskId}`, { method: "DELETE" });
  },

  createComment(data) {
    return request(API_CONFIG.boardBaseUrl, "/board-row-comments", {
      method: "POST",
      body: jsonBody(data),
    });
  },

  updateComment(commentId, data) {
    return request(API_CONFIG.boardBaseUrl, `/board-row-comments/${commentId}`, {
      method: "PUT",
      body: jsonBody(data),
    });
  },

  deleteComment(commentId) {
    return request(API_CONFIG.boardBaseUrl, `/board-row-comments/${commentId}`, {
      method: "DELETE",
    });
  },

  events(boardId) {
    return request(API_CONFIG.boardBaseUrl, `/board-events/board/${boardId}`);
  },

  createEvent(data) {
    return request(API_CONFIG.boardBaseUrl, "/board-events", {
      method: "POST",
      body: jsonBody(data),
    });
  },

  updateEvent(eventId, data) {
    return request(API_CONFIG.boardBaseUrl, `/board-events/${eventId}`, {
      method: "PUT",
      body: jsonBody(data),
    });
  },

  deleteEvent(eventId) {
    return request(API_CONFIG.boardBaseUrl, `/board-events/${eventId}`, { method: "DELETE" });
  },

  permissions(boardId) {
    return request(API_CONFIG.boardBaseUrl, `/boards/${boardId}/permissions`);
  },

  addPermission(boardId, data) {
    return request(API_CONFIG.boardBaseUrl, `/boards/${boardId}/permissions`, {
      method: "POST",
      body: jsonBody(data),
    });
  },

  updatePermission(boardId, userId, data) {
    return request(API_CONFIG.boardBaseUrl, `/boards/${boardId}/permissions/${userId}`, {
      method: "PUT",
      body: jsonBody(data),
    });
  },

  removePermission(boardId, userId) {
    return request(API_CONFIG.boardBaseUrl, `/boards/${boardId}/permissions/${userId}`, {
      method: "DELETE",
    });
  },
};
