function render_bakalari_task(task) {
    // no rendering yet
    return fallback_renderer(task);
}

service_task_renderers["bakalari"] = render_bakalari_task;