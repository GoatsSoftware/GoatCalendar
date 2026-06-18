import { boardApi } from "../api.js";
import { hydrateShell } from "../app_shell.js";
import {
  $,
  createElement,
  empty,
  formDataToObject,
  formatDate,
  formatUser,
  setFeedback,
} from "../dom.js";
import { requireSession } from "../session.js";

const session = requireSession();
const feedback = $("#board-feedback");
const boardTitle = $("#board-title");
const loadBoardForm = $("#load-board-form");
const createColumnForm = $("#create-column-form");
const createEventForm = $("#create-event-form");
const addPermissionForm = $("#add-permission-form");
const boardGrid = $("#board-grid");
const columnsList = $("#columns-list");
const eventsList = $("#events-list");
const permissionsList = $("#permissions-list");
const boardDetailLink = $("#board-detail-link");
const DEFAULT_COLUMN_WIDTHS = {
  Row: 150,
  TaskName: 260,
  TaskContent: 320,
  TaskStatus: 150,
  Deadline: 180,
  StartingFrom: 180,
  Comment: 260,
  Actions: 190,
};
const WIDTH_LIMITS = {
  Row: [120, 240],
  TaskName: [180, 420],
  TaskContent: [220, 560],
  TaskStatus: [130, 220],
  Deadline: [150, 260],
  StartingFrom: [150, 260],
  Comment: [200, 560],
  Actions: [170, 320],
};

let state = {
  board: null,
  rows: [],
  columns: [],
  events: [],
  permissions: [],
};
let columnWidths = {};

if (session) {
  hydrateShell(feedback);
  const initialBoardId = new URLSearchParams(window.location.search).get("board_id");

  if (initialBoardId) {
    loadBoardForm.elements.board_id.value = initialBoardId;
    loadBoard(initialBoardId);
  }
}

loadBoardForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadBoard(loadBoardForm.elements.board_id.value.trim());
});

boardDetailLink?.addEventListener("click", async (event) => {
  if (!state.board?.id) {
    return;
  }

  event.preventDefault();
  await loadBoard(state.board.id);
});

