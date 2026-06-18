import { authApi, boardApi } from "../api.js";
import { hydrateShell } from "../app_shell.js";
import {
  $,
  createElement,
  empty,
  formDataToObject,
  formatUser,
  setFeedback,
} from "../dom.js";
import { getSession, requireSession, saveSession } from "../session.js";

const session = requireSession();
const boardsList = $("#boards-list");
const usersList = $("#users-list");
const boardCount = $("#board-count");
const feedback = $("#dashboard-feedback");
const createBoardForm = $("#create-board-form");
const searchUsersForm = $("#search-users-form");
const profileForm = $("#profile-form");
const boardDetailLink = $("#board-detail-link");

if (session) {
  hydrateShell(feedback).then((user) => {
    if (user) {
      fillProfile(user);
    }
  });
  loadDashboard();
}

$("#refresh-button")?.addEventListener("click", loadDashboard);

createBoardForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = formDataToObject(createBoardForm);
  setFeedback(feedback, "Creating board...");

  try {
    await boardApi.createBoard({
      name: data.name,
      description: data.description ?? "",
    });
    createBoardForm.reset();
    setFeedback(feedback, "Board created.", "success");
    await loadBoards();
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});

searchUsersForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = new FormData(searchUsersForm).get("q")?.trim();

  if (!query) {
    await loadUsers();
    return;
  }

  try {
    renderUsers(await authApi.searchUsers(query));
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = formDataToObject(profileForm);
  setFeedback(feedback, "Updating profile...");

  try {
    const user = await authApi.updateMe(data);
    const currentSession = getSession();
    saveSession({ ...currentSession, user });
    fillProfile(user);
    $("#current-user").textContent = formatUser(user);
    setFeedback(feedback, "Profile updated.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});

async function loadDashboard() {
  setFeedback(feedback, "Loading workspace...");

  try {
    const [authHealth, boardHealth] = await Promise.all([
      authApi.health(),
      boardApi.health(),
      loadBoards(),
      loadUsers(),
    ]);
    setFeedback(
      feedback,
      `Services ready: ${authHealth.status} / ${boardHealth.status}`,
      "success",
    );
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function loadBoards() {
  const boards = await boardApi.boards();
  renderBoards(boards);
}

async function loadUsers() {
  const users = await authApi.users();
  renderUsers(users);
}

function renderBoards(boards) {
  empty(boardsList);
  boardCount.textContent = String(boards.length);
  syncBoardDetailLink(boards[0]?.id);

  if (boards.length === 0) {
    boardsList.append(createElement("p", "muted", "No boards yet."));
    return;
  }

  boards.forEach((board) => {
    const item = createElement("article", "list-item board-card");
    const title = createElement("strong", "", board.name ?? "Untitled board");
    const description = createElement("p", "muted", board.description || "No description");
    const meta = createElement(
      "p",
      "muted",
      `${board.columns?.length ?? 0} columns - ${board.events?.length ?? 0} events`,
    );
    const actions = createElement("div", "list-item-actions");
    const openLink = createElement("a", "button button-primary", "Open");
    const renameButton = createElement("button", "button button-secondary", "Rename");
    const deleteButton = createElement("button", "button button-secondary", "Delete");

    openLink.href = `./board.html?board_id=${encodeURIComponent(board.id)}`;
    renameButton.type = "button";
    deleteButton.type = "button";
    renameButton.addEventListener("click", async () => {
      const name = window.prompt("Board name", board.name ?? "");

      if (!name) {
        return;
      }

      try {
        await boardApi.updateBoard(board.id, {
          name,
          description: board.description ?? "",
        });
        await loadBoards();
        setFeedback(feedback, "Board updated.", "success");
      } catch (error) {
        setFeedback(feedback, error.message, "error");
      }
    });
    deleteButton.addEventListener("click", async () => {
      try {
        await boardApi.deleteBoard(board.id);
        await loadBoards();
        setFeedback(feedback, "Board deleted.", "success");
      } catch (error) {
        setFeedback(feedback, error.message, "error");
      }
    });

    actions.append(openLink, renameButton, deleteButton);
    item.append(title, description, meta, actions);
    boardsList.append(item);
  });
}

function syncBoardDetailLink(boardId) {
  if (!boardDetailLink) {
    return;
  }

  if (!boardId) {
    boardDetailLink.href = "./board.html";
    boardDetailLink.setAttribute("aria-disabled", "true");
    return;
  }

  boardDetailLink.href = `./board.html?board_id=${encodeURIComponent(boardId)}`;
  boardDetailLink.removeAttribute("aria-disabled");
}

function renderUsers(users) {
  empty(usersList);

  if (users.length === 0) {
    usersList.append(createElement("p", "muted", "No users found."));
    return;
  }

  users.forEach((user) => {
    const item = createElement("article", "list-item");
    item.append(
      createElement("strong", "", formatUser(user)),
      createElement("span", "muted", user.email_address),
      createElement("code", "muted", user.id),
    );
    usersList.append(item);
  });
}

function fillProfile(user) {
  profileForm.elements.first_name.value = user.first_name ?? "";
  profileForm.elements.last_name.value = user.last_name ?? "";
  profileForm.elements.email_address.value = user.email_address ?? "";
}
