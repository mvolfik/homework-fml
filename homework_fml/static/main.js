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

let import_button;
let running_import_job_id = null;

function request_import() {
    import_button.prop("disabled", true);
    $.post("/api/request-import", {csrf_token: csrf_token}, function (data) {
            if (!data.ok) {
                if (confirm("Something went wrong. Try again?")) {
                    request_import();
                } else {
                    import_button.prop("disabled", false);
                }
            } else {
                alert("Import is running");
                running_import_job_id = data.job_id;
                import_button.prop("disabled", false);
            }
        }
    )
}

$(function () {
    main_list = $("#main-list");
    import_button = $("#request-import");
    import_button.on("click", request_import);
    load_tasks();
});