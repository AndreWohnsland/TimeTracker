from dataclasses import dataclass

import qtawesome as qta
from PyQt6.QtGui import QIcon

from src.utils import get_background_color, get_font_color


@dataclass
class PresetIconNames:
    start = "fa5s.play"
    stop = "fa5.pause-circle"
    exit = "mdi.close-box-outline"
    stats = "fa5s.chart-line"
    table = "fa5s.table"
    setting = "fa6s.gear"
    clock = "fa5.clock"
    delete = "fa5.trash-alt"
    edit = "fa5.edit"


@dataclass
class PresetIcon:
    start: QIcon
    stop: QIcon
    exit: QIcon
    stats: QIcon
    table: QIcon
    setting: QIcon
    clock: QIcon
    delete: QIcon
    delete_inverted: QIcon
    edit: QIcon
    edit_inverted: QIcon


def generate_icon(icon_name: str, color: str = "white") -> QIcon:
    return qta.icon(icon_name, color=color)


def get_preset_icons() -> PresetIcon:
    default_color = get_font_color()
    bg_color = get_background_color()
    return PresetIcon(
        start=generate_icon(PresetIconNames.start, "green"),
        stop=generate_icon(PresetIconNames.stop, "orange"),
        exit=generate_icon(PresetIconNames.exit, "red"),
        stats=generate_icon(PresetIconNames.stats, "#0F84FF"),
        table=generate_icon(PresetIconNames.table, default_color),
        setting=generate_icon(PresetIconNames.setting, "gray"),
        clock=generate_icon(PresetIconNames.clock, default_color),
        delete=generate_icon(PresetIconNames.delete, "red"),
        delete_inverted=generate_icon(PresetIconNames.delete, bg_color),
        edit=generate_icon(PresetIconNames.edit, "#0F84FF"),
        edit_inverted=generate_icon(PresetIconNames.edit, bg_color),
    )


def get_app_icon() -> QIcon:
    default_color = get_font_color()
    return generate_icon(PresetIconNames.clock, default_color)
