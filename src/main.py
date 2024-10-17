import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
import locale

# Устанавливаем локаль для правильного распознавания русских месяцев
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

# Словарь для перевода русских месяцев в числовой формат
months = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def get_contract_dates(contract_root):
    # Извлекаем даты из статьи 3 контракта
    article_3 = contract_root.find(".//Article[@title='Статья 3 Сроки выполнения работ']")
    if article_3 is not None:
        subarticles = article_3.findall(".//Subarticle")
        for subarticle in subarticles:
            title = subarticle.attrib.get("title", "")
            if "3.1" in title:
                dates = subarticle.findall(".//Date")
                if dates:
                    try:
                        start_date = datetime.strptime(dates[0].text, "%d.%m.%Y")
                        end_date = datetime.strptime(dates[1].text.split(" по ")[1], "%d.%m.%Y")
                        print(f"Даты (сроки) оказания услуг:{start_date}, Дата окончания: {end_date}")
                        return start_date, end_date
                    except Exception as e:
                        print(f"Ошибка при разборе дат в статье 3: {e}")
                else:
                    print("Не удалось найти даты в статье 3")
        print("Не удалось найти подпункт 3.1 в статье 3")
    else:
        print("Не удалось найти статью 3")
    return None, None

def get_submission_deadline(contract_root):
    # Извлекаем срок предоставления отчетных документов из статьи 4 контракта
    article_4 = contract_root.find(".//Article[@title='Статья 4 Порядок сдачи-приемки выполненных работ']")
    if article_4 is not None:
        subarticles = article_4.findall(".//Subarticle")
        for subarticle in subarticles:
            title = subarticle.attrib.get("title", "")
            if "4.1" in title:
                match = re.search(r'не  позднее  (\d+)', title)
                if match:
                    days = int(match.group(1))
                    print(f"Cроки предоставления отчетных документов: {days} дней")
                    return days
                else:
                    print("Не удалось найти число дней в заголовке статьи 4.1")
        print("Не удалось найти подпункт 4.1 в статье 4")
    else:
        print("Не удалось найти статью 4")
    return None

def get_acceptance_dates(acceptance_root):
    # Извлекаем даты из документа о приемке
    dates = []
    date_of_delivery = acceptance_root.find(".//Датаотгрузки")
    if date_of_delivery is not None:
        date_of_delivery_text = date_of_delivery.text
        print(f"Дата отгрузки: {date_of_delivery_text}")
    else:
        print("Дата отгрузки не найдена в документе о приемке")
        return dates

    signatures_root = acceptance_root.find(".//Подписи")
    if signatures_root is not None:
        for signature_tag in ["Подпись1", "Подпись2"]:
            signature = signatures_root.find(f".//{signature_tag}")
            if signature is not None:
                date_of_signature = signature.find(f".//Датаподписи{signature_tag[-1]}")
                if date_of_signature is not None:
                    try:
                        date_of_signature_text = date_of_signature.text
                        print(f"Дата подписи: {date_of_signature_text}")
                        # Очищаем строку даты от лишних символов
                        date_of_delivery_text_clean = date_of_delivery_text.replace(" г.", "")
                        # Заменяем название месяца на числовое значение
                        for month_name, month_num in months.items():
                            date_of_delivery_text_clean = date_of_delivery_text_clean.replace(month_name, month_num)
                        # Разбираем дату
                        date_of_delivery_parsed = datetime.strptime(date_of_delivery_text_clean, "%d %m %Y")
                        date_of_signature_parsed = datetime.strptime(date_of_signature_text, "%d.%m.%Y")
                        dates.append((date_of_delivery_parsed, date_of_signature_parsed))
                    except Exception as e:
                        print(f"Ошибка при разборе дат в документе о приемке: {e}")
                else:
                    print(f"Дата подписи не найдена в элементе {signature_tag}")
            else:
                print(f"Элемент {signature_tag} не найден в документе о приемке")
    else:
        print("Не удалось найти корневой элемент <Подписи> в документе о приемке")
    return dates

def check_dates(contract_dates, submission_deadline, acceptance_dates):
    start_date, end_date = contract_dates
    results = []
    for date_of_delivery, date_of_signature in acceptance_dates:
        expected_submission_date = date_of_delivery + timedelta(days=submission_deadline)
        if date_of_signature <= expected_submission_date:
            results.append((date_of_delivery, date_of_signature, "В срок"))
        else:
            results.append((date_of_delivery, date_of_signature, "Просрочено"))
    return results

if __name__ == "__main__":
    contract_path = "PdfMultiplyParser/docs/example-1/contract_6215618.xml"
    acceptance_path = "PdfMultiplyParser/docs/example-1/UPD-589.xml"
    
    contract_root = parse_xml(contract_path)
    acceptance_root = parse_xml(acceptance_path)

    contract_dates = get_contract_dates(contract_root)
    submission_deadline = get_submission_deadline(contract_root)
    acceptance_dates = get_acceptance_dates(acceptance_root)

    if contract_dates and submission_deadline and acceptance_dates:
        results = check_dates(contract_dates, submission_deadline, acceptance_dates)
        for result in results:
            print(f"Дата отгрузки: {result[0].strftime('%d.%m.%Y')}, Дата подписи: {result[1].strftime('%d.%m.%Y')}, Статус: {result[2]}")
    else:
        print("Не удалось извлечь все необходимые данные для проверки.")
        if not contract_dates:
            print("Проблема с извлечением дат из контракта.")
        if not submission_deadline:
            print("Проблема с извлечением срока предоставления отчетных документов.")
        if not acceptance_dates:
            print("Проблема с извлечением дат из документа о приемке.")