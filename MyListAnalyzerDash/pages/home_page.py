import dash
from dash import register_page, html, get_app
from MyListAnalyzerDash.Parts.home_page import HomePage
from MyListAnalyzerDash.mappings.enums import HomeEnum
from MyListAnalyzerDash.utils import from_css

page = HomePage()
page.connect_callbacks()
app: dash.Dash = get_app()


def layout():
    return html.Div([page.layout(), from_css("home-page.css")])


register_page(__name__, path="/MLA", title=HomeEnum.name, description=HomeEnum.description, layout=layout)
