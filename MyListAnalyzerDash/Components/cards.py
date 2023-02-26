import logging
import typing
import dash_mantine_components as dmc
from dash import html
from MyListAnalyzerDash.Components.ModalManager import relative_time_stamp_but_calc_in_good_way
from MyListAnalyzerDash.Components.layout import expanding_layout, expanding_row
from MyListAnalyzerDash.Components.tooltip import floating_tooltip, set_tooltip
from MyListAnalyzerDash.mappings.enums import CSSClasses, Icons, list_status_color
from MyListAnalyzerDash.Components.buttons import anime_link


def home_card(*children, as_card: typing.Union[str, bool] = False, **__):
    return dmc.Paper(
        expanding_layout(*children, **__),
        className=as_card if as_card else CSSClasses.home_card
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
    class_name_added = f"{CSSClasses.number_counter} {class_name}"

    if is_percent:
        class_name_added += f" {CSSClasses.as_percent}"

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
        number=0, label="...", another=-1, color="green", class_name="", is_percent=True,
        ref_number=-1, ref_another=-1,
        main_class=""
):
    references = []
    references.append(floating_tooltip(
        html.Sub([
            "[", html.Span(
                another, className=f"{CSSClasses.number_counter} {class_name}", **{"data-value": another}), "]"]
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


def number_parameter(label, value, class_name, is_percent=False):
    return expanding_layout(
        dmc.Text(label, color="gray", size="sm"),
        number_comp(value, is_percent, color="light", size="xs", class_name=class_name),
        spacing=2, align="flexStart", position="left")


def special_divider(special_label, special_color):
    return dmc.Divider(
        label=dmc.Text(
            special_label,
            weight="bold",
            style=dict(textShadow="-2px 4px 0 rgba(0, 0, 0, 0.3)")),
        color=special_color, labelPosition="center", size="md")


def special_anime_card(name, _id, picture, special_label, special_color, progress, special_about, special_value, _info,
                       *parameters, class_name=""):
    info = floating_tooltip(
        dmc.ActionIcon(
            dmc.Image(src=Icons.info), size="xs"
        ),
        label=_info,
        multiline=True, width=190
    )

    return expanding_layout(
        expanding_row(
            dmc.Image(src=picture, width=70, height=102, fit="contain", className=CSSClasses.to_zoom),
            expanding_layout(
                anime_link(name, _id),
                progress,
                expanding_row(
                    *(expanding_layout(
                        dmc.Text(label, color="dimmed", size="sm"),
                        dmc.Text(value, size="xs", weight="bold"), spacing=2, align="flexStart", position="left",
                        no_wrap=True
                    ) for label, value in zip(("Favs.", "Start Date", "Finish Date"), parameters)),
                    info, style=dict(columnGap="3px", justifyContent="flex-start")
                ), no_wrap=True, spacing="sm"
            ), style=dict(padding="1px", gap="12px")
        ), special_divider(special_label, special_color),
        floating_tooltip(
            dmc.Text(special_value, size="xs", color="white", className="special-thing"),
            label=special_about
        ),
        class_name=f"anime_card {class_name}", style=dict(padding="1px"), spacing=0
    )


def relative_color(value, full):
    relative = value / full
    return "green.9" if relative > 0.89 else "teal.5" if relative > 0.85 else "lime.3" if relative > 0.75 else "yellow" if relative <= .69 else "orange.6" if relative <= 5 else "red.9"


def progress_bar_from_status(watched, total, status, *extra):
    progressed = ((watched / total) * 1e2) if total and total > 0 else 100
    common = [dmc.Text(f"Status: {status}"), dmc.Text(f"Watched: {watched}"), dmc.Text(f"Total: {total}"), *extra]
    value = dict(
        value=progressed,
        color=list_status_color[status].value,
        tooltip=common,
        label=f"{watched}"
    )
    left = dict(
        value=100 - progressed, color="gray",
        tooltip=common,
        label=f"{(total - watched) if total else 'NA'}"
    )

    return dmc.Progress(
        sections=[
            value,
            left
        ], animate=status == "Watching", size="md", style=dict(minHeight="8px")
    )


def currently_airing_card(
        _id, title, img_url, user_started,
        watched, total, updated_at,
        source, status, started_week, started_time, started_date,
        class_name=CSSClasses.time_format
):
    cells = [
        ("Broadcast Started at", started_date),
        ("Started at", user_started if user_started else "NA"),
        ("Broadcast Time", started_time),
        ("Broadcast Weekday", started_week),
    ]

    rows = expanding_layout(
        *(expanding_layout(
            dmc.Text(cell[0], color="dimmed", size="sm"),
            dmc.Text(cell[1], size="xs", weight="bold"),
            spacing=.5, align="flexStart", position="left", no_wrap=True
        ) for cell in cells),
        progress_bar_from_status(watched, total, status), no_wrap=True
    )

    footer = expanding_row(
        anime_link(title, _id),
        set_tooltip(
            dmc.Badge(source, color="orange", size="xs"),
            "Source"
        ),
        relative_time_stamp_but_calc_in_good_way(
            False, default=updated_at, isMS=True, isNotUTC=True,
            class_name=f"{class_name} rightFix", size="sm"),
        style=dict(alignItems="center", flexWrap="nowrap"),
    )

    return dmc.HoverCard(
        (dmc.HoverCardTarget(expanding_layout(
            expanding_row(
                dmc.Image(src=img_url, height=210, fit="cover", width=90, className=CSSClasses.to_zoom),
                rows, style=dict(gap="10px")
            ), footer
        )), dmc.HoverCardDropdown(dmc.Text(title))), withArrow=True, withinPortal=True, className="swiper-slide"),\
        status


def number_card_format_3(
        anime_id, anime_name, status, total, up_until, time_stamp, difference,
        re_watching=True,
        _=False,
        *extra,
        special_label="",
        special_color="orange",
        class_name="",
        status_badge=True,

):
    badges = [dmc.Badge(
        relative_time_stamp_but_calc_in_good_way(False, default=time_stamp, size="xs", isMS=True), color="orange",
        size="xs"
    ), *extra]

    set_tooltip(badges.append(dmc.Badge(status, color=list_status_color[status].value, size="sm")), label="Status") if status_badge else ...

    return expanding_layout(
        anime_link(anime_name, anime_id),
        expanding_row(
            *badges, style=dict(alignItems="center")
        ),
        progress_bar_from_status(
            up_until, total, status,
            dmc.Text(f"{'+' if difference > 0 else ''}{difference} Eps")
        ),
        special_divider(special_label, special_color),
        class_name=f"{class_name} recent_anime", no_wrap=True, spacing="xs"
    )