$("#create-row-button").addEventListener("click", async () => {
  if (!state.board) {
    setFeedback(feedback, "Load a board first.", "error");
    return;
  }

  try {
    const taskName = window.prompt("Task name", "New task");

    if (!taskName) {
      return;
    }

    const taskContent = window.prompt("Task content", "");

    if (taskContent === null) {
      return;
    }

    const taskColumn = await ensureTaskColumn();
    const row = await boardApi.createRow(state.board.id);
    await boardApi.createTask({
      board_row_id: row.id,
      board_column_id: taskColumn.id,
      task_name: taskName,
      task_content: taskContent,
      task_status: "pending",
      starting_from: today(),
      deadline: today(),
      assigned_to_id: getDefaultAssigneeId(),
    });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Task row created.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});

createColumnForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!state.board) {
    setFeedback(feedback, "Load a board first.", "error");
    return;
  }

  const data = formDataToObject(createColumnForm);
  const columnConfig = readColumnConfig(data);

  if (!columnConfig) {
    setFeedback(feedback, "Choose a column before showing it.", "error");
    return;
  }

  const { name, type } = columnConfig;
  const existingColumn = state.columns.find((column) => column.name === name);

  if (existingColumn) {
    setFeedback(feedback, `${columnLabel(existingColumn.name)} is already visible.`, "success");
    return;
  }

  try {
    await boardApi.createColumn({
      board_id: state.board.id,
      name,
      type,
      position: normalizeColumnPosition(data.position),
    });
    createColumnForm.reset();
    await loadBoard(state.board.id);
    setFeedback(feedback, `${columnLabel(name)} column is now visible.`, "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});

createEventForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!state.board) {
    setFeedback(feedback, "Load a board first.", "error");
    return;
  }

  const data = formDataToObject(createEventForm);

  try {
    await boardApi.createEvent({
      board_id: state.board.id,
      title: data.title ?? null,
      description: data.description ?? "",
      starting_from: data.starting_from,
      deadline: data.deadline,
    });
    createEventForm.reset();
    await loadBoard(state.board.id);
    setFeedback(feedback, "Event created.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});

addPermissionForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!state.board) {
    setFeedback(feedback, "Load a board first.", "error");
    return;
  }

  const data = formDataToObject(addPermissionForm);

  try {
    await boardApi.addPermission(state.board.id, data);
    addPermissionForm.reset();
    await loadBoard(state.board.id);
    setFeedback(feedback, "Permission added.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
});

async function loadBoard(boardId) {
  if (!boardId) {
    return;
  }

  setFeedback(feedback, "Loading board...");

  try {
    const [board, rows, columns, events, permissions] = await Promise.all([
      boardApi.board(boardId),
      boardApi.rows(boardId),
      boardApi.columns(boardId),
      boardApi.events(boardId),
      boardApi.permissions(boardId),
    ]);
    state = { board, rows, columns, events, permissions };
    columnWidths = loadColumnWidths(board.id);
    boardTitle.textContent = board.name ?? "Untitled board";
    syncBoardDetailLink(board.id);
    renderColumns();
    renderBoard();
    renderEvents();
    renderPermissions();
    setFeedback(feedback, "Board loaded.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

function syncBoardDetailLink(boardId) {
  if (!boardDetailLink) {
    return;
  }

  boardDetailLink.href = `./board.html?board_id=${encodeURIComponent(boardId)}`;
}

function renderColumns() {
  empty(columnsList);

  if (state.columns.length === 0) {
    columnsList.append(createElement("span", "muted", "No columns yet."));
    return;
  }

  state.columns.forEach((column) => {
    const chip = createElement("span", "column-chip");
    const label = createElement("span", "column-chip-label");
    const widthControl = renderColumnWidthControl(column.name);

    label.append(
      createElement("strong", "", columnLabel(column.name)),
      createElement("small", "", `${column.type} - position ${column.position}`),
    );

    if (isCoreColumn(column.name)) {
      chip.append(label, widthControl, createElement("span", "column-chip-static", "Core"));
    } else {
      const deleteButton = createElement("button", "", "Remove");

      deleteButton.type = "button";
      deleteButton.title = `Delete ${column.name}`;
      deleteButton.addEventListener("click", () => deleteColumn(column));
      chip.append(label, widthControl, deleteButton);
    }

    columnsList.append(chip);
  });
}

function renderBoard() {
  empty(boardGrid);
  const visibleColumns = getVisibleColumns();
  const template = getTableTemplate(visibleColumns);

  boardGrid.style.setProperty("--board-table-width", `${template.totalWidth}px`);
  boardGrid.append(renderHeaderRow(visibleColumns, template));

  if (state.rows.length === 0) {
    boardGrid.append(createElement("p", "muted", "No rows yet."));
    return;
  }

  state.rows.forEach((row, index) => {
    const line = createElement("article", "table-row");
    applyTableTemplate(line, template);
    line.append(renderRowCell(row, index));
    visibleColumns.forEach((column) => {
      line.append(renderColumnCell(row, column));
    });
    line.append(renderRowActions(row));
    boardGrid.append(line);
  });
}

function renderHeaderRow(visibleColumns, template) {
  const header = createElement("div", "table-row header");
  applyTableTemplate(header, template);
  ["Row", ...visibleColumns.map((column) => columnLabel(column.name)), "Actions"].forEach((label) => {
    header.append(createElement("span", "table-cell", label));
  });
  return header;
}

function renderRowCell(row, index) {
  const cell = createElement("div", "table-cell");
  cell.append(
    createElement("strong", "", `Row ${index + 1}`),
    createElement("span", "muted", row.id),
  );
  return cell;
}

function renderColumnCell(row, column) {
  if (column.name === "TaskName") {
    return renderTaskNameCell(row);
  }

  if (column.name === "TaskContent") {
    return renderTaskContentCell(row);
  }

  if (column.name === "TaskStatus") {
    return renderStatusCell(row);
  }

  if (column.name === "Deadline") {
    return renderTaskDateCell(row, "deadline", "No deadline");
  }

  if (column.name === "StartingFrom") {
    return renderTaskDateCell(row, "starting_from", "No start date");
  }

  if (column.name === "Comment") {
    return renderCommentsCell(row);
  }

  const cell = createElement("div", "table-cell");
  cell.append(createElement("span", "muted", "Not displayed"));
  return cell;
}

function renderTaskNameCell(row) {
  const cell = createElement("div", "table-cell");
  const task = primaryTask(row);

  if (!task) {
    cell.append(createElement("span", "muted", "No task yet"));
    return cell;
  }

  const taskItem = createElement("div", "task-line");
  taskItem.append(
    createElement("strong", "", task.task_name),
    createElement("span", "muted", `v${task.version}`),
  );
  cell.append(taskItem);

  return cell;
}

function renderTaskContentCell(row) {
  const cell = createElement("div", "table-cell");
  const task = primaryTask(row);

  if (!task) {
    cell.append(createElement("span", "muted", "Use Create task"));
    return cell;
  }

  cell.append(createElement("span", "task-content", task.task_content || "No content"));
  return cell;
}

function renderStatusCell(row) {
  const cell = createElement("div", "table-cell");
  const task = primaryTask(row);

  if (!task) {
    cell.append(createElement("span", "muted", "-"));
    return cell;
  }

  cell.append(statusSelect(task));
  return cell;
}

function renderTaskDateCell(row, fieldName, emptyText) {
  const cell = createElement("div", "table-cell");
  const task = primaryTask(row);

  if (!task) {
    cell.append(createElement("span", "muted", "-"));
    return cell;
  }

  const button = createElement(
    "button",
    "date-cell-button",
    task[fieldName] ? formatDate(task[fieldName]) : emptyText,
  );

  button.type = "button";
  button.title = "Click to edit date";
  button.addEventListener("click", () => editTaskDate(task, fieldName));
  cell.append(button);
  return cell;
}

function renderCommentsCell(row) {
  const cell = createElement("div", "table-cell");
  const addButton = createElement("button", "button button-secondary compact-button", "Add comment");

  addButton.type = "button";
  addButton.addEventListener("click", () => createComment(row));

  if (!row.comments?.length) {
    cell.append(createElement("span", "muted", "No comments"), addButton);
    return cell;
  }

  row.comments.slice(0, 2).forEach((comment) => {
    const wrapper = createElement("div", "task-actions");
    const commentLine = createElement("button", "comment-line", comment.content);
    const actions = createElement("div", "mini-actions");
    const deleteButton = createElement("button", "button button-secondary", "Delete");

    commentLine.type = "button";
    commentLine.title = "Click to edit comment";
    commentLine.addEventListener("click", () => editComment(comment));
    deleteButton.type = "button";
    deleteButton.addEventListener("click", () => deleteComment(comment));
    actions.append(deleteButton);
    wrapper.append(commentLine, actions);
    cell.append(wrapper);
  });

  cell.append(addButton);
  return cell;
}

function renderRowActions(row) {
  const cell = createElement("div", "table-cell");
  const task = primaryTask(row);
  const editTaskButton = createElement(
    "button",
    "button button-secondary",
    task ? "Edit" : "Create task",
  );
  const addCommentButton = createElement("button", "button button-secondary", "Comment");
  const deleteButton = createElement("button", "button button-secondary", "Delete row");

  editTaskButton.type = "button";
  addCommentButton.type = "button";
  deleteButton.type = "button";

  editTaskButton.addEventListener("click", () => (task ? editTask(task) : createTask(row)));
  addCommentButton.addEventListener("click", () => createComment(row));
  deleteButton.addEventListener("click", () => deleteRow(row));

  cell.append(editTaskButton, addCommentButton, deleteButton);
  return cell;
}

function renderEvents() {
  empty(eventsList);

  if (state.events.length === 0) {
    eventsList.append(createElement("p", "muted", "No events yet."));
    return;
  }

  state.events.forEach((event) => {
    const item = createElement("article", "list-item");
    const editButton = createElement("button", "button button-secondary", "Edit");
    const deleteButton = createElement("button", "button button-secondary", "Delete");
    const actions = createElement("div", "list-item-actions");

    editButton.type = "button";
    deleteButton.type = "button";
    editButton.addEventListener("click", () => editEvent(event));
    deleteButton.addEventListener("click", () => deleteEvent(event));
    actions.append(editButton, deleteButton);

    item.append(
      createElement("strong", "", event.title ?? "Untitled event"),
      createElement("span", "muted", `${formatDate(event.starting_from)} - ${formatDate(event.deadline)}`),
      createElement("p", "muted", event.description || "No description"),
      actions,
    );
    eventsList.append(item);
  });
}

function renderPermissions() {
  empty(permissionsList);

  if (state.permissions.length === 0) {
    permissionsList.append(createElement("p", "muted", "No permissions yet."));
    return;
  }

  state.permissions.forEach((permission) => {
    const item = createElement("article", "list-item");
    const roleSelect = document.createElement("select");
    const removeButton = createElement("button", "button button-secondary", "Remove");

    ["viewer", "editor", "owner"].forEach((role) => {
      const option = document.createElement("option");
      option.value = role;
      option.textContent = role;
      option.selected = role === permission.user_role_in_board;
      roleSelect.append(option);
    });

    roleSelect.addEventListener("change", () => updatePermission(permission, roleSelect.value));
    removeButton.type = "button";
    removeButton.addEventListener("click", () => removePermission(permission));

    item.append(
      createElement("strong", "", formatUser(permission.user)),
      createElement("span", "muted", permission.user.email_address),
      roleSelect,
      removeButton,
    );
    permissionsList.append(item);
  });
}

function statusPill(status) {
  const classes = {
    completed: "status-done",
    accepted: "status-working",
    pending: "status-stuck",
  };
  return createElement("span", `status-pill ${classes[status] ?? "status-neutral"}`, status);
}

function statusSelect(task) {
  const select = document.createElement("select");
  select.className = "status-select";
  select.title = `Update ${task.task_name} status`;

  [
    ["pending", "Pending"],
    ["accepted", "Accepted"],
    ["completed", "Completed"],
  ].forEach(([value, label]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    option.selected = value === task.task_status;
    select.append(option);
  });

  select.addEventListener("change", () => updateTaskStatus(task, select.value));
  return select;
}

async function deleteColumn(column) {
  try {
    await boardApi.deleteColumn(column.id);
    await loadBoard(state.board.id);
    setFeedback(feedback, "Column deleted.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function createTask(row) {
  const column = await ensureTaskColumn();
  const assignedToId = getDefaultAssigneeId();

  if (!column || !assignedToId) {
    setFeedback(feedback, "Unable to resolve default task metadata.", "error");
    return;
  }

  const taskName = window.prompt("Task name", "New task");

  if (!taskName) {
    return;
  }

  try {
    await boardApi.createTask({
      board_row_id: row.id,
      board_column_id: column.id,
      task_name: taskName,
      task_content: "",
      task_status: "pending",
      starting_from: today(),
      deadline: today(),
      assigned_to_id: assignedToId,
    });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Task created.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function deleteTask(task) {
  try {
    await boardApi.deleteTask(task.id);
    await loadBoard(state.board.id);
    setFeedback(feedback, "Task deleted.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

function primaryTask(row) {
  return row.tasks?.[0] ?? null;
}

function getVisibleColumns() {
  const fallbackColumns = [
    { name: "TaskName", type: "TEXT", position: 0 },
    { name: "TaskContent", type: "LONG_TEXT", position: 1 },
    { name: "TaskStatus", type: "STATUS", position: 2 },
  ];
  const columns = state.columns.length > 0 ? state.columns : fallbackColumns;
  const displayableColumns = columns.filter((column) => column.name !== "TaskID" && column.name !== "Files");
  const baseNames = ["TaskName", "TaskContent", "TaskStatus"];
  const withBaseColumns = [
    ...baseNames
      .filter((name) => !displayableColumns.some((column) => column.name === name))
      .map((name, index) => fallbackColumns[index]),
    ...displayableColumns,
  ];

  return withBaseColumns.sort((left, right) => left.position - right.position);
}

function columnLabel(name) {
  const labels = {
    TaskID: "Task ID",
    TaskName: "Task name",
    TaskContent: "Content",
    TaskStatus: "Status",
    Comment: "Comments",
    StartingFrom: "Start date",
    Deadline: "Deadline",
    Files: "Files",
  };

  return labels[name] ?? name;
}

function isCoreColumn(name) {
  return ["TaskName", "TaskContent", "TaskStatus"].includes(name);
}

function renderColumnWidthControl(columnName) {
  const wrapper = createElement("label", "column-width-control");
  const value = createElement("span", "", `${getColumnWidth(columnName)}px`);
  const range = document.createElement("input");
  const [min, max] = getWidthLimits(columnName);

  range.type = "range";
  range.min = min;
  range.max = max;
  range.step = "10";
  range.value = getColumnWidth(columnName);
  range.title = `Resize ${columnLabel(columnName)} column`;
  range.addEventListener("input", () => {
    setColumnWidth(columnName, Number(range.value));
    value.textContent = `${getColumnWidth(columnName)}px`;
    renderBoard();
  });

  wrapper.append(createElement("small", "", "Width"), range, value);
  return wrapper;
}

function getTableTemplate(visibleColumns) {
  const widths = [
    getColumnWidth("Row"),
    ...visibleColumns.map((column) => getColumnWidth(column.name)),
    getColumnWidth("Actions"),
  ];

  return {
    columns: widths.map((width) => `${width}px`).join(" "),
    totalWidth: widths.reduce((total, width) => total + width, 0),
  };
}

function applyTableTemplate(rowElement, template) {
  rowElement.style.gridTemplateColumns = template.columns;
  rowElement.style.width = `${template.totalWidth}px`;
  rowElement.style.minWidth = `${template.totalWidth}px`;
}

function getColumnWidth(columnName) {
  const [min, max] = getWidthLimits(columnName);
  const width = columnWidths[columnName] ?? DEFAULT_COLUMN_WIDTHS[columnName] ?? 180;

  return Math.min(Math.max(width, min), max);
}

function setColumnWidth(columnName, width) {
  columnWidths[columnName] = getClampedColumnWidth(columnName, width);
  saveColumnWidths();
}

function getClampedColumnWidth(columnName, width) {
  const [min, max] = getWidthLimits(columnName);

  return Math.min(Math.max(width, min), max);
}

function getWidthLimits(columnName) {
  return WIDTH_LIMITS[columnName] ?? [140, 420];
}

function loadColumnWidths(boardId) {
  try {
    return JSON.parse(localStorage.getItem(columnWidthStorageKey(boardId)) ?? "{}");
  } catch {
    return {};
  }
}

function saveColumnWidths() {
  if (!state.board?.id) {
    return;
  }

  localStorage.setItem(columnWidthStorageKey(state.board.id), JSON.stringify(columnWidths));
}

function columnWidthStorageKey(boardId) {
  return `goatcalendar:board:${boardId}:column-widths`;
}

function readColumnConfig(data) {
  const configuredColumns = {
    Deadline: "DATE",
    Comment: "COMMENT",
    StartingFrom: "DATE",
    TaskName: "TEXT",
    TaskContent: "LONG_TEXT",
    TaskStatus: "STATUS",
  };

  if (data.column_key) {
    const [name, type] = String(data.column_key).split(":");

    if (name && type) {
      return { name, type };
    }
  }

  if (data.name) {
    return {
      name: data.name,
      type: data.type || configuredColumns[data.name] || "TEXT",
    };
  }

  return null;
}

function normalizeColumnPosition(value) {
  if (value === undefined || value === null || value === "") {
    return state.columns.length;
  }

  const position = Number.parseInt(value, 10);
  return Number.isNaN(position) || position < 0 ? state.columns.length : position;
}

function getDefaultAssigneeId() {
  return state.permissions[0]?.user?.id ?? state.board?.created_by_id ?? state.board?.created_by?.id;
}

async function ensureTaskColumn() {
  const taskColumn = state.columns.find((column) => column.name === "TaskName") ?? state.columns[0];

  if (taskColumn) {
    return taskColumn;
  }

  const defaultColumns = [
    ["TaskName", "TEXT"],
    ["TaskContent", "LONG_TEXT"],
    ["TaskStatus", "STATUS"],
  ];
  let createdTaskColumn = null;

  for (const [index, [name, type]] of defaultColumns.entries()) {
    const column = await boardApi.createColumn({
      board_id: state.board.id,
      name,
      type,
      position: index,
    });

    if (name === "TaskName") {
      createdTaskColumn = column;
    }
  }

  state.columns = await boardApi.columns(state.board.id);
  return createdTaskColumn ?? state.columns[0];
}

async function updateTaskStatus(task, taskStatus) {
  try {
    await boardApi.updateTask(task.id, {
      task_status: taskStatus,
      version: task.version,
    });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Task status updated.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function editTask(task) {
  const taskName = window.prompt("Task name", task.task_name);

  if (!taskName) {
    return;
  }

  const taskContent = window.prompt("Task content", task.task_content ?? "");

  if (taskContent === null) {
    return;
  }

  try {
    await boardApi.updateTask(task.id, {
      task_name: taskName,
      task_content: taskContent,
      version: task.version,
    });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Task updated.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function editTaskDate(task, fieldName) {
  const value = window.prompt(columnLabel(fieldName === "deadline" ? "Deadline" : "StartingFrom"), task[fieldName] ?? today());

  if (!value) {
    return;
  }

  try {
    await boardApi.updateTask(task.id, {
      [fieldName]: value,
      version: task.version,
    });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Task date updated.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function createComment(row) {
  const content = window.prompt("Comment", "New comment");

  if (!content) {
    return;
  }

  try {
    await boardApi.createComment({
      board_row_id: row.id,
      content,
    });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Comment created.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function editComment(comment) {
  const content = window.prompt("Comment", comment.content);

  if (!content) {
    return;
  }

  try {
    await boardApi.updateComment(comment.id, { content });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Comment updated.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function deleteComment(comment) {
  try {
    await boardApi.deleteComment(comment.id);
    await loadBoard(state.board.id);
    setFeedback(feedback, "Comment deleted.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function deleteRow(row) {
  try {
    await boardApi.deleteRow(row.id);
    await loadBoard(state.board.id);
    setFeedback(feedback, "Row deleted.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function editEvent(event) {
  const title = window.prompt("Event title", event.title ?? "");

  if (title === null) {
    return;
  }

  try {
    await boardApi.updateEvent(event.id, { title });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Event updated.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function deleteEvent(event) {
  try {
    await boardApi.deleteEvent(event.id);
    await loadBoard(state.board.id);
    setFeedback(feedback, "Event deleted.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function updatePermission(permission, role) {
  try {
    await boardApi.updatePermission(state.board.id, permission.user_id, {
      user_role_in_board: role,
    });
    await loadBoard(state.board.id);
    setFeedback(feedback, "Permission updated.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

async function removePermission(permission) {
  try {
    await boardApi.removePermission(state.board.id, permission.user_id);
    await loadBoard(state.board.id);
    setFeedback(feedback, "Permission removed.", "success");
  } catch (error) {
    setFeedback(feedback, error.message, "error");
  }
}

function today() {
  return new Date().toISOString().slice(0, 10);
}
