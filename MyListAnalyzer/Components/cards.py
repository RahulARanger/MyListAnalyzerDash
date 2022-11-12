import typing
import dash_mantine_components as dmc
from MyListAnalyzer.Components.layout import expanding_layout, expanding_row
from MyListAnalyzer.Components.coreGraph import core_graph
from MyListAnalyzer.mappings.enums import css_classes
from dash import html, dcc
import logging


def graph_card(
        title, name, index, graph, extras=tuple(), menu_options=tuple(), is_resp=False,
        footer_class="graph-card-footer", card_class="graph-card",
        **__
):
    options = dmc.Menu(
        [dmc.MenuLabel(title), dmc.Divider(color="orange"), *menu_options], class_name=footer_class, trigger="hover"
    )
    elements = [
        expanding_layout(
            core_graph(graph, prefix=name, index=index, responsive=is_resp, **__),
        ),
        options,
        *extras
    ]
    return html.Article(elements, className=card_class)


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


def number_card_format_1(
        number=0, label="...", another=-1, color="green", class_name="", is_percent=True,
        ref_number=-1, ref_another=-1
):
    references = []
    references.append(html.Sub([
        "[",
        html.Span(another, title=str(another), className=f"count-number {class_name}"), "]"]
    )) if another >= 0 else ...

    numbers = [dmc.Text(
        f"{number:.2f}%" if is_percent else str(number), color=color, weight="bold", size="lg",
        class_name=f"percent-number count-number {class_name}"),
    ]

    references.insert(0, sign(number, ref_number, class_name)) if ref_number > -1 else ...
    numbers.append(dmc.Text(references, size="xs", color=color)) if references else ...
    references.append(sign(another, ref_another, class_name)) if another > -1 and ref_another > -1 else ...

    return expanding_row(
        expanding_layout(
            *numbers,
            direction="row", spacing=0, no_wrap=True, align="center", position="center"
        ),
        dmc.Space(h=1),
        dmc.Divider(
            label=" ".join(label.capitalize().split("_")), color=color, labelPosition="center",
            style={"opacity": 0.8, "width": "100%"}
        ), class_name=f"number-card {class_name}")


def slides(x):
    def _operate(*_, **__):
        return [html.Aside(
            card, className="embla__slide"
        ) for card in x(*_, **__)]

    return _operate


def one_card_at_a_time(gives_slides):
    def _operate(*_, **__):
        class_name = __.get("class_name", "")
        return html.Article(
            html.Section(
                html.Div(
                    gives_slides(*_, **__), className="embla__container"
                ), className="embla__viewport"
            ), className=f"embla {class_name}"
        )

    return _operate


@one_card_at_a_time
@slides
def graph_two_cards(fig, fig_class="", index=0, animate=True, is_resp=False, class_name="", second_card=html.Section("Not yet Implemented")):
    return dcc.Graph(
        figure=fig,
        className=fig_class,
        animate=animate,
        config=dict(),
        responsive="auto" if is_resp is None else is_resp,
        id=dict(index=index, type=class_name)
    ), second_card
