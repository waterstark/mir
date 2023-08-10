from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_admin import DropDown, I18nConfig
from starlette_admin._types import RequestAction
from starlette_admin.contrib.sqla import Admin
from starlette_admin.exceptions import FormValidationError
from starlette_admin.views import BaseModelView

from src.admin.auth_provider import EmailAndPasswordProvider
from src.admin.utils import get_password_hash
from src.admin.views import (
    BlackListUserView,
    MessageView,
    UserAuthView,
    UserLikeView,
    UserQuestionnaireView,
    UserSettingsView,
)
from src.auth.models import AuthUser, UserSettings
from src.config import settings
from src.database import engine
from src.likes.models import UserLike
from src.posts.models import Message
from src.questionnaire.models import BlackListUser, UserQuestionnaire


class CustomAdmin(Admin):
    async def render_form_response(
        self,
        request: Request,
        model: BaseModelView,
        action: RequestAction,
    ):
        action_template = (
            model.create_template
            if action == RequestAction.CREATE
            else model.edit_template
        )
        form = await request.form()
        dict_obj = await self.form_to_dict(
            request,
            form,
            model,
            action,
        )

        if "hashed_password" in dict_obj:
            password = dict_obj.pop("hashed_password")
            dict_obj["hashed_password"] = get_password_hash(password)

        try:
            if action == RequestAction.CREATE:
                obj = await model.create(request, dict_obj)
            else:
                pk = request.path_params.get("pk")
                obj = await model.edit(request, pk, dict_obj)
        except FormValidationError as exc:
            return self.templates.TemplateResponse(
                action_template,
                {
                    "request": request,
                    "model": model,
                    "errors": exc.errors,
                    "obj": dict_obj,
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except IntegrityError:
            return self.templates.TemplateResponse(
                action_template,
                {
                    "request": request,
                    "model": model,
                    "errors": {
                        "email": ("Пользователь c такими данными уже существует"),
                    },
                    "obj": dict_obj,
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        pk = getattr(obj, model.pk_attr)
        url = request.url_for(
            self.route_name + ":list",
            identity=model.identity,
        )

        if form.get("_continue_editing", None) is not None:
            url = request.url_for(
                self.route_name + ":edit",
                identity=model.identity,
                pk=pk,
            )
        elif form.get("_add_another", None) is not None:
            if action == RequestAction.CREATE:
                url = request.url
            else:
                url = request.url_for(
                    self.route_name + ":create",
                    identity=model.identity,
                )
        return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)

    async def _render_create(self, request: Request) -> Response:
        request.state.action = RequestAction.CREATE
        identity = request.path_params.get("identity")
        model = self._find_model_from_identity(identity)

        if not model.is_accessible(request) or not model.can_create(request):
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        if request.method == "GET":
            return self.templates.TemplateResponse(
                model.create_template,
                {"request": request, "model": model},
            )

        return await self.render_form_response(request, model, RequestAction.CREATE)

    async def _render_edit(self, request: Request) -> Response:
        request.state.action = RequestAction.EDIT
        identity = request.path_params.get("identity")
        model = self._find_model_from_identity(identity)

        if not model.is_accessible(request) or not model.can_edit(request):
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        pk = request.path_params.get("pk")
        obj = await model.find_by_pk(request, pk)

        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            return self.templates.TemplateResponse(
                model.edit_template,
                {
                    "request": request,
                    "model": model,
                    "raw_obj": obj,
                    "obj": await model.serialize(
                        obj,
                        request,
                        RequestAction.EDIT,
                    ),
                },
            )

        return await self.render_form_response(request, model, RequestAction.EDIT)


admin = CustomAdmin(
    engine,
    title="Socnet App",
    base_url="/admin",
    statics_dir="static",
    i18n_config=I18nConfig(default_locale="ru"),
    logo_url="http://127.0.0.1:8000/static/img/logo.png",  # Доработаю
    auth_provider=EmailAndPasswordProvider(
        allow_paths=["/statics/img/logo.png"],
    ),
    middlewares=[Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)],
)


admin.add_view(
    DropDown(
        "Пользователи",
        icon="fa-solid fa-users",
        views=[
            UserAuthView(
                AuthUser,
                label="Аутентификация",
            ),
            UserSettingsView(
                UserSettings,
                label="Настройки пользователя",
            ),
        ],
    ),
)
admin.add_view(
    DropDown(
        "Анкеты",
        icon="fa-solid fa-file-pen",
        views=[
            UserQuestionnaireView(
                UserQuestionnaire,
                label="Анкета пользователя",
            ),
            BlackListUserView(
                BlackListUser,
                label="Чёрный список",
            ),
        ],
    ),
)
admin.add_view(
    DropDown(
        "Взаимодействия",
        icon="fa-solid fa-heart",
        views=[
            MessageView(
                Message,
                label="Сообщения",
            ),
            UserLikeView(
                UserLike,
                label="Лайки",
            ),
        ],
    ),
)
