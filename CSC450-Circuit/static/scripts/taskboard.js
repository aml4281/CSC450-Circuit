"use strict";

const variables = document.getElementById("variables");

const projectId   = variables.dataset.projectId;
const tasks   = JSON.parse(variables.dataset.tasks);

const statuses = {};
statuses['todo'] = 'To Do';
statuses['designing'] = 'Designing';
statuses['inProgress'] = 'In Progress';
statuses['testing'] = 'Testing';
statuses['done'] = 'Done';

let columns = document.querySelectorAll(".task_list");

// Build the taskboard
tasks.forEach(task => {
    // Create new element format
    let taskItem = document.createElement("li");
    let anchor = document.createElement("a");
    anchor.href = "#";
    anchor.textContent = task["task_title"];
    anchor.classList.add("taskModal")
    anchor.setAttribute("data-bs-toggle", "modal");
    anchor.setAttribute("data-bs-target", "#taskModal");
    anchor.setAttribute("id", task["task_id"]);
    anchor.setAttribute("data-description", task["task_description"]);
    anchor.setAttribute("data-status", task["task_status"]);
    taskItem.appendChild(anchor);

    // Add task to the correct column
    columns.forEach(column => {
        if (column.id === task["task_status"] + "_list") {
            column.appendChild(taskItem);
        }
    });
});

// Create modal format
let createModal = (taskId, taskTitle, taskDescription, taskStatus) => {
    const modal = document.createElement("div");
    modal.classList.add("modal", "fade");
    modal.id = `taskModal-${taskId}`;
    modal.tabIndex = -1;
    modal.setAttribute("aria-labelledby", `taskModalLabel-${taskId}`);
    modal.setAttribute("aria-hidden", "true");

    let taskAssignees = () => {
        let taskAssigneeList = [];
        for (let i = 0; i < tasks.length; i++) {
            if (tasks[i]["task_id"] == taskId) {
                taskAssigneeList = tasks[i]["assigned_members"];
            }
        }
        return taskAssigneeList;
    };

    let assignedMemberString = "";
    taskAssignees().forEach(assignee => {
        assignedMemberString += "<li>" + assignee + "</li>";
    });

    // Modal content
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="taskModalLabel-${taskId}">${taskTitle}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>${taskDescription}</p>
                    <h5>Assignees</h5>
                    <ul>
                        ${assignedMemberString}
                    </ul>
                    <p><strong>Status:</strong> ${statuses[taskStatus]}</p>
                    <h5>Change Status</h5>
                    <form action="change_status" method="POST">
                        <input type="hidden" name="project_id" value="${projectId}">
                        <input type="hidden" name="task_id" value="${taskId}">
                        <select name="task_status" class="form-select">
                            <option value="todo" ${taskStatus === "todo" ? "selected" : ""}>To Do</option>
                            <option value="designing" ${taskStatus === "designing" ? "selected" : ""}>Designing</option>
                            <option value="inProgress" ${taskStatus === "inProgress" ? "selected" : ""}>In Progress</option>
                            <option value="testing" ${taskStatus === "testing" ? "selected" : ""}>Testing</option>
                            <option value="done" ${taskStatus === "done" ? "selected" : ""}>Done</option>
                        </select>
                        <button type="submit" id="change_status_btn" class="btn btn-primary">Change Status</button>
                    </form>
                    <form action="delete_task" method="POST">
                        <input type="hidden" name="project_id" value="${projectId}">
                        <input type="hidden" name="task_id" value="${taskId}">
                        <button type="submit" id="delete_task_btn" class="btn btn-danger">Delete Task</button>
                    </form>
                
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    return modal;
};

// Add event listeners to task items
// This will create a modal when a task is clicked
let taskItems = document.querySelectorAll(".taskModal");
taskItems.forEach(taskItem => {
    taskItem.addEventListener("click", () => {
        document.querySelector("body").appendChild(createModal(taskItem.id, taskItem.textContent, taskItem.dataset.description, taskItem.dataset.status));
        let modalStructure = document.getElementById(`taskModal-${taskItem.id}`);
        let modal = new bootstrap.Modal(modalStructure);
        modal.show();
    });
});