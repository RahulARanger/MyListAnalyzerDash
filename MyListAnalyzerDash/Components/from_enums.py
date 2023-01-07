import dash_mantine_components as dmc
from MyListAnalyzerDash.Components.ModalManager import relative_time_stamp_but_calc_in_good_way
from MyListAnalyzerDash.Components.cards import number_comp


def parse_enum(obj, size="sm", class_name=""):
    typed = obj.get("obj", None)
    value = obj.get("value", "NA")

    if typed == "str":
        return dmc.Text(
            value, size=size
        )

    if typed == "time":
        return relative_time_stamp_but_calc_in_good_way(
            False, default=value, size=size
        )

    if typed == "number" or typed == "percent":
        return number_comp(
            value, typed == "percent", obj.get("color", "orange"), class_name
        )