from dataclasses import dataclass

from starlette_admin.contrib.sqla import Admin, ModelView


@dataclass(frozen=True)
class AdminPanel:
    model_views: dict

    def register_views(self, panel: Admin):
        for icon, model in self.model_views.items():
            panel.add_view(ModelView(model, icon))
