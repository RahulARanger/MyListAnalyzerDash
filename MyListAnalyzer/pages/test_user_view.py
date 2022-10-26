from dash import register_page
from MyListAnalyzer.Parts.view_page import ViewPage
from MyListAnalyzer.mappings.enums import home_page

register_page(__name__, path_template="/MLA/view/<name>", title="User View", description=home_page.description)

page = ViewPage()


def layout(name=""):
    return page.layout(name)
