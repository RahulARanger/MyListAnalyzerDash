import dash_mantine_components as dmc
from dash import html


def expanding_layout(
        *children,
        spacing="xs",
        direction="column",
        position="apart",
        align="stretch",
        style=None,
        class_name=None,
        reverse=False,
        grow=True,
        id_=None,
        no_wrap=False,
        grow_child=False
):
    extras = {"id": id_}
    extras.pop("id") if not id_ else ...

    return dmc.Group(
        children=children,
        spacing=spacing,
        direction=direction,
        position=position,
        align=align,
        style=None if style is False else {
            "flexDirection": direction + ("-reverse" if reverse else ""),
            "flexGrow": "initial" if grow is False else 1 if grow is True else grow,
            "height": "initial" if grow is False else "100%"
        },
        class_name=class_name,
        noWrap=no_wrap,
        grow=grow_child, **extras
    )


def expanding_scroll(*children, **__):
    return dmc.ScrollArea(
        children, type="auto", **__
    )


def expanding_row(*args, class_name="", style=None, id_=""):
    style = style if style else dict()
    return html.Article(
        args, className=f"expanding-row {class_name}", style=style, id=id_
    )
