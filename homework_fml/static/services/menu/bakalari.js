function setup_bakalari_view() {
    if ("bakalari" in services_user_data) {
        const d = services_user_data["bakalari"];
        $("#bakalari-name").text(d["name"]);
        for (const task_type of ["homework", "komens", "noticeboard"]) {
            const field = $("#bakalari-" + task_type);
            if (task_type in d["enabled_modules"]) {
                field.prop("disabled", false);
                field.prop("checked", d["enabled_modules"][task_type]);
                $(`label[for='bakalari-${task_type}']`).removeClass("disabled");
            } else {
                field.prop("disabled", true);
                $(`label[for='bakalari-${task_type}']`).addClass("disabled");
            }
        }
        $("#menuitem-bakalari").attr("data-display", "settings");
    } else {
        $("#menuitem-bakalari").attr("data-display", "setup");
    }
}

function bakalari_process_register_response(data) {
    $("#bakalari-send").prop("disabled", false);
    if (data.ok) {
        services_user_data["bakalari"] = data.data;
        setup_bakalari_view();
    } else if (data.reason === "SPECIFIED") {
        alert("Error: " + data.error_info);
    } else {
        if (confirm("An unspecified error occurred. Try again?")) {
            bakalari_process_register_form();
        }
    }
}

function bakalari_process_register_form(e) {
    if (e !== undefined) e.preventDefault();

    $("#bakalari-send").prop("disabled", true);
    $.post("/services/bakalari/register", $("#bakalari-setup form").serialize(), bakalari_process_register_response);
}

function bakalari_process_settings_response(data) {
    $("#bakalari-save-settings").prop("disabled", false);
    if (data.ok) {
        services_user_data["bakalari"] = data.data;
        setup_bakalari_view();
    } else if (confirm("Something went wrong saving the settings. Try again?")) {
        bakalari_process_settings();
    }
}

function bakalari_process_settings(e) {
    if (e !== undefined) e.preventDefault();

    $("#bakalari-save-settings").prop("disabled", true);
    $.post("/services/bakalari/settings", $("#bakalari-settings form").serialize(), bakalari_process_settings_response);
    $("#bakalari-settings form input").prop("disabled", true);
}

function bakalari_confirm_delete() {
    const button = $("#bakalari-delete");
    if (confirm("Are you sure you want to delete this integration?")) {
        button.prop("disabled", true);
        $.post("/services/bakalari/delete", {
            csrf_token: csrf_token,
            delete_tasks: confirm("Do you want to also delete the tasks from this service? This is irreversible!")
        }, function (data) {
            if (data.ok) {
                delete services_user_data["bakalari"];
                setup_bakalari_view();
            } else {
                alert("Something went wrong. Please try again.");
            }
            button.prop("disabled", false);
        })
    }
}

$(() => {
    $("#bakalari-setup form").on("submit", bakalari_process_register_form);
    $("#bakalari-settings form").on("submit", bakalari_process_settings);
    $("#bakalari-delete").on("click", bakalari_confirm_delete)
});