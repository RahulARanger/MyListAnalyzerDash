from dash import register_page
from MyListAnalyzerDash.Parts.view_page import ViewPage
from MyListAnalyzerDash.mappings.enums import home_page
from MyListAnalyzerDash.utils import from_css

page = ViewPage()
page.connect_callbacks()


def layout(name=""):
    return [*page.layout(name), from_css("user-view.css"), from_css("general-dashboard.css")]


register_page(
    __name__, path_template="/MLA/view/<name>", title="User View", description=home_page.description,
    layout=layout)

register_page(
    __name__ + "-general", path="/MLA/view", title="User View", description=home_page.description, layout=layout
)
