from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..db import Task, db
from ..utils import ErrorReason, fail


def import_data(_):
    pass  # no importing is actually done for manual tasks


bp = Blueprint("services.manual", __name__, url_prefix="/services/manual")


@bp.route("/add-manual-task", methods=("POST",))
def add_manual_task():
    if not current_user.is_authenticated:
        return fail(ErrorReason.UNAUTHORIZED)

    data = request.form
    due = datetime.fromtimestamp(int(data["due_timestamp"]), tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    if due <= now:
        return fail(ErrorReason.DUE_IN_PAST)

    t = Task(
        assigned_on=now,
        due=due,
        full_text=data["title"] + ":\n" + data["description"],
        service_name="manual",
        data={"title": data["title"]},
    )
    current_user.tasks.append(t)
    db.session.commit()
    return jsonify({"ok": True, "result": t})
