from dataclasses import dataclass
import typing
from dash import dcc
import dash_mantine_components as dmc
import plotly.graph_objects as go


@dataclass
class GraphInfo:
    multiple: bool
    show_x: bool
    show_y: bool
    show_x_grid: bool
    show_y_grid: bool
    allow_drag: bool
    mt: int
    mb: int
    ml: int
    mr: int
    width: typing.Optional[int]
    height: typing.Optional[int]
    pad: int
    showlegend: bool
    autosize: bool
    legend_x: int
    legend_y: int
    legend_title: str
    legend_font_size: int
    x_tick_angle: int
    title: str
    x_title: str
    y_title: str
    hover_mode: str


class BeautifyMyGraph(GraphInfo):
    def __init__(
            self, multiple=False, show_x=False, show_y=False,
            show_x_grid=False, show_y_grid=False, allow_drag=False,
            ml=1, mr=1, mt=5, mb=2, width=None, height=None,
            pad=0, showlegend=False, autosize=False, legend_x=1, legend_y=1, legend_title=None, legend_font_size=10,
            x_tick_angle=45, title="", x_title="", y_title="", hover_mode="closest"
    ):
        super().__init__(
            multiple, show_x, show_y, show_x_grid, show_y_grid, allow_drag,
            mt, mb, ml, mr, width, height, pad, showlegend, autosize,
            legend_x, legend_y, legend_title, legend_font_size, x_tick_angle, title, x_title, y_title,
            hover_mode=hover_mode
        )
        self.worker: typing.Optional[typing.Callable] = None

    def __call__(
            self, worker_subject: typing.Callable
    ) -> typing.Callable:
        self.worker = worker_subject
        return self.handle_worker

    def handle_worker(self, *args, **kwargs) -> typing.Union[
        typing.Tuple[go.Figure, typing.Any], typing.List[go.Figure], go.Figure]:

        rec = self.worker(*args, **kwargs)
        if self.multiple:
            return [self.handle_subject(fig) for fig in rec]
        elif isinstance(rec, tuple):
            return self.handle_subject(rec[0]), *rec[1:]
        else:
            return self.handle_subject(rec)

        # in case if u need to handle multiple return a sequence of figures
        # in case u need to return multiple but handle only one figure ?, then return casually

    def handle_subject(self, figure: go.Figure) -> go.Figure:
        font_family = 'Arial Helvetica Barlow'
        font = dict(family=font_family, size=12)

        title_font = font.copy()
        title_font["size"] += 2

        figure.update_layout(
            dragmode=self.allow_drag,
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font={
                "family": font_family
            },
            margin=dict(
                l=self.ml,
                r=self.mr,
                b=self.mb,
                t=max(self.mt, title_font["size"]) + 10,
                pad=self.pad
            ),
            width=self.width,
            height=self.height,
            showlegend=self.showlegend,
            autosize=self.autosize,
            legend=dict(
                x=self.legend_x,
                y=self.legend_y,
                title_text=self.legend_title,
                font=dict(
                    size=self.legend_font_size, family=font_family
                )
            ),
            title=dict(
                text=self.title if self.title else f"{self.title}<br><br><br><br>", font=title_font
            ), hovermode=self.hover_mode
        )

        figure.update_xaxes(
            showgrid=self.show_x_grid, visible=self.show_x, automargin=True,
            title=dict(text=self.x_title, font=font)
        )
        figure.update_yaxes(
            showgrid=self.show_y_grid, visible=self.show_y, automargin=True,
            title=dict(text=self.y_title, font=font)
        )

        return figure


def shimmer(graph, prefix, index):
    return dmc.Skeleton(
        children=graph,
        animate=True,
        visible=False,
        id=dict(type=prefix, index=index, section="shimmer")
    )


@dataclass
class Config:
    butt_to_remove = ["zoom"]
    butts_to_add = ["drawopenpath", "eraseshape"]
    scroll_zoom = False
    editable = False

    def to_dict(self):
        return {
            "editable": self.editable,
            "modeBarButtonsToAdd": self.butts_to_add,
            "modeBarButtonsToRemove": self.butt_to_remove,
            "displaylogo": False,
            "scrollZoom": self.scroll_zoom
        }


def core_graph(
        fig: go.Figure, prefix: str, index: typing.Union[bool, str, int] = False,
        responsive: bool = "auto", class_name=None, config: Config = None, apply_shimmer=True, animate=False):
    config = config if config else Config()

    graph = dcc.Graph(
        id=prefix if index is False else dict(type=prefix, index=index),
        animate=animate,
        figure=fig,
        responsive=responsive,
        className=class_name,
        config=config.to_dict()
    )

    return graph if not apply_shimmer else shimmer(graph, prefix, index)


def style_dash_table():
    # styles for the header, data
    return (
        dict(
            backgroundColor="transparent", color="white", border="1px ridge orange", textAlign="center",
            fontSize="0.8rem", fontWeight="bold"),
        dict(backgroundColor="transparent", color="white", fontSize="0.69rem", textAlign="left"),
        dict(overflow="hidden", textOverflow="ellipsis", maxWidth="0")
    )
