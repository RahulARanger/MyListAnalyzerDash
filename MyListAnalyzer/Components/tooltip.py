import dash_mantine_components as dmc


def set_tooltip(inside, label, pos="bottom", zIndex=1):
    return dmc.Tooltip(
        inside, color="orange", label=label, position=pos, placement="center", wrapLines=True, zIndex=zIndex
    )
