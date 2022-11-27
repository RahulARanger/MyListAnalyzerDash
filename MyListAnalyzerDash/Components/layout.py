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
        id_=None,
        no_wrap=False,
        grow_child=False
):
    extras = {"id": id_}
    extras.pop("id") if not id_ else ...

    _style = dict(height="100%", flexGrow=1, flexDirection=direction + ("-reverse" if reverse else ""))
    _style.update(style) if style else ...

    return dmc.Group(
        children=children,
        spacing=spacing,
        direction=direction,
        position=position,
        align=align,
        style=_style,
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

    extras = dict()
    extras.update(id=id_) if id_ else ...

    return html.Article(
        args, className=f"expanding-row {class_name}", style=style, **extras
    )
