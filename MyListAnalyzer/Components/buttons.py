import dash_mantine_components as dmc


def image_button(img_url, id_, class_name="action-icon", is_text=False):
    return dmc.ActionIcon(dmc.Text(img_url) if is_text else dmc.Image(src=img_url), class_name=class_name, id=id_)


def icon_butt(text, id_="", image_src="", class_name="custom_butt", size="md", disabled=False, color="orange"):
    return dmc.Button(
        text, id=id_, disabled=disabled, class_name=class_name, size=size, leftIcon=[dmc.Avatar(
            src=image_src, size="sm"
        )], color=color, style={"width": "100%"})
