from app.configuration.routes.routes import Routes
from app.core.routes import auth, base, user, user_transaction

__routes__ = Routes(
    routers=(
        auth.router, base.router, user_transaction.router, user.router))
