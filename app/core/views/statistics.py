from loguru import logger
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView

from app.core.crud.user_transaction import get_all_transactions_for_view


class StatisticsView(CustomView):

    @logger.catch(reraise=True)
    async def render(self, request: Request, templates: Jinja2Templates):
        user_transactions = await get_all_transactions_for_view(
            request.state.session,
            request.query_params.get("transactions_creation_date"))

        return templates.TemplateResponse(
            "statistics.html",
            dict(request=request, user_transactions=user_transactions))
