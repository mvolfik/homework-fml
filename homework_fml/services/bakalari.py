from datetime import datetime, timezone

from bakapi import BakapiUser, InvalidCredentials, InvalidResponse
from flask import Blueprint, jsonify, request
from flask_login import current_user
from requests import RequestException
from sqlalchemy.orm.attributes import flag_modified

from ..db import Task, db
from ..utils import ErrorReason, fail

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def dt(string):
    return datetime.strptime(string, DATETIME_FORMAT)


def process_homework(hw):
    return Task(
        assigned_on=dt(hw["DateStart"]),
        due=dt(hw["DateEnd"]),
        service_name="bakalari",
        full_text=hw["Content"],
        data={
            "type": "homework",
            "internal_id": hw["ID"],
            "subject": {
                "short": hw["Subject"]["Abbrev"],
                "full": hw["Subject"]["Name"],
            },
            "teacher": hw["Teacher"]["Name"],
            "attachments": hw["Attachments"],
            "requires_send": hw["Electronic"],
        },
    )


def process_komens_message(msg):
    sent = dt(msg["SentDate"])
    return Task(
        assigned_on=sent,
        due=sent,
        service_name="bakalari",
        full_text=msg["Text"],
        data={
            "type": "komens",
            "internal_id": msg["Id"],
            "teacher": msg["Sender"]["Name"],
            "attachments": msg["Attachments"],
            "requires_confirmation": msg["CanConfirm"],
        },
    )


def process_notice(msg):
    sent = dt(msg["SentDate"])
    return Task(
        assigned_on=sent,
        due=sent,
        service_name="bakalari",
        full_text="<span class='bakalari-noticeboard-title'>%(Title)s</span>\n%(Text)s"
        % msg,
        data={
            "type": "noticeboard",
            "internal_id": msg["Id"],
            "title": msg["Title"],
            "teacher": msg["Sender"]["Name"],
            "attachments": msg["Attachments"],
            "requires_confirmation": msg["CanConfirm"],
        },
    )


def import_data(db_user):
    data = db_user.services_data.get("bakalari")
    if data is None:  # service not registered for this user
        return []

    known_tasks = [
        (task.data["type"], task.data["internal_id"])
        for task in db_user.tasks
        if task.service_name == "bakalari"
    ]
    old_validity = datetime.fromtimestamp(data["token_valid_until"], tz=timezone.utc)
    bakapi_user = BakapiUser(
        token_valid_until=old_validity,
        **{
            k: v
            for k, v in data.items()
            if k in ("access_token", "refresh_token", "url", "username")
        }
    )
    results = []
    user_info = bakapi_user.get_user_info()

    enabled_modules = data["_frontend"]["enabled_modules"]
    if enabled_modules.get("homework"):
        for hw in bakapi_user.get_homework(
            since=dt(user_info["SettingModules"]["Common"]["ActualSemester"]["From"]),
            to=dt(user_info["SettingModules"]["Common"]["ActualSemester"]["To"]),
        )["Homeworks"]:
            if ("homework", hw["ID"]) not in known_tasks:
                results.append(process_homework(hw))
    if enabled_modules.get("komens"):
        for msg in bakapi_user.get_received_komens_messages()["Messages"]:
            if ("komens", msg["Id"]) not in known_tasks:
                results.append(process_komens_message(msg))
    if enabled_modules.get("noticeboard"):
        for msg in bakapi_user.query_api(
            "api/3/komens/messages/noticeboard", method="POST"
        )["Messages"]:
            if ("noticeboard", msg["Id"]) not in known_tasks:
                results.append(process_notice(msg))

    if old_validity != bakapi_user.token_valid_until:
        db_user.services_data["bakalari"].update(vars(bakapi_user))
        flag_modified(db_user, "services_data")
    return results


bp = Blueprint("services.bakalari", __name__, url_prefix="/services/bakalari")


@bp.route("/register", methods=("POST",))
def register():
    if current_user is None:
        return fail(ErrorReason.UNAUTHORIZED)

    if current_user.services_data.get("bakalari") is not None:
        return fail("This service is already initialized for this user")

    data = request.form
    try:
        baka_user = BakapiUser(
            url=data["url"], username=data["username"], password=data["password"]
        )
    except InvalidCredentials:
        return fail("Bakaláři username or password invalid")
    except (RequestException, InvalidResponse):
        return fail("Invalid Bakaláři server URL")

    service_data = current_user.services_data["bakalari"] = vars(baka_user)

    user_info = baka_user.get_user_info()

    frontend_data = service_data["_frontend"] = {}
    frontend_data["name"] = user_info["FullName"]
    modules = frontend_data["enabled_modules"] = {}

    for module in user_info["EnabledModules"]:
        if module["Module"] == "Komens":
            if "ShowReceivedMessages" in module["Rights"]:
                modules["komens"] = False
            if "ShowNoticeBoardMessages" in module["Rights"]:
                modules["noticeboard"] = False
        elif module["Module"] == "Homeworks" and "ShowHomeworks" in module["Rights"]:
            modules["homework"] = True

    current_user.services_data["bakalari"] = service_data
    flag_modified(current_user, "services_data")
    db.session.commit()
    return jsonify({"ok": True, "data": frontend_data})


@bp.route("/settings", methods=("POST",))
def settings():
    if current_user is None:
        return fail(ErrorReason.UNAUTHORIZED)

    if current_user.services_data.get("bakalari") is None:
        return fail("This service is not initialized for this user")

    frontend_data = current_user.services_data["bakalari"]["_frontend"]
    data = {k: request.form.get(k) == "on" for k in frontend_data["enabled_modules"]}
    frontend_data["enabled_modules"] = data
    flag_modified(current_user, "services_data")
    db.session.commit()
    return jsonify({"ok": True, "data": frontend_data})


@bp.route("/delete", methods=("POST",))
def delete():
    if current_user is None:
        return fail(ErrorReason.UNAUTHORIZED)

    del current_user.services_data["bakalari"]
    flag_modified(current_user, "services_data")

    if request.form["delete_tasks"] == "true":
        Task.query.filter_by(user_id=current_user.id, service_name="bakalari").delete()
    db.session.commit()
    return jsonify({"ok": True})
