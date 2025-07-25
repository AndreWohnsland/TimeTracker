import datetime
import logging
from pathlib import Path

import pandas as pd
import xlsxwriter
import xlsxwriter.format
from xlsxwriter.exceptions import XlsxWriterException

from src.config_handler import CONFIG_HANDLER
from src.filepath import REPORTS_PATH

logger = logging.getLogger(__name__)


class DataExporter:
    def export_data(self, df: pd.DataFrame, report_date: datetime.date, overtime_report: bool = True) -> str:
        if df.empty:
            message = "No data to export, will no generate file..."
            logger.warning(message)
            return message
        file_suffix = "time"
        if overtime_report:
            file_suffix = "overtime"
        file_name = f"{CONFIG_HANDLER.config.name.replace(' ', '_')}_{df.index[0].strftime('%m_%Y')}_{file_suffix}.xlsx"
        config_save_path = CONFIG_HANDLER.config.save_path
        save_path = REPORTS_PATH if not config_save_path else Path(config_save_path)
        file_path = save_path / file_name
        try:
            workbook = xlsxwriter.Workbook(file_path)
            bold = workbook.add_format({"bold": True})
            color = workbook.add_format({"bg_color": "#00CC00", "align": "center"})
            worksheet = workbook.add_worksheet()
            cell_width = 20
            worksheet.set_column("A:F", cell_width)  # Extended to column F for new columns
            self._write_information(worksheet, df, bold, color, overtime_report)
            self._write_times(worksheet, df, color, overtime_report)
            workbook.close()
            return f"File saved at: {file_path}"
        except XlsxWriterException:
            message = f"Could not open Workbook: {file_name}, is it still opened?"
            logger.error(message)
            return message

    def _round_quarterly(self, number: float) -> float:
        return round(number * 4) / 4

    def _write_information(
        self,
        worksheet: xlsxwriter.Workbook.worksheet_class,
        df: pd.DataFrame,
        bold: xlsxwriter.format.Format,
        color: xlsxwriter.format.Format,
        overtime_report: bool,
    ) -> None:
        worksheet.write("A1", "Name:", bold)
        worksheet.write("B1", CONFIG_HANDLER.config.name, color)
        worksheet.write("A3", "Month:", bold)
        worksheet.write("B3", df.index[0].strftime("%B"), color)
        worksheet.write("A4", "Year", bold)
        worksheet.write("B4", df.index[0].year, color)
        worksheet.write("A6", "Day:")
        if overtime_report:
            worksheet.write("B6", "Over 8 h")
        else:
            worksheet.write("B6", "Work Time")
        worksheet.write("C6", "Start Time")
        worksheet.write("D6", "End Time")
        worksheet.write("E6", "Break Time")
        worksheet.write("F6", "Total Time")

    def _write_times(
        self,
        worksheet: xlsxwriter.Workbook.worksheet_class,
        df: pd.DataFrame,
        color: xlsxwriter.format.Format,
        overtime_report: bool,
    ) -> None:
        time_to_subtract = 0.0
        if overtime_report:
            time_to_subtract = CONFIG_HANDLER.config.daily_hours
        for i, (index, row) in enumerate(df.iterrows()):
            worksheet.write(f"A{7 + i}", index.strftime("%d.%m.%Y"))  # type: ignore
            _time = self._round_quarterly(max(row["work"] - time_to_subtract, 0))
            worksheet.write(f"B{7 + i}", _time, color)

            # Add start time
            start_time = row.get("start_time")
            if start_time and not pd.isna(start_time):
                worksheet.write(f"C{7 + i}", start_time.strftime("%H:%M"), color)
            else:
                worksheet.write(f"C{7 + i}", "-", color)

            # Add end time
            end_time = row.get("end_time")
            if end_time and not pd.isna(end_time):
                worksheet.write(f"D{7 + i}", end_time.strftime("%H:%M"), color)
            else:
                worksheet.write(f"D{7 + i}", "-", color)

            # Add break time
            break_time = row.get("break_time", 0)
            if break_time and not pd.isna(break_time):
                worksheet.write(f"E{7 + i}", self._round_quarterly(break_time), color)
            else:
                worksheet.write(f"E{7 + i}", 0, color)

            # Add total time (work + break)
            total_time = row.get("work_time", 0)
            if total_time and not pd.isna(total_time):
                worksheet.write(f"F{7 + i}", self._round_quarterly(total_time), color)
            else:
                worksheet.write(f"F{7 + i}", 0, color)


EXPORTER = DataExporter()
