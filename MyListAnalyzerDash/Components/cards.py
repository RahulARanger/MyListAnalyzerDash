import logging
import logging
import typing
import dash_mantine_components as dmc
from dash import html
from MyListAnalyzerDash.Components.ModalManager import relative_time_stamp_but_calc_in_good_way
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.Components.tooltip import floating_tooltip, set_tooltip
from MyListAnalyzerDash.mappings.enums import css_classes, recent_status_color, helper, status_colors
from MyListAnalyzerDash.utils import ellipsis_part, anime_link


def home_card(*children, as_card: typing.Union[str, bool] = False, **__):
    return dmc.Paper(
        expanding_layout(*children, **__),
        className=as_card if as_card else css_classes.home_card
    )


def no_data(directions, force=False):
    return home_card(
        dmc.Image(
            src="/assets/nodata.svg",
            withPlaceholder=True,
            alt="Failed to load illustration, but please wait for some time for data to get processed",
            placeholder="Illustration to inform you that data is currently getting processed, and suggests you to wait."
            , caption=directions, style=dict(width="25vw", marginTop="5vw")
        ), align="center", position="center", as_card="center-card"
    )


def error_card(directions):
    logging.exception(directions, exc_info=True)
    return home_card(dmc.Image(
        src="/assets/warning.svg",
        caption=f"Error while processing things, Please report it as a bug",
        alt="Error",
        placeholder="Failed to plot data",
        withPlaceholder=True, style=dict(width="25vw", marginTop="5vw")
    ), dmc.Code(directions),
        align="center", position="center", as_card="center-card")


def sign(number, reference, className=""):
    return dmc.Text([
        html.Span(" = " if number == reference else " ▼  " if number < reference else " ▲ "),
        html.Span(f'{abs(number - reference)}', className=f"count-number {className}")],
        color="yellow" if number == reference else "red" if number < reference else "green",
        size="xs", className="indicator-number"
    )


def number_comp(number, is_percent, color, class_name, size="lg"):
    exact_value = f"{number:.2f}%" if is_percent else str(number)
    class_name_added = f"{css_classes.number_counter} {class_name}"

    if is_percent:
        class_name_added += f" {css_classes.as_percent}"

    return dmc.Text(
        floating_tooltip(html.Span(
            exact_value, className=class_name_added, **{"data-value": exact_value}
        ), label=exact_value),
        color=color, weight="bold", size=size
    )


def _number_layout(*numbers):
    return expanding_layout(
        *numbers,
        direction="row", spacing=0, no_wrap=True, align="center", position="center"
    )


def _divider(label: str = "", color: str = "gray"):
    return dmc.Divider(
        label=label, color=color, labelPosition="center",
        style={"opacity": 0.8, "width": "100%"})


def number_card_format_1(
        number=0, label="...", another=-1, color="green", class_name=None, is_percent=True,
        ref_number=-1, ref_another=-1,
        main_class=None
):
    references = []
    references.append(floating_tooltip(
        html.Sub([
            "[", html.Span(
                another, className=f"{css_classes.number_counter} {class_name}", **{"data-value": another}), "]"]
        ), label=another
    )) if another >= 0 else ...

    numbers = [number_comp(number, is_percent, color, class_name)]

    references.insert(0, sign(number, ref_number, class_name)) if ref_number > -1 else ...
    numbers.append(dmc.Text(references, size="xs", color=color)) if references else ...
    references.append(sign(another, ref_another, class_name)) if another > -1 and ref_another > -1 else ...

    return expanding_row(
        _number_layout(*numbers),
        dmc.Space(h=1),
        _divider(" ".join(label.capitalize().split("_")), color),
        class_name=f"number-card {class_name} {main_class}")


def card_format_4(text, label, color, class_name, size="lg", url=None):
    return expanding_row(
        expanding_row(
            dmc.Text(text, size=size, color=color, weight="bold") if not url else dmc.Anchor(
                text, size=size, color=color, href=url, weight="bold", target="_blank"),
            style=dict(justifyContent="center")
        ),
        dmc.Space(h=1),
        _divider(label, color),
        class_name=f"number-card {class_name}"
    )


def number_card_format_2(label, icon, value=0, color="red", percent_value=0, class_name=None):
    return expanding_row(
        dmc.Avatar(src=icon, size="lg"),
        expanding_layout(
            expanding_layout(
                number_comp(value, False, color, class_name),
                # dmc.Divider(color="gray", orientation="vertical"),
                # number_comp(percent_value, True, color, class_name, size="md"),
                direction="row", position="center"
            ),
            _divider(label, color)
        )
    )


