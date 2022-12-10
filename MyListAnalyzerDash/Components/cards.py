import json
import typing
import dash_mantine_components as dmc
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.mappings.enums import css_classes, recent_status_color
from MyListAnalyzerDash.Components.ModalManager import relative_time_stamp_but_calc_in_good_way
from dash import html, dcc
from dash.dependencies import Component
import logging
from dataclasses import dataclass, asdict, Field

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


def home_card(*children, as_card: typing.Union[str, bool] = False, **__):
    return dmc.Paper(
        expanding_layout(*children, **__),
        class_name=as_card if as_card else css_classes.home_card
    )


def no_data(directions, force=False):
    return home_card(dmc.Image(
        class_name="no-data",
        src="/assets/nodata.svg",
        caption=directions if force else f"No Data Found, Please wait or else open {directions} to start the Timer",
        alt="No Data Found",
        placeholder="No Data Found ",
        withPlaceholder=True
    ), align="center", position="center", as_card="center-card")


def error_card(directions):
    logging.exception(directions, exc_info=True)
    return home_card(dmc.Image(
        class_name="no-data",
        src="/assets/warning.svg",
        caption=f"Error while processing things, Please report it as a bug",
        alt="Error",
        placeholder="Failed to plot data",
        withPlaceholder=True
    ), dmc.Text(["Please refer to the error: ", dmc.Code(directions)]),
        align="center", position="center", as_card="center-card")


def sign(number, reference, class_name=""):
    return dmc.Text([
        html.Span(" = " if number == reference else " ▼  " if number < reference else " ▲ "),
        html.Span(f'{abs(number - reference)}', className=f"count-number {class_name}")],
        color="yellow" if number == reference else "red" if number < reference else "green",
        size="xs", class_name="indicator-number"
    )


def number_comp(number, is_percent, color, class_name, size="lg"):
    exact_value = f"{number:.2f}%" if is_percent else str(number)
    class_name_added = f"{css_classes.number_counter} {class_name}"

    if is_percent:
        class_name_added += f" {css_classes.as_percent}"

    return dmc.Text(
        html.Span(
            exact_value,
            title=exact_value, className=class_name_added
        ),
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
        ref_number=-1, ref_another=-1
):
    references = []
    references.append(html.Sub([
        "[",
        html.Span(another, title=str(another), className=f"{css_classes.number_counter} {class_name}"), "]"]
    )) if another >= 0 else ...

    numbers = [number_comp(number, is_percent, color, class_name)]

    references.insert(0, sign(number, ref_number, class_name)) if ref_number > -1 else ...
    numbers.append(dmc.Text(references, size="xs", color=color)) if references else ...
    references.append(sign(another, ref_another, class_name)) if another > -1 and ref_another > -1 else ...

    return expanding_row(
        _number_layout(*numbers),
        dmc.Space(h=1),
        _divider(" ".join(label.capitalize().split("_")), color),
        class_name=f"number-card {class_name}")


def splide_slides(_slides: typing.Tuple[Component]):
    return [html.Li(
        card, className="splide__slide"
    ) for card in _slides]


def splide_container(
        *slides: Component,
        class_name: str = "",
        id_="",
        splide_options: SplideOptions = SplideOptions()
):
    splide_class = f"splide {class_name}"
    child = html.Div(
        html.Ul(
            splide_slides(slides), className="splide__list"
        ), className="splide__track"
    ),

    extras = {"data-splide": splide_options.embeded()}
    extras.update(id=id_) if id_ else ...

    return html.Section(
        child, className=splide_class, **extras, style=dict(minWidth="20%")
    )


def number_card_format_2(label, icon, value=0, color="red", percent_value=0, class_name=None):
    return expanding_row(
        dmc.Avatar(src=icon, size="lg"),
        dmc.Space(w=6),
        expanding_layout(
            expanding_layout(
                number_comp(value, False, color, class_name),
                dmc.Divider(color="gray", orientation="vertical"),
                number_comp(percent_value, True, color, class_name, size="md"),
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
        link="",
        size="sm"
):

    link = link if link else f"https://myanimelist.net/anime/{id_}"
    try:
        status_color = getattr(recent_status_color, status_label)
    except AttributeError:
        status_color = "red"

    changed = expanding_row(
        dmc.Text("+" if difference else "", size=size, color="green", weight="bold"),
        number_comp(
            difference, is_percent=False, class_name=class_name, color="green", size=size
        ), style=dict(alignItems="center", justifyContent="flex-start")
    ) if not re_watching else dmc.Badge("Re-watching", color="blue", size=size)

    up_until_comp = number_comp(
        up_until, color="blue" if difference else "violet", size=size, class_name=class_name, is_percent=False)

    transition = [expanding_row(
            number_comp(up_until - difference, color="cyan", size=size, class_name=class_name, is_percent=False),
            dmc.Text("→", color="gray", size=size), up_until_comp,
            style=dict(alignItems="center", justifyContent="center")
        ) if difference else up_until_comp]

    transition.append(
        expanding_row(
            dmc.Text("Total: ", size=size, color="orange"),
            number_comp(total, is_percent=False, size=size, color="orange", class_name=class_name),
            style=dict(justifyContent="flex-end")
        )
    ) if total else ...

    return expanding_layout(
        expanding_row(
            dmc.Anchor(
                html.Span(anime_name, title=anime_name),
                href=link, target="_blank", size="lg", align="center",
                style=dict(textOverflow="ellipsis")
            ),
            html.Sup(
                dmc.Text(
                    html.Span(str(index + 1), **{"data-rank": str(index + 1)}, className=css_classes.rank_index_format),
                    size="xs", color="yellow"
                ))
        ),
        expanding_row(
            changed,
            *transition,
            style=dict(alignItems="center")
        ),
        dmc.Divider(color=status_color),
        expanding_row(
            dmc.Badge(status_label, color=status_color, size="sm"),
            relative_time_stamp_but_calc_in_good_way(
                False, default=time_stamp,
                size="sm", class_name=css_classes.time_format
            )
        ), class_name=f"{class_name} belt"
    )
