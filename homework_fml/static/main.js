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
    if (tasks.length === 0) {
        result.html("<span id='no-tasks'>No tasks to show&hellip;</span>");
        $("#main-list").replaceWith(result)
    } else {
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

function do_poll() {
    if (running_import_job_id !== null) {
        $.post("/api/poll-job", {
            csrf_token: csrf_token,
            job_id: running_import_job_id,
            get_tasks_from_ids: true
        }, function (data) {
            if (data.ok && data.finished) {
                tasks.push(...data.result);
                render_tasks();
                import_button.prop("disabled", false);
                running_import_job_id = null;
            } else {
                setTimeout(do_poll, 500);
            }
        });
    }
}

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
                running_import_job_id = data.job_id;
                setTimeout(do_poll, 500);
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