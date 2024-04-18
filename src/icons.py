from dataclasses import dataclass
import qtawesome as qta
from PyQt5.QtGui import QIcon

from src.utils import get_icon_color


@dataclass
class PresetIconNames:
    start = "fa5s.play"
    stop = "fa5.pause-circle"
    exit = "fa.close"
    stats = "fa5s.chart-line"
    table = "fa5s.table"
    setting = "fa.gears"
    clock = "fa5.clock"


@dataclass
class PresetIcon:
    start: QIcon
    stop: QIcon
    exit: QIcon
    stats: QIcon
    table: QIcon
    setting: QIcon
    clock: QIcon


def generate_icon(icon_name: str, color: str = "white") -> QIcon:
    return qta.icon(icon_name, color=color)


def get_preset_icons() -> PresetIcon:
    default_color = get_icon_color()
    return PresetIcon(
        start=generate_icon(PresetIconNames.start, "green"),
        stop=generate_icon(PresetIconNames.stop, "orange"),
        exit=generate_icon(PresetIconNames.exit, "red"),
        stats=generate_icon(PresetIconNames.stats, "#0F84FF"),
        table=generate_icon(PresetIconNames.table, default_color),
        setting=generate_icon(PresetIconNames.setting, "gray"),
        clock=generate_icon(PresetIconNames.clock, default_color),
    )
