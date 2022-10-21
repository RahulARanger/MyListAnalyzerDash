import logging
import os
from MyListAnalyzer import __name__ as name
from dash import Dash, page_container
import dash_mantine_components as dmc
from dotenv import load_dotenv

load_dotenv()

assert os.getenv("MAL_CLIENT_ID"), "We need client id for MAL"


logging.getLogger('flask_cors').level = logging.DEBUG


class MainApplication:
    def __init__(self):
        self.__app = Dash(
            name,
            title="MAL-Remainder",
            update_title="Loading...",
            use_pages=True,
            external_scripts=[
                "https://unpkg.com/dash.nprogress@latest/dist/dash.nprogress.js",
                "https://unpkg.com/embla-carousel/embla-carousel.umd.js"
            ]
        )

        self.set_layout()

    @property
    def app(self):
        return self.__app

    def set_layout(self):
        self.app.layout = dmc.MantineProvider(
            theme={"colorScheme": "dark", "fontFamily": "'segoe ui', 'Inter', sans-serif"},
            children=[
                page_container
            ]
        )


if __name__ == "__main__":
    Application = MainApplication()
    Application.app.run(port=6969, dev_tools_ui=True, debug=True, host="127.0.0.1")
