import datetime
import os
import xlsxwriter
import pandas as pd
import xlsxwriter.format

from src.config_handler import ConfigHandler, Config


class DataExporter:
    def __init__(self):
        dirpath = os.path.dirname(__file__)
        self.default_save_path = os.path.join(dirpath, "..", "reports")
        self.config_handler = ConfigHandler()
        self.work_time = 8

    def export_data(self, df: pd.DataFrame, report_date: datetime.date, overtime_report: bool = True):
        if df.empty:
            message = "No data to export, will no generate file..."
            print(message)
            return False, message
        config = self.config_handler.get_config()
        file_suffix = "time"
        if overtime_report:
            file_suffix = "overtime"
        file_name = f"{config.name.replace(' ', '_')}_{df.index[0].strftime('%m_%Y')}_{file_suffix}.xlsx"
        save_path = config.save_path
        if not save_path:
            save_path = self.default_save_path
        file_path = os.path.join(save_path, file_name)
        try:
            workbook = xlsxwriter.Workbook(file_path)
            bold = workbook.add_format({"bold": True})
            color = workbook.add_format({"bg_color": "#00CC00", "align": "center"})
            worksheet = workbook.add_worksheet()
            cell_width = 20
            worksheet.set_column("A:B", cell_width)
            self.write_person_information(worksheet, df, config, bold, color, overtime_report)
            self.write_times(worksheet, df, color, overtime_report)
            workbook.close()
            return True, file_path
        except:
            message = f"Could not open Workbook: {file_name}, is it still opened?"
            print(message)
            return False, message

    def round_quarterly(self, number):
        return round(number * 4) / 4

    def write_person_information(
        self,
        worksheet: xlsxwriter.Workbook.worksheet_class,
        df: pd.DataFrame,
        config: Config,
        bold: xlsxwriter.format.Format,
        color: xlsxwriter.format.Format,
        overtime_report: bool,
    ):
        worksheet.write("A1", "Name:", bold)
        worksheet.write("B1", config.name, color)
        worksheet.write("A3", "Monat:", bold)
        worksheet.write("B3", df.index[0].strftime("%B"), color)
        worksheet.write("A4", "Jahr", bold)
        worksheet.write("B4", df.index[0].year, color)
        worksheet.write("A6", "Tag:")
        if overtime_report:
            worksheet.write("B6", "Über 8 h")
        else:
            worksheet.write("B6", "Arbeitszeit")

    def write_times(
        self,
        worksheet: xlsxwriter.Workbook.worksheet_class,
        df: pd.DataFrame,
        color: xlsxwriter.format.Format,
        overtime_report: bool,
    ):
        time_to_subtract = 0
        if overtime_report:
            time_to_subtract = self.work_time
        for i, (index, row) in enumerate(df.iterrows()):
            worksheet.write(f"A{7+i}", index.strftime("%d.%m.%Y"))  # type: ignore
            if index.weekday() < 5:  # type: ignore
                _time = self.round_quarterly(max(row["final_time"] - time_to_subtract, 0))
                worksheet.write(f"B{7+i}", _time, color)


EXPORTER = DataExporter()
