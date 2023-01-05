import dash
from dash import register_page, html, get_app
from MyListAnalyzerDash.Parts.home_page import HomePage
from MyListAnalyzerDash.mappings.enums import home_page
from MyListAnalyzerDash.utils import from_css

page = HomePage()
page.connect_callbacks()
app: dash.Dash = get_app()


def layout():
    return html.Div([page.layout(0), from_css("home-page.css")])


register_page(__name__, path="/MLA", title=home_page.name, description=home_page.description, layout=layout)
