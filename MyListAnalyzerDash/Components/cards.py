import json
import logging
import typing
from dataclasses import dataclass, asdict

import dash_mantine_components as dmc
from dash import html
from dash.dependencies import Component

from MyListAnalyzerDash.Components.ModalManager import relative_time_stamp_but_calc_in_good_way
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.mappings.enums import css_classes, recent_status_color, helper
from MyListAnalyzerDash.Components.tooltip import floating_tooltip, set_tooltip


@dataclass
class SplideOptions:
    # Subset of options presented in https://splidejs.com/guides/options
    type: str = "slide"
    autoplay: bool = False
    rewind: bool = False
    arrows: bool = False
    pagination: bool = False
    width: str = "200px"
    mediaQuery: str = "min"
    perPage: int = 1
    gap: str = "0px"
    padding: str = "0px"
    autoScroll: typing.Union[typing.Dict[str, int], bool] = False
    breakpoints: typing.Union[typing.Dict, bool] = False

    def embeded(self):
        return json.dumps(asdict(self))

    @classmethod
    def with_breakpoints(cls):
        return dict(
            mediaQuery="max",
            breakpoints={
                "1120": dict(perPage=3.5),
                "980": dict(perPage=3),
                "860": dict(perPage=2.5),
                "740": dict(perPage=2),
                "620": dict(perPage=1.5),
                "420": dict(perPage=1.25),
                "300": dict(perPage=1)
            }
        )


def home_card(*children, as_card: typing.Union[str, bool] = False, **__):
    return dmc.Paper(
        expanding_layout(*children, **__),
        className=as_card if as_card else css_classes.home_card
    )


def no_data(directions, force=False):
    return home_card(
        dmc.Image(
            src="/assets/nodata.svg",
            withPlaceholder=True,
            alt="Failed to load illustration, but please wait for some time for data to get processed",
            placeholder="Illustration to inform you that data is currently getting processed, and suggests you to wait."
            , caption=directions, style=dict(width="25vw", marginTop="5vw")
        ), align="center", position="center", as_card="center-card"
    )


def error_card(directions):
    logging.exception(directions, exc_info=True)
    return home_card(dmc.Image(
        src="/assets/warning.svg",
        caption=f"Error while processing things, Please report it as a bug",
        alt="Error",
        placeholder="Failed to plot data",
        withPlaceholder=True, style=dict(width="25vw", marginTop="5vw")
    ), dmc.Code(directions),
        align="center", position="center", as_card="center-card")


def sign(number, reference, className=""):
    return dmc.Text([
        html.Span(" = " if number == reference else " ▼  " if number < reference else " ▲ "),
        html.Span(f'{abs(number - reference)}', className=f"count-number {className}")],
        color="yellow" if number == reference else "red" if number < reference else "green",
        size="xs", className="indicator-number"
    )


def number_comp(number, is_percent, color, class_name, size="lg"):
    exact_value = f"{number:.2f}%" if is_percent else str(number)
    class_name_added = f"{css_classes.number_counter} {class_name}"

    if is_percent:
        class_name_added += f" {css_classes.as_percent}"

    return dmc.Text(
        floating_tooltip(html.Span(
            exact_value, className=class_name_added, **{"data-value": exact_value}
        ), label=exact_value),
        color=color, weight="bold", size=size
    )


def _number_layout(*numbers):
    return expanding_layout(
        *numbers,
        direction="row", spacing=0, no_wrap=True, align="center", position="center"
    )


def _divider(label: str = "", color: str = "gray"):
    return dmc.Divider(
        label=label, color=color, labelPosition="center",
        style={"opacity": 0.8, "width": "100%"})


def number_card_format_1(
        number=0, label="...", another=-1, color="green", class_name=None, is_percent=True,
        ref_number=-1, ref_another=-1,
        main_class=None
):
    references = []
    references.append(floating_tooltip(
        html.Sub([
            "[", html.Span(
                another, className=f"{css_classes.number_counter} {class_name}", **{"data-value": another}), "]"]
        ), label=another
    )) if another >= 0 else ...

    numbers = [number_comp(number, is_percent, color, class_name)]

    references.insert(0, sign(number, ref_number, class_name)) if ref_number > -1 else ...
    numbers.append(dmc.Text(references, size="xs", color=color)) if references else ...
    references.append(sign(another, ref_another, class_name)) if another > -1 and ref_another > -1 else ...

    return expanding_row(
        _number_layout(*numbers),
        dmc.Space(h=1),
        _divider(" ".join(label.capitalize().split("_")), color),
        class_name=f"number-card {class_name} {main_class}")


def card_format_4(text, label, color, class_name, size="lg", url=None):
    return expanding_row(
        expanding_row(
            dmc.Text(text, size=size, color=color, weight="bold") if not url else dmc.Anchor(
                text, size=size, color=color, href=url, weight="bold"), style=dict(justifyContent="center")
        ),
        dmc.Space(h=1),
        _divider(label, color),
        class_name=f"number-card {class_name}"
    )


def splide_slides(_slides: typing.Tuple[Component]):
    return [html.Li(
        card, className="splide__slide"
    ) for card in _slides]


