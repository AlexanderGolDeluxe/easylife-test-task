from app.configuration.dashboards.admin_panel import AdminPanel
from app.core.models import (
    RolePermission, TransactionType, User, UserTransaction)

__admin_panel__ = AdminPanel(
    model_views={
        "fa fa-user-lock": RolePermission,
        "fa fa-arrows-turn-right": TransactionType,
        "fa fa-users": User,
        "fa fa-arrows-turn-to-dots": UserTransaction})