def number_card_format_3(
        class_name="",
        index=0,
        id_="",
        anime_name="Testing",
        time_stamp=0,
        up_until=4,
        difference=2,
        status_label="Hold",
        total=12,
        re_watching=True,
        link=""
):
    link = link if link else f"https://myanimelist.net/anime/{id_}"
    try:
        status_color = getattr(recent_status_color, status_label)
    except AttributeError:
        status_color = "red"

    current = up_until - ((-1 if re_watching else 1) * difference)
    changed = f"{'' if not difference else '-' if re_watching else '+'}{difference}"
    so = f"{current} {changed} → {up_until}"

    progress = dmc.Progress(
        sections=[
            dict(value=(current / total) * 1e2, color="green", tooltip=so),
            dict(
                value=(difference / total) * 1e2,
                color="violet" if re_watching else "indigo", label=changed, tooltip=so
            )
        ], animate=status_label == "Watching"
    ) if total else dmc.Progress(
        sections=[
            dict(value=100, color="cyan", tooltip=so, label=so),
        ], animate=True, striped=True
    )

    return expanding_layout(
        expanding_row(
            set_tooltip(dmc.Anchor(
                anime_name,
                href=link, target="_blank", size="lg", align="center",
                style=dict(textOverflow="ellipsis")
            ), anime_name),
            html.Sup(
                dmc.Text(
                    html.Span(str(index + 1), **{"data-rank": str(index + 1)}, className=css_classes.rank_index_format),
                    size="xs", color="yellow"
                ))
        ),
        progress,
        dmc.Divider(color=status_color),
        expanding_row(
            dmc.Badge(status_label, color=status_color, size="sm"),
            relative_time_stamp_but_calc_in_good_way(
                False, default=time_stamp,
                size="sm"
            )
        ), class_name=f"{class_name} belt"
    )


def number_parameter(label, value, class_name, is_percent=False):
    return expanding_layout(
        dmc.Text(label, color="gray", size="sm"),
        number_comp(value, is_percent, color="light", size="xs", class_name=class_name),
        spacing=2, align="flexStart", position="left")


def special_anime_card(name, url, picture, special_label, special_color, progress, special_about, special_value, _info,
                       *parameters, class_name=""):
    info = floating_tooltip(
        dmc.ActionIcon(
            dmc.Image(src=helper.info), size="sm"
        ),
        label=_info,
        multiline=True, width=190
    )

    return expanding_layout(
        expanding_row(
            dmc.Image(src=picture, width=70, height=102, fit="contain"),
            expanding_layout(
                set_tooltip(
                    dmc.Anchor(
                        name, href=url, size="sm", target="_blank",
                        style=ellipsis_part(220)
                    ), label=name
                ),
                progress,
                expanding_row(
                    *(expanding_layout(
                        dmc.Text(label, color="gray", size="sm"),
                        dmc.Text(value, size="xs", weight="bold"), spacing=2, align="flexStart", position="left",
                        no_wrap=True
                    ) for label, value in zip(("Favs", "Start Date", "Finish Date"), parameters)),
                    info, style=dict(columnGap="3px", justifyContent="flex-start")
                ), no_wrap=True, spacing="sm"
            ), style=dict(padding="1px", gap="12px")
        ), dmc.Divider(
            label=dmc.Text(
                special_label,
                weight="bold",
                style=dict(textShadow="-2px 4px 0 rgba(0, 0, 0, 0.3)")),
            color=special_color, labelPosition="center", size="md"),
        floating_tooltip(
            dmc.Text(special_value, style=dict(position="absolute", top="0px", right="2px"), size="xs", color="yellow"),
            label=special_about
        ),
        class_name=f"anime_card {class_name}", style=dict(padding="1px"), spacing=0
    )


def relative_color(value, full):
    relative = value / full
    return "green" if relative > 0.89 else "teal" if relative > 0.85 else "lime" if relative > 0.75 else "yellow" if relative <= .69 else "orange" if relative <= 5 else "red"


def progress_bar_from_status(watched, total, status, watched_color="green", animate=False, *other_sections):
    value = dict(
        value=((watched / total) * 1e2) if total > 0 else 100,
        color=watched_color,
        tooltip=[dmc.Text(f"Status: {status}"), dmc.Text(f"Watched: {watched}"), dmc.Text(f"Total: {total}")]
    )
    return dmc.Progress(
        sections=[
            value,
            *other_sections
        ], animate=animate, size="md"
    )


def currently_airing_card(
        _id, title, img_url, user_started,
        watched, total, updated_at,
        source, status, started_week, started_time, started_date,
        class_name=css_classes.time_format
):
    cells = [
        ("Broadcast Started at", started_date),
        ("Started at", user_started if user_started else "NA"),
        ("Broadcast Time", started_time),
        ("Broadcast Weekday", started_week),
    ]

    rows = expanding_layout(
        *(expanding_layout(
            dmc.Text(cell[0], color="gray", size="sm"),
            dmc.Text(cell[1], size="xs", weight="bold"),
            spacing=.5, align="flexStart", position="left", no_wrap=True
        ) for cell in cells),
        progress_bar_from_status(
            watched, total, status, getattr(status_colors, status), animate=status == "watching"
        ), no_wrap=True
    )

    footer = expanding_row(
        set_tooltip(
            dmc.Anchor(title, href=anime_link(_id), style=ellipsis_part(150), size="sm"),
            title
        ),
        set_tooltip(
            dmc.Badge(source, color="orange", size="xs"),
            "Source"
        ),
        relative_time_stamp_but_calc_in_good_way(
            False, default=updated_at, isMS=True, isNotUTC=True,
            class_name=f"{class_name} rightFix", size="xs"),
        style=dict(alignItems="center", flexWrap="nowrap"),
    )

    return expanding_layout(
        expanding_row(
            dmc.Image(src=img_url, height=210, fit="cover", width=90),
            rows, style=dict(gap="10px")
        ),
        footer, class_name="swiper-slide"
    ), status
