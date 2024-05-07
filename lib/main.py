"""Example with which we test UI elements with L10N support."""

import os
import random
import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, responses, Header, Request, Depends
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

from nc_py_api import NextcloudApp
from nc_py_api.ex_app import (
    run_app,
    set_handlers,
    AppAPIAuthMiddleware,
    SettingsField,
    SettingsFieldType,
    SettingsForm,
    UiActionFileInfo,
    nc_app
)
from contextvars import ContextVar

from gettext import translation

LOCALE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale")
current_translator = ContextVar("current_translator")
current_translator.set(translation(os.getenv("APP_ID"), LOCALE_DIR, languages=["en"], fallback=True))


def _(text):
    return current_translator.get().gettext(text)


print(_("UI example"))


class LocalizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_lang = request.headers.get('Accept-Language', 'en')
        print(f"DEBUG: lang={request_lang}")
        translator = translation(
            os.getenv("APP_ID"), LOCALE_DIR, languages=[request_lang], fallback=True
        )
        current_translator.set(translator)
        print(_("UI example"))
        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_handlers(app, enabled_handler)
    print(_("UI example"))
    yield


APP = FastAPI(lifespan=lifespan)
APP.add_middleware(AppAPIAuthMiddleware)
APP.add_middleware(LocalizationMiddleware)

SETTINGS_EXAMPLE = SettingsForm(
    id="settings_example",
    section_type="admin",
    section_id="ai_integration_team",
    title=_("Example of declarative settings"),
    description=_("These fields are rendered dynamically from declarative schema"),
    fields=[
        SettingsField(
            id="field1",
            title="Multi-selection",
            description=_("Select some option setting"),
            type=SettingsFieldType.MULTI_SELECT,
            default=["foo", "bar"],
            placeholder=_("Select some multiple options"),
            options=["foo", "bar", "baz"],
        ),
        SettingsField(
            id="some_real_setting",
            title=_("Choose init status check background job interval"),
            description=_("How often ExApp should check for initialization status"),
            type=SettingsFieldType.RADIO,
            default="40m",
            placeholder=_("Choose init status check background job interval"),
            options={
                _("Each 40 minutes"): "40m",
                _("Each 60 minutes"): "60m",
                _("Each 120 minutes"): "120m",
                _("Each day"): f"{60 * 24}m",
            },
        ),
        SettingsField(
            id="test_ex_app_field_1",
            title=_("Default text field"),
            description=_("Set some simple text setting"),
            type=SettingsFieldType.TEXT,
            default="foo",
            placeholder=_("Enter text setting"),
        ),
        SettingsField(
            id="test_ex_app_field_1_1",
            title=_("Email field"),
            description=_("Set email config"),
            type=SettingsFieldType.EMAIL,
            default="",
            placeholder=_("Enter email"),
        ),
        SettingsField(
            id="test_ex_app_field_1_2",
            title=_("Tel field"),
            description=_("Set tel config"),
            type=SettingsFieldType.TEL,
            default="",
            placeholder=_("Enter your tel"),
        ),
        SettingsField(
            id="test_ex_app_field_1_3",
            title=_("Url (website) field"),
            description=_("Set url config"),
            type=SettingsFieldType.URL,
            default="",
            placeholder=_("Enter url"),
        ),
        SettingsField(
            id="test_ex_app_field_1_4",
            title=_("Number field"),
            description=_("Set number config"),
            type=SettingsFieldType.NUMBER,
            default=0,
            placeholder=_("Enter number value"),
        ),
        SettingsField(
            id="test_ex_app_field_2",
            title=_("Password"),
            description=_("Set some secure value setting"),
            type=SettingsFieldType.PASSWORD,
            default="",
            placeholder=_("Set secure value"),
        ),
        SettingsField(
            id="test_ex_app_field_3",
            title=_("Selection"),
            description=_("Select some option setting"),
            type=SettingsFieldType.SELECT,
            default="foo",
            placeholder=_("Select some option setting"),
            options=["foo", "bar", "baz"],
        ),
        SettingsField(
            id="test_ex_app_field_3",
            title=_("Selection"),
            description=_("Select some option setting"),
            type=SettingsFieldType.SELECT,
            default="foo",
            placeholder=_("Select some option setting"),
            options=["foo", "bar", "baz"],
        ),
        SettingsField(
            id="test_ex_app_field_4",
            title=_("Toggle something"),
            description=_("Select checkbox option setting"),
            type=SettingsFieldType.CHECKBOX,
            default=False,
            label=_("Verify something if enabled"),
        ),
        SettingsField(
            id="test_ex_app_field_5",
            title=_("Multiple checkbox toggles, describing one setting"),
            description=_("Select checkbox option setting"),
            type=SettingsFieldType.MULTI_CHECKBOX,
            default={"foo": True, "bar": True},
            options={"Foo": "foo", "Bar": "bar", "Baz": "baz", "Qux": "qux"},
        ),
        SettingsField(
            id="test_ex_app_field_6",
            title=_("Radio toggles, describing one setting like single select"),
            description=_("Select radio option setting"),
            type=SettingsFieldType.RADIO,
            label=_("Select single toggle"),
            default="foo",
            options={_("First radio"): "foo", _("Second radio"): "bar", _("Third radio"): "baz"},
        ),
    ],
)


