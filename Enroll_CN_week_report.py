"""
Скрипт автоматизации отчета о количестве лидов по
заданному списку Close-фильтров в json-формате.
Рабочая задача в рамках проекта Enroll CN.
"""
import os

import functions as f
import pandas as pd
from datetime import datetime as dt
import json
import time
import color_prints as p
from tg_logger import logger


def main():
    """Основная функция скрипта"""
    try:
        # Название Google таблицы
        spreadsheet_name = 'Rubrain - Enroll CN'

        # Получаем список json-фильтров из гугл-таблицы
        reg_filters = f.get_sheet_range(
            spread=spreadsheet_name,
            income_sheet='WeekReport',
            income_range='A2:C'
        )

        # Создаем DataFrame из полученных данных
        columns = ['email', 'url', 'filters_json']
        reg_df = pd.DataFrame(reg_filters[1:], columns=columns)
        reg_dict = reg_df.to_dict(orient='records')  # преобразуем DF в список словарей

        # Подготавливаем заголовки отчета и определяем текущее время
        report = [['timestamp', 'url', 'email', 'total_leads', 'errors']]
        current_time = dt.now().strftime('%Y/%m/%d, %H:%M:%S')

        # Обрабатываем каждый json-фильтр из реестра
        for row in reg_dict:
            filter_value = row['filters_json']

            # Пропускаем пустые фильтры
            if not filter_value:
                continue

            # Формируем запрос для API Close
            query = json.loads(row['filters_json'])
            query['include_counts'] = True
            error_message = ''

            try:
                # Выполняем запрос к API для получения количества лидов
                total_leads = f.api.post('data/search/', data=query)['count']['total']
                p.print_success(f'Найдено лидов: {total_leads} для {row["url"]}')

            except Exception as e:
                # Обрабатываем ошибки при запросе к API
                p.print_error(f'Ошибка при обработке {row["url"]}: {e}')
                error_message = str(e)
                total_leads = f'error\n{error_message}'

            # Формируем строку отчета
            report_row = [current_time, row['url'], row['email'], total_leads, error_message]
            report.append(report_row)

        # Записываем отчет в Google таблицу
        f.add_report_to_sheet(
            spread=spreadsheet_name,
            sheet='py_weekReport',
            report=report[1:]
        )
        p.print_success('Отчет успешно записан в таблицу')
        return True

    except Exception as e:
        p.print_error(f"Критическая ошибка в основной функции: {e}")
        return False


def run_with_restart():
    """
    Запускает скрипт с автоматическим перезапуском при ошибках
    """
    max_attempts = 10  # Максимальное количество попыток
    attempt = 1
    restart_delay = 300  # 5 минут в секундах

    logger.info(f"✅ {current_file} Запуск скрипта...")

    while attempt <= max_attempts:
        p.print_info(f"Попытка #{attempt} - {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            success = main()

            if success:
                p.print_success(f"Скрипт успешно завершен!")
                break
            else:
                p.print_warning(f"Скрипт завершился с ошибкой, готовим перезапуск...")

        except KeyboardInterrupt:
            p.print_info("Скрипт остановлен пользователем")
            break
        except Exception as e:
            p.print_warning(f"Неожиданная ошибка: {e} \nГотовим перезапуск...")

        # Если это не последняя попытка, ждем перед перезапуском
        if attempt < max_attempts:
            p.print_info(f"Ожидание {restart_delay//60} минут перед следующей попыткой...")
            for i in range(restart_delay, 0, -60):
                if i % 300 == 0 or i <= 60:  # Выводим каждые 5 минут или последнюю минуту
                    p.print_info(f"До перезапуска: {i//60} мин {i%60} сек")
                time.sleep(min(60, i))  # Спим не более 60 секунд за раз

            logger.info(f"{current_file} Перезапуск скрипта...")

        attempt += 1

    if attempt > max_attempts:
        logger.critical(f"❌ {current_file} Достигнуто максимальное количество попыток. Скрипт остановлен.")
    else:
        logger.success(f"✅ {current_file} Скрипт завершил работу после {attempt} попытки(ок)")


if __name__ == '__main__':
    current_file = os.path.basename(__file__)
    run_with_restart()