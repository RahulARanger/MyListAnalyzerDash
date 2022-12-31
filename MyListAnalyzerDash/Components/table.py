from dash import html
import dash_mantine_components as dmc


class MakeTable:
    def __init__(self):
        self.headers = ...
        self.rows = []
        self.cells = []

    def set_headers(self, headers, class_name="make-table-thead"):
        self.headers = html.Thead(html.Tr(
            [html.Th(header) for header in headers], className=class_name
        ))

    def make_row(self, row_class="make-table-row"):
        self.rows.append(html.Tr(
            self.cells.copy(), className=row_class
        ))
        return self.cells.clear()

    def add_cell(self, cell_text, cell_class="make-table-cell"):
        return self.cells.append(
            html.Td(cell_text, className=cell_class)
        )

    def __call__(self):
        return dmc.Table(
            [self.headers, html.Tbody(self.rows)],
            striped=True, highlightOnHover=True,
            withBorder=True, withColumnBorders=True,
            verticalSpacing="md"
        )