def splide_container(
        *slides: Component,
        class_name: str = "",
        id_="",
        splide_options: SplideOptions = SplideOptions(),
        style=None
):
    splide_class = f"splide {class_name}"
    child = html.Div(
        html.Ul(
            splide_slides(slides), className="splide__list"
        ), className="splide__track"
    ),

    extras = {"data-splide": splide_options.embeded()}
    extras.update(id=id_) if id_ else ...

    _style = dict() if not style else style
    _style["minWidth"] = "20%"

    return html.Section(
        child, className=splide_class, **extras, style=_style
    )


def number_card_format_2(label, icon, value=0, color="red", percent_value=0, class_name=None):
    return expanding_row(
        dmc.Avatar(src=icon, size="lg"),
        expanding_layout(
            expanding_layout(
                number_comp(value, False, color, class_name),
                # dmc.Divider(color="gray", orientation="vertical"),
                # number_comp(percent_value, True, color, class_name, size="md"),
                direction="row", position="center"
            ),
            _divider(label, color)
        )
    )


def number_card_format_3(
        class_name="",
        index=0,
        id_="",
        anime_name="Testing",
        time_stamp=0,
        up_until=4,
        difference=2,
        status_label="Hold",
        total=12,
        re_watching=True,
        link=""
):
    link = link if link else f"https://myanimelist.net/anime/{id_}"
    try:
        status_color = getattr(recent_status_color, status_label)
    except AttributeError:
        status_color = "red"

    current = up_until - ((-1 if re_watching else 1) * difference)
    changed = f"{'' if not difference else '-' if re_watching else '+'}{difference}"
    so = f"{current} {changed} → {up_until}"

    progress = dmc.Progress(
        sections=[
            dict(value=(current / total) * 1e2, color="green", tooltip=so),
            dict(
                value=(difference / total) * 1e2,
                color="violet" if re_watching else "indigo", label=changed, tooltip=so
            )
        ], animate=status_label == "Watching"
    ) if total else dmc.Progress(
        sections=[
            dict(value=100, color="cyan", tooltip=so, label=so),
        ], animate=True, striped=True
    )

    return expanding_layout(
        expanding_row(
            set_tooltip(dmc.Anchor(
                anime_name,
                href=link, target="_blank", size="lg", align="center",
                style=dict(textOverflow="ellipsis")
            ), anime_name),
            html.Sup(
                dmc.Text(
                    html.Span(str(index + 1), **{"data-rank": str(index + 1)}, className=css_classes.rank_index_format),
                    size="xs", color="yellow"
                ))
        ),
        progress,
        dmc.Divider(color=status_color),
        expanding_row(
            dmc.Badge(status_label, color=status_color, size="sm"),
            relative_time_stamp_but_calc_in_good_way(
                False, default=time_stamp,
                size="sm"
            )
        ), class_name=f"{class_name} belt"
    )


def number_parameter(label, value, class_name, is_percent=False):
    return expanding_layout(
        dmc.Text(label, color="gray", size="sm"),
        number_comp(value, is_percent, color="light", size="xs", class_name=class_name),
        spacing=2, align="flexStart", position="left")


def special_anime_card(name, url, picture, special_label, special_color, progress, special_about, special_value, _info, *parameters, class_name=""):
    text_limit = 24
    info = floating_tooltip(
        dmc.ActionIcon(
            dmc.Image(src=helper.info), size="sm"
        ),
        label=_info,
        multiline=True, width=190
    )

    return expanding_layout(
        expanding_row(
            dmc.Image(src=picture, width=75, height=97, fit="contain"),
            expanding_layout(
                set_tooltip(
                    dmc.Anchor(
                        name[: text_limit] + ("..." if len(name) > text_limit else ""),
                        href=url, size="sm", target="_blank"
                    ), label=name
                ),
                progress,
                expanding_row(
                    *(expanding_layout(
                        dmc.Text(label, color="gray", size="sm"),
                        dmc.Text(value, size="xs", weight="bold"), spacing=2, align="flexStart", position="left",
                        no_wrap=True
                    ) for label, value in zip(("Favs", "Start Date", "Finish Date"), parameters)),
                    info, style=dict(columnGap="3px", justifyContent="flex-start")
                ), no_wrap=True
            )
        ), dmc.Divider(
            label=dmc.Text(
                special_label,
                weight="bold",
                style=dict(textShadow="-2px 4px 0 rgba(0, 0, 0, 0.3)")),
            color=special_color, labelPosition="center", size="md"),
        floating_tooltip(
            dmc.Text(special_value, style=dict(position="absolute", top="0px", right="0px"), size="xs", color="yellow"),
            label=special_about
        ),
        class_name=f"anime_card {class_name}", style=dict(padding="3px")
    )


def relative_color(value, full):
    relative = value / full
    return "green" if relative > 0.89 else "teal" if relative > 0.85 else "lime" if relative > 0.75 else "yellow" if relative <= .69 else "orange" if relative <= 5 else "red"


def progress_bar_from_status(watched, total, status, watched_color="green", animate=False, *other_sections):
    return dmc.Progress(
        sections=[
            dict(value=(watched / total) * 1e2, color=watched_color, tooltip=status),
            *other_sections
        ], animate=animate
    )
