import typing
import dash_mantine_components as dmc
from dash import html
import random
import string
from MyListAnalyzerDash.utils import set_timestamp


def show_notifications(title: object, *message: object, auto_close: typing.Union[bool, int] = False, color: object = "red") -> object:
    return dmc.Notification(
        title=set_timestamp(title),
        color=color,
        autoClose=auto_close,
        disallowClose=False,
        message=message,
        action="show",
        id="".join(random.choices(string.ascii_letters, k=10))
    )


def is_loading(id_, title, *message, color="orange", loaded=False):
    return dmc.Notification(
        title=title,
        message=message,
        id=id_,
        color=color,
        loading=not loaded,
        action="update" if loaded else "show",
        disallowClose=not loaded,
        autoClose=4000 if loaded else False
    )


def provider(*id_s):
    return dmc.NotificationsProvider(
        children=[html.Div(id=_) for _ in id_s],
        transitionDuration=690,
        zIndex=201,
        limit=6,
        position="bottom-right"
    )
