import os
from closeio_api import Client
import gspread
from gspread.utils import rowcol_to_a1
from dotenv import load_dotenv
load_dotenv()


SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
api = Client(os.getenv('CLOSE_API_KEY_MARY'))


def get_sheet_range(spread, income_sheet, income_range):
    """Получает из гугл-таблицы диапазон"""
    sh = gc.open(spread)
    data = sh.worksheet(income_sheet).get(income_range)
    return data


def add_report_to_sheet(spread, sheet, report):
    """
    Добавляет на лист данные отчета без удаления уже существующих там записей
    :param spread: гугл таблица (название)
    :param sheet: название листа
    :param report: отчет в виде списка списков
    :return: None
    """
    sh = gc.open(spread)
    worksheet = sh.worksheet(sheet)

    # Получить размеры отчета (количество строк и столбцов)
    num_rows = len(report)
    num_cols = len(report[0])

    # Получить диапазон для записи данных
    q_rows = len(worksheet.get_all_values())  # узнаем кол-во уже заполненных на листе строк

    start_cell = rowcol_to_a1(q_rows + 1, 1)
    end_cell = rowcol_to_a1(q_rows + num_rows, num_cols)

    # Записать значения в диапазон
    cell_range = f"{start_cell}:{end_cell}"
    worksheet.update(cell_range, report, value_input_option="USER_ENTERED")

    print("Отчет добавлен")
