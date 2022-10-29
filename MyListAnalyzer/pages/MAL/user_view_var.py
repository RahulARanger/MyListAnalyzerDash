from dash import register_page
from MyListAnalyzer.Parts.view_page import ViewPage
from MyListAnalyzer.mappings.enums import home_page

register_page(__name__, path="/MLA/view/", title=home_page.name, description=home_page.description)

page = ViewPage()
page.connect_callbacks()


def layout():
    return page.layout()
