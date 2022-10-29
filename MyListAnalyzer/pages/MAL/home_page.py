from dash import register_page
from MyListAnalyzer.Parts.home_page import HomePage
from MyListAnalyzer.mappings.enums import home_page

register_page(__name__, path="/MLA", title=home_page.name, description=home_page.description)

page = HomePage()
page.connect_callbacks()


def layout():
    return page.layout(0)
