import json
import typing
import dash_mantine_components as dmc
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.mappings.enums import css_classes
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


def _number_comp(number, is_percent, color, class_name, size="lg"):
    return dmc.Text(
        f"{number:.2f}%" if is_percent else str(number), color=color, weight="bold", size=size,
        class_name=f"{css_classes.as_percent} {css_classes.number_counter} {class_name}")


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

    numbers = [_number_comp(number, is_percent, color, class_name)]

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
        class_name: str = None,
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
                _number_comp(value, False, color, class_name),
                dmc.Divider(color="gray", orientation="vertical"),
                _number_comp(percent_value, True, color, class_name, size="md"),
                direction="row", position="center"
            ),
            _divider(label, color)
        )
    )
