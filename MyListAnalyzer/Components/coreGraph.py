from dataclasses import dataclass
import typing
from dash import dcc
import dash_mantine_components as dmc
import plotly.graph_objects as go


def with_slimmer(
        handler: typing.Callable[
            [dcc.Graph, str, str, typing.Tuple[typing.Any], typing.Dict[typing.Any, typing.Any]], go.Figure]
):
    def handle_subject(graph: dcc.Graph, prefix: str, index: str, *_, **__):
        graph = handler(graph, prefix, index, *_, **__)

        if not __.get("apply_shimmer", True):
            return graph

        return dmc.Skeleton(
            children=graph,
            animate=True,
            visible=False,
            id={
                "type": prefix,
                "index": index,
                "section": "shimmer"
            }
        )

    return handle_subject


@dataclass
class Config:
    butt_to_remove = ["zoom"]
    butts_to_add = ["drawopenpath", "eraseshape"]

    def to_dict(self):
        return {
            "modeBarButtonsToAdd": self.butts_to_add,
            "modeBarButtonsToRemove": self.butt_to_remove,
            "displaylogo": False
        }


@with_slimmer
def core_graph(
        fig: go.Figure, prefix: str, index: typing.Union[bool, str, int] = False,
        responsive: bool = "auto", class_name=None, config: Config = None, apply_shimmer=True, animate=True):
    config = config if config else Config()

    return dcc.Graph(
        id=prefix if index is False else {
            "section": prefix,
            "index": index
        },
        animate=animate,
        figure=fig,
        responsive=responsive,
        className=class_name,
        config=config.to_dict()
    )
