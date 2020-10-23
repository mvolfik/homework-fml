// region renderer

function render_manual_task(task) {
    // no rendering yet
    return fallback_renderer(task);
}

service_task_renderers["manual"] = render_manual_task;

// endregion

let manual_task_modal_cross;
let manual_task_modal_wrapper;
let manual_task_add_button;

let manual_task_title_input;
let manual_task_date_input;
let manual_task_time_input;
let manual_task_description_input;

// region validators

function manual_task_validate_title() {
    if (manual_task_title_input.val() === "") {
        manual_task_title_input[0].setCustomValidity("Please enter title");
        return false;
    } else {
        manual_task_title_input[0].setCustomValidity("");
        return true;
    }
}

function manual_task_validate_date() {
    if (manual_task_date_input.val() === "") {
        manual_task_date_input[0].setCustomValidity("Please enter date");
        return false;
    } else {
        manual_task_date_input[0].setCustomValidity("");
        return true;
    }
}

function manual_task_validate_time() {
    if (manual_task_time_input.val() === "") {
        manual_task_time_input[0].setCustomValidity("Please enter time");
        return false;
    } else {
        manual_task_time_input[0].setCustomValidity("");
        return true;
    }
}

function manual_task_validate_description() {
    if (manual_task_description_input.val() === "") {
        manual_task_description_input[0].setCustomValidity("Please enter description");
        return false;
    } else {
        manual_task_description_input[0].setCustomValidity("");
        return true;
    }
}

// endregion
// region send new manual task

function process_new_manual_task_response(data) {
    if (data.ok) {
        manual_task_modal_wrapper.hide();
        alert("Task added successfully");
        tasks.push(data.result);
        render_tasks();
        manual_task_modal_wrapper.hide();
    } else {
        if (data.reason === "DUE_IN_PAST") {
            alert("The due date and time can't be in the past!");
        } else {
            alert("Something went wrong, please try again")
        }
        manual_task_modal_cross.show();
    }
    manual_task_add_button.prop("disabled", false);
}

function send_new_manual_task(e) {

    e.preventDefault();

    if (!manual_task_validate_title()) {
        return
    }
    if (!manual_task_validate_date()) {
        return
    }
    if (!manual_task_validate_time()) {
        return
    }
    if (!manual_task_validate_description()) {
        return
    }

    // check that datetime is in the future
    const datetime = new Date(manual_task_date_input.val() + " " + manual_task_time_input.val());
    if (datetime <= (new Date())) {
        manual_task_date_input[0].setCustomValidity("The due date and time can't be in the past");
        return;
    }
    manual_task_add_button.prop("disabled", true);
    manual_task_modal_cross.hide();
    $.post("/services/manual/add-manual-task", {
        csrf_token: csrf_token,
        title: manual_task_title_input.val(),
        description: manual_task_description_input.val(),
        due_timestamp: datetime.getTime() / 1000
    }, process_new_manual_task_response)
}

// endregion
// region show add manual task

function prepare_manual_task_modal() {
    manual_task_title_input.val("");
    let tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    // bruh, js dates are the weirdest thing I've ever seen
    manual_task_date_input.val(`${tomorrow.getFullYear()}-${(tomorrow.getMonth() + 1).toString().padStart(2, "0")}-${tomorrow.getDate().toString().padStart(2, "0")}`);
    manual_task_time_input.val("23:59");
    manual_task_description_input.val("");
}

function show_add_manual_task() {
    prepare_manual_task_modal();
    manual_task_modal_cross.show();
    manual_task_modal_wrapper.show();
    manual_task_title_input.focus();
}

// endregion
// region setup

$(function () {

    $("body").append('<div class="modal-wrapper" id="manual-task-modal-wrapper"><div>' +
        '<span class="modal-close" id="manual-task-modal-close">&times;</span>' +
        '<form>' +
        '<label for="manual-task-title">Title</label><input type="text" name="title" id="manual-task-title"/>' +
        '<label for="manual-task-due-date">Due</label><input type="date" name="due-date" id="manual-task-due-date" required="required"/><label for="manual-task-due-time">at</label><input type="time" name="due-time" id="manual-task-due-time" required="required" value="23:59"/>' +
        '<label for="manual-task-description">Description</label><textarea name="description" id="manual-task-description"></textarea>' +
        '<button id="manual-task-add" type="submit">Add task</button>' +
        '</form></div></div>');
    manual_task_modal_cross = $("#manual-task-modal-close");
    manual_task_modal_wrapper = $("#manual-task-modal-wrapper");
    manual_task_add_button = $("#manual-task-add");
    manual_task_add_button.on("click", send_new_manual_task);

    manual_task_title_input = $("#manual-task-title");
    manual_task_title_input.on("input", manual_task_validate_title);
    manual_task_date_input = $("#manual-task-due-date");
    manual_task_date_input.on("input", manual_task_validate_date);
    manual_task_time_input = $("#manual-task-due-time");
    manual_task_time_input.on("input", manual_task_validate_time);
    manual_task_description_input = $("#manual-task-description");
    manual_task_description_input.on("input", manual_task_validate_description);

    manual_task_modal_wrapper.hide();
    manual_task_modal_cross.on("click", function () {
        manual_task_modal_wrapper.hide();
    });
    $(window).on("click", function (e) {
        if (manual_task_modal_wrapper.is(e.target) && !manual_task_modal_cross.is(":hidden")) {
            manual_task_modal_wrapper.hide();
        }
    });


    $("main").prepend('<button onclick="show_add_manual_task()">Add task</button>');
});

// endregion