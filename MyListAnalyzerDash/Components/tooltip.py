import dash_mantine_components as dmc


def set_tooltip(inside, label, pos="bottom", zIndex=1, color="dark", class_name=None):
    return dmc.Tooltip(
        inside,
        color=color, label=label, position=pos, zIndex=zIndex, className=class_name
    )


def floating_tooltip(inside, label, pos="bottom", zIndex=1, color="dark", multiline=False, width=""):
    defaults = dict()
    if width:
        defaults["width"] = width

    return dmc.FloatingTooltip(
        label=label,
        color=color,
        position=pos,
        children=inside,
        zIndex=zIndex,
        multiline=multiline, **defaults
    )
