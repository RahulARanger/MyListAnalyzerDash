from dash import html
import dash_mantine_components as dmc


def table_headers(*headers):
    return html.Thead(
        html.Tr(
            [html.Th(_) for _ in headers]
        ))


def table_generate(table_id, *rows, headers=("Key", "Value")):
    return dmc.Table(
        children=[table_headers(*headers), html.Tbody(rows)],
        captionSide="bottom", striped=True, highlightOnHover=True,
        id=table_id
    )
