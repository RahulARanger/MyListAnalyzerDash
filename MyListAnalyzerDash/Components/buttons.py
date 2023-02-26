import typing

import dash_mantine_components as dmc
from MyListAnalyzerDash.Components.tooltip import set_tooltip
from MyListAnalyzerDash.utils import anime_href, ellipsis_part
from MyListAnalyzerDash.mappings.enums import Icons


def icon_butt_img(
        img_url, id_: typing.Optional[typing.Union[str, dict]] = None, class_name="action-icon",
        is_text=False, pad=4, style=None):
    kwargs = style if style else dict()
    kwargs.update(id=id_) if id_ else ...
    return dmc.ActionIcon(
        dmc.Text(img_url) if is_text else dmc.Image(src=img_url), className=class_name, p=pad,
        style=kwargs)


def button_with_icon(text, id_="", image_src="", class_name="custom_butt", size="md", disabled=False, color="orange",
                     **style):
    kwargs = dict(style=dict(width="100%"), color=color, size=size)
    kwargs.update(id=id_, **style) if id_ else ...

    return dmc.Button(
        text, disabled=disabled, className=class_name, leftIcon=[dmc.Avatar(
            src=image_src, size="sm"
        )], **kwargs)


def anime_link(name, id_):
    return set_tooltip(
        dmc.Menu([
            dmc.MenuTarget(dmc.Text(name, color="blue.6", style=ellipsis_part(150), size="sm")),
            dmc.MenuDropdown([dmc.MenuItem(
                    "Know More", href=anime_href(id_), target="_blank",
                    icon=icon_butt_img(Icons.redirect)
            )])], withArrow=True), name
    )