def enabled_handler(enabled: bool, nc: NextcloudApp) -> str:
    print(f"enabled={enabled}")
    if enabled:
        nc.ui.resources.set_initial_state(
            "top_menu",
            "first_menu",
            "ui_example_state",
            {"initial_value": "test init value"},
        )
        nc.ui.resources.set_script("top_menu", "first_menu", "js/ui_example-main")
        nc.ui.top_menu.register("first_menu", "UI example", "img/app.svg")
        nc.ui.files_dropdown_menu.register("test_menu", _("Test menu"), "/test_menu", mime="image/jpeg",
                                           icon="img/app-dark.svg")
        nc.ui.files_dropdown_menu.register_ex("test_redirect", _("Test redirect"), "/test_redirect", mime="image/jpeg",
                                              icon="img/app-dark.svg")
        nc.occ_commands.register("ui_example:ping", "/occ_ping")
        nc.occ_commands.register(
            "ui_example:setup",
            "/occ_setup",
            arguments=[
                {
                    "name": "test_arg",
                    "mode": "required",
                    "description": "Test argument",
                }
            ],
        )
        nc.occ_commands.register(
            "ui_example:stream",
            "/occ_stream",
            arguments=[
                {
                    "name": "stream_count",
                    "mode": "required",
                    "description": "Number of stream rows",
                }
            ],
            options=[
                {
                    "name": "double",
                    "mode": "optional",
                    "description": "Double the stream rows",
                    "default": False,
                }
            ],
        )

        if nc.srv_version["major"] >= 29:
            nc.ui.settings.register_form(SETTINGS_EXAMPLE)
    else:
        nc.ui.resources.delete_initial_state(
            "top_menu", "first_menu", "ui_example_state"
        )
        nc.ui.resources.delete_script("top_menu", "first_menu", "js/ui_example-main")
        nc.ui.top_menu.unregister("first_menu")
        nc.ui.files_dropdown_menu.unregister("test_menu")
        nc.ui.files_dropdown_menu.unregister("test_redirect")
        nc.occ_commands.unregister("ui_example:ping")
        nc.occ_commands.unregister("ui_example:setup")
        nc.occ_commands.unregister("ui_example:stream")
    return ""


class Button1Format(BaseModel):
    initial_value: str


@APP.post("/verify_initial_value")
async def verify_initial_value(
    input1: Button1Format,
):
    print("Old value: ", input1.initial_value)
    return responses.JSONResponse(
        content={"initial_value": str(random.randint(0, 100))}, status_code=200
    )


@APP.post("/test_menu")
async def test_menu_handler(
    file: UiActionFileInfo,
    nc: Annotated[NextcloudApp, Depends(nc_app)],
    accept_language: Annotated[str | None, Header()] = None
):
    print(f'File: {file}')
    print(f'Accept-Language: {accept_language}')
    print(_("Test menu"))
    # Note: Only singular string translations are supported
    nc.notifications.create(_('Test notification subject'), _("Test notification message"))
    return responses.Response()

class NodesPayload(BaseModel):
    files: list[UiActionFileInfo]


@APP.post("/test_redirect")
async def test_menu_handler(
    files: NodesPayload,
    nc: Annotated[NextcloudApp, Depends(nc_app)],
    accept_language: Annotated[str | None, Header()] = None
):
    print(f'Files: {files}')
    print(f'Accept-Language: {accept_language}')
    print(_("Test redirect"))
    nc.notifications.create(_('Test redirect notification subject'), _("Test redirect notification message"))
    return responses.JSONResponse(content={"redirect_handler": "first_menu/second_page"})


class OccPayload(BaseModel):
    arguments: dict | None = None
    options: dict | None = None


class OccData(BaseModel):
    occ: OccPayload


@APP.post("/occ_ping")
async def occ_ping():
    return responses.Response(content="<info>PONG</info>\n")


@APP.post("/occ_setup")
async def occ_setup(data: OccData):
    print(f"params: {data}")
    test_arg = data.occ.arguments['test_arg']
    print(f"test_arg: {test_arg}")
    if test_arg == "test":
        return responses.Response(content="<info>OK</info>\n")
    else:
        return responses.Response(content="<error>ERROR</error>\n")


def fake_data_streamer(data: OccData):
    stream_count = int(data.occ.arguments['stream_count'])
    if not stream_count:
        stream_count = 1
    if 'double' in data.occ.options:
        stream_count *= 2
    for i in range(stream_count):
        yield f"<info>Test stream row {i}</info>\n"
        time.sleep(0.5)


@APP.post("/occ_stream")
async def occ_stream(data: OccData):
    print(f"params: {data}")
    return StreamingResponse(fake_data_streamer(data), status_code=200, media_type="text/plain")


@APP.post("/nextcloud_file")
async def nextcloud_file(
    args: dict,
):
    print(args["file_info"])
    return responses.Response()


if __name__ == "__main__":
    run_app("main:APP", log_level="trace")
