import dash_mantine_components as dmc


def set_tooltip(inside, label, pos="bottom", zIndex=1, color="dark"):
    return dmc.Tooltip(
        inside,
        color=color, label=label, position=pos, zIndex=zIndex
    )


def floating_tooltip(inside, label, pos="bottom", zIndex=1, color="dark"):
    return dmc.FloatingTooltip(
        label=label,
        color=color,
        position=pos,
        children=inside,
        zIndex=zIndex
    )
