import os

from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration

dsn = os.environ.get("SENTRY_DSN", None)
if dsn is not None:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            RqIntegration(),
        ],
        traces_sample_rate=float(os.environ.get("SENTRY_SAMPLE_RATE", "1.0")),
        environment=os.environ.get("SENTRY_ENVIRON", "unknown"),
    )
