from starlette_admin.contrib.sqla import ModelView


class BaseView(ModelView):
    exclude_fields_from_edit = ("created_at",)
    exclude_fields_from_create = ("created_at",)


class UserAuthView(BaseView):
    ...


class UserQuestionnaireView(BaseView):
    ...


class UserLikeView(BaseView):
    ...


class BlackListUserView(BaseView):
    ...


class UserSettingsView(BaseView):
    ...


class MatchView(BaseView):
    ...


class MessageView(BaseView):
    ...
