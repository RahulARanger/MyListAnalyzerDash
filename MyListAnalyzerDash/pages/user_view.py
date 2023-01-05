from dash import register_page
from MyListAnalyzerDash.Parts.view_page import ViewPage
from MyListAnalyzerDash.utils import from_css
from collections import namedtuple
from dash import html

page_template = namedtuple(
    "PageTemplate", ["title", "description", "user_job", "path", "is_template", "layout"]
)

page = ViewPage()
page.connect_callbacks()
common_css = from_css("user-view.css"), from_css("general-dashboard.css"), from_css("https://cdn.jsdelivr.net/npm/swiper@8/swiper-bundle.min.css", path="")


def whole_layout(name=""):
    return html.Div(
        [*page.layout(name), *common_css]
    )


def layout_for_recently_tab(name=""):
    return html.Div([*page.layout(name, disable_user_job=True), *common_css])


user_view_requested = page_template(
    "User View", "User View for the requested user", True, "/MLA/view/<name>", True, whole_layout
)
user_view = user_view_requested._replace(
    path="/MLA/view", description="User View for yet to request user", title="User View - Say")

recent_view_requested = page_template(
    "Recent", "Dashboard for Recently watched animes for the requested user", False, "/MLA/view-r/<name>",
    True, layout_for_recently_tab
)

recent_view = recent_view_requested._replace(
    path="/MLA/view-r", description="Dashboard for Recently watched animes for yet to request users", title="Recent - Say"
)

for _ in (user_view_requested, user_view, recent_view_requested, recent_view):
    extras = {
        ("path_template" if _.is_template else "path"): _.path
    }

    register_page(
        __name__ + _.title, title=_.title, description=_.description, layout=_.layout, **extras
    )
