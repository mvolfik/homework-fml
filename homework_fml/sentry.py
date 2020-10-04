import os

dsn = os.environ.get("SENTRY_DSN", None)
if dsn is not None:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from flask_login import current_user
    from flask import request

    def add_user_info(event, hint):
        try:
            user_info = event.setdefault("user", {})
            if current_user.is_authenticated:
                user_info["id"] = current_user.id
                user_info["email"] = current_user.email
            else:
                user_info["ip_address"] = request.remote_addr
        except Exception:  # noqa
            pass
        return event

    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=float(os.environ.get("SENTRY_SAMPLE_RATE", "1.0")),
        before_send=add_user_info,
    )
