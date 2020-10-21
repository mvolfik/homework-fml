const service_task_renderers = {};

let main_list;
let tasks = [];

function fallback_renderer(task) {
    const text_node = document.createTextNode(JSON.stringify(task, null, 2));
    const p = document.createElement("p");
    p.style.fontFamily = "monospace";
    p.style.whiteSpace = "pre-wrap";
    p.appendChild(text_node);
    return p;
}

function render_tasks() {
    let result = $(document.createElement("div"));
    result.prop("id", "main-list");
    for (const task of tasks) {
        const renderer = service_task_renderers[task["service_name"]];
        if (renderer !== undefined) {
            result.append(renderer(task));
        } else {
            result.append(fallback_renderer(task));
        }

    }
    $("#main-list").replaceWith(result);
}

function load_tasks() {
    $.get("/api/get-tasks", function (data) {
        if (!data.ok) {
            if (confirm("Tasks loading failed. Try again?")) {
                load_tasks();
            }
        } else {
            tasks = data.tasks;
            render_tasks();
        }
    });
}

$(function () {
    main_list = $("#main-list");
    load_tasks();
});