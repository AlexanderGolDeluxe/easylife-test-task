from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette_admin.contrib.sqla import Admin
from starlette_admin.views import Link

from app.configuration.dashboards import __admin_panel__
from app.configuration.db_helper import db_helper
from app.configuration.initial_db_data import insert_all_initial_db_data
from app.configuration.routes import __routes__
from app.core.models import Base
from app.core.views import StatisticsView


class Server:

    def __init__(self, app: FastAPI):
        self.__app = app
        self.__register_routes(app)
        self.__mount_admin_panel(app)

    def get_app(self):
        return self.__app

    @staticmethod
    def __register_routes(app: FastAPI):
        __routes__.register_routers(app)

    @staticmethod
    def __mount_admin_panel(app: FastAPI):
        admin = Admin(
            engine=db_helper.engine,
            title="EasyLife test task",
            index_view=StatisticsView(
                label="Statistics",
                icon="fa fa-chart-line",
                template_path="statistics.html")
        )
        __admin_panel__.register_views(admin)
        admin.add_view(
            Link(label="Go to Swagger", icon="fa fa-link", url="/docs")
        )
        admin.mount_to(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await insert_all_initial_db_data()
    yield
    await db_helper.engine.dispose()
