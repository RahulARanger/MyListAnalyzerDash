from dash import register_page
import dash_mantine_components as dmc
from MyListAnalyzerDash.mappings.enums import view_dashboard, status_colors, status_labels, seasons_maps, \
    status_light_colors, css_classes
from MyListAnalyzerDash.Components.cards import number_card_format_1, no_data, error_card, splide_container, \
    number_card_format_2, SplideOptions, number_card_format_3
from MyListAnalyzerDash.Components.layout import expanding_row, expanding_layout
from MyListAnalyzerDash.utils import from_css


def layout():
    tab_name = "Recently"

    cards = [
        number_card_format_3(
            class_name=tab_name)
        for _ in range(10)
    ]
    splide_options = SplideOptions(
        type="loop", width="", perPage=3, gap=".69rem", padding="6px", autoScroll=dict(speed=1),
        mediaQuery="max",
        breakpoints={
            "720": dict(perPage=2),
            "420": dict(perPage=1.5)
        }
    )
    child = expanding_layout(
        splide_container(*cards, splide_options=splide_options, class_name=tab_name),
        dmc.Paper("Hi There")
    )

    return [dmc.LoadingOverlay(children=child, class_name="home"), from_css("home-page.css"),
            from_css("general-dashboard.css")]


register_page(
    __name__ + "-test-comp", title="Sample", layout=layout, path="/_test"
)
