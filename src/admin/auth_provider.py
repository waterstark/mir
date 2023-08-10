from sqlalchemy import select
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.templating import Jinja2Templates
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.base import BaseAdmin
from starlette_admin.exceptions import FormValidationError, LoginFailed

from src.admin.utils import verify_password
from src.auth.models import AuthUser
from src.database import async_session_maker

templates = Jinja2Templates(directory="templates")


class EmailAndPasswordProvider(AuthProvider):
    async def login(
        self,
        email: str,
        password: str,
        request: Request,
        response: Response,
    ) -> Response:
        async with async_session_maker() as session:
            query = select(AuthUser).filter_by(email=email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
        if user:
            hashed_password = user.hashed_password
            if verify_password(password, hashed_password):
                request.session.update({"email": email})
                return response
        raise LoginFailed("Invalid email or password")

    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("email", None) is not None:
            request.state.user = request.session.get("email")
            return True
        return False

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        photo_url = request.url_for("static", path="img/admin.png")
        return AdminUser(username=user, photo_url=photo_url)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    async def render_login(
        self,
        request: Request,
        admin: BaseAdmin,
    ) -> Response:
        if request.method == "GET":
            return templates.TemplateResponse(
                name="admin_login.html",
                context={"request": request, "_is_login_path": True},
            )
        form = await request.form()
        try:
            return await self.login(
                form.get("email"),
                form.get("password"),
                request,
                RedirectResponse(
                    request.query_params.get("next")
                    or request.url_for(admin.route_name + ":index"),
                    status_code=status.HTTP_303_SEE_OTHER,
                ),
            )
        except FormValidationError as errors:
            return templates.TemplateResponse(
                "admin_login.html",
                {
                    "request": request,
                    "form_errors": errors,
                    "_is_login_path": True,
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except LoginFailed as error:
            return templates.TemplateResponse(
                "admin_login.html",
                {
                    "request": request,
                    "form_errors": error.msg,
                    "_is_login_path": True,
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
