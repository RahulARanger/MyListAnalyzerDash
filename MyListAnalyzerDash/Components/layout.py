import typing

import dash_mantine_components as dmc
from dash import html


def expanding_layout(
        *children: object,
        spacing: str = "xs",
        direction: str = "column",
        position: str = "apart",
        align: str = "stretch",
        style: typing.Optional[typing.Dict[str, str]] = None,
        class_name: typing.Optional[str] = None,
        reverse: typing.Optional[bool] = False,
        id_: typing.Optional[str] = None,
        no_wrap: object = False,
        grow_child: object = False,
        grow: object = True
) -> object:
    extras = {"id": id_}
    extras.pop("id") if not id_ else ...

    _style = dict(height="100%", flexGrow=1 if grow else 0, flexDirection=direction + ("-reverse" if reverse else ""))
    _style.update(style) if style else ...

    return dmc.Group(
        children=children,
        spacing=spacing,
        position=position,
        align=align,
        style=_style,
        className=class_name,
        noWrap=no_wrap,
        grow=grow_child, **extras
    )


def expanding_scroll(*children, **__):
    return dmc.ScrollArea(
        children, type="auto", **__
    )


def expanding_row(*args, class_name="", style=None, id_=""):
    style = style if style else dict()

    extras = dict()
    extras.update(id=id_) if id_ else ...

    return html.Article(
        args, className=f"expanding-row {class_name}", style=style, **extras
    )
