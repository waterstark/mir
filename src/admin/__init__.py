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

from src.admin.auth_provider import EmailAndPasswordProvider
from src.admin.utils import get_password_hash
from src.admin.views import (
    BlackListUserView, MatchView, UserAuthView,
    UserQuestionnaireView, UserSettingsView,
)
from src.auth.models import AuthUser, UserSettings
from src.config import SECRET_AUTH
from src.database import engine
from src.posts.models import Match
from src.questionnaire.models import BlackListUser, UserQuestionnaire


class CustomAdmin(Admin):
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
        form = await request.form()
        dict_obj = await self.form_to_dict(
            request, form, model, RequestAction.CREATE,
        )
        if "hashed_password" in dict_obj:
            password = dict_obj.pop("hashed_password")
            dict_obj["hashed_password"] = get_password_hash(password)
        try:
            obj = await model.create(request, dict_obj)
        except FormValidationError as exc:
            return self.templates.TemplateResponse(
                model.create_template,
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
                model.create_template,
                {
                    "request": request,
                    "model": model,
                    "errors": {
                        "email": (
                                    "Пользователь с такими "
                                    "данными уже существует"
                                ),
                    },
                    "obj": dict_obj,
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        pk = getattr(obj, model.pk_attr)
        url = request.url_for(
            self.route_name + ":list", identity=model.identity,
        )
        if form.get("_continue_editing", None) is not None:
            url = request.url_for(
                self.route_name + ":edit", identity=model.identity, pk=pk,
            )
        elif form.get("_add_another", None) is not None:
            url = request.url
        return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)

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
                        obj, request, RequestAction.EDIT,
                    ),
                },
            )
        form = await request.form()
        dict_obj = await self.form_to_dict(
            request, form, model, RequestAction.EDIT,
        )
        if "hashed_password" in dict_obj:
            password = dict_obj.pop("hashed_password")
            dict_obj["hashed_password"] = get_password_hash(password)
        try:
            obj = await model.edit(request, pk, dict_obj)
        except FormValidationError as exc:
            return self.templates.TemplateResponse(
                model.edit_template,
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
                model.create_template,
                {
                    "request": request,
                    "model": model,
                    "errors": {
                        "email": "Пользователь с такими данными уже существует",
                    },
                    "obj": dict_obj,
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        pk = getattr(obj, model.pk_attr)
        url = request.url_for(
            self.route_name + ":list", identity=model.identity,
        )
        if form.get("_continue_editing", None) is not None:
            url = request.url_for(
                self.route_name + ":edit", identity=model.identity, pk=pk,
            )
        elif form.get("_add_another", None) is not None:
            url = request.url_for(
                self.route_name + ":create", identity=model.identity,
            )
        return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)


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
    middlewares=[Middleware(SessionMiddleware, secret_key=SECRET_AUTH)],
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
            MatchView(
                Match,
                label="Совпадения",
            ),
            # UserLikeView(
            #     UserLike,
            #     label="Лайки"
            # )
        ],
    ),
)
