import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re
import locale
import os
from PDFparser import process_pdf as process_contract_pdf
from UPD_PDFparser import process_pdf as process_upd_pdf
from WordParser import parse_dates_from_word
import subprocess

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

def get_contract_dates(contract_root, word_doc_path):
    # Извлекаем даты из статьи 3 контракта
    article_3 = contract_root.find(".//Article[@title='Статья 3 Сроки выполнения работ']" or ".//Article[@title='Статья 3 Сроки оказания услуг']")
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
    else:
        print("Не удалось найти статью 3")
    
    # Вызов WordParser, если не удалось найти даты в статье 3
    word_dates = parse_dates_from_word(word_doc_path)
    if word_dates:
        print(f"Даты из Word-документа: {word_dates}")
        return word_dates
    return None, None

def get_submission_deadline(contract_root):
    # Извлекаем срок предоставления отчетных документов из статьи 4 контракта
    article_4 = contract_root.find(".//Article[@title='Статья 4 Порядок сдачи-приемки оказанных услуг']")
    if article_4 is None:
        article_4 = contract_root.find(".//Article[@title='Статья 4 Порядок сдачи-приемки выполненных работ']")
    
    if article_4 is not None:
        subarticles = article_4.findall(".//Subarticle")
        for i, subarticle in enumerate(subarticles):
            title = subarticle.attrib.get("title", "")
            if "4.1" in title or "4.2" in title:
                # Объединяем заголовки, если они разделены
                full_title = title
                for next_subarticle in subarticles[i+1:]:
                    next_title = next_subarticle.attrib.get("title", "")
                    if next_title.startswith("4.3"):
                        break
                    full_title += " " + next_title
                
                match = re.search(r'не позднее (\d+)', full_title)
                if match:
                    days = int(match.group(1))
                    print(f"Cроки предоставления отчетных документов: {days} дней")
                    return days
                else:
                    print(f"Не удалось найти число дней в заголовке статьи {title.split()[0]}")
        print("Не удалось найти подпункт 4.1 или 4.2 в статье 4")
    else:
        print("Не удалось найти статью 4")
        print(contract_root)
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
                date_of_signature = signature.find(f".//Датаподписи")
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

def main():
    if len(sys.argv) < 4:
        print("Usage: python main.py <contract_pdf_path> <word_doc_path> <upd_files>")
        sys.exit(1)

    contract_pdf_path = sys.argv[1]
    word_doc_path = sys.argv[2]
    upd_files = sys.argv[3:]

    # Создаем XML файл для контракта
    contract_xml_path = os.path.splitext(contract_pdf_path)[0] + ".xml"
    print("Обработка контрактного PDF...")
    process_contract_pdf(contract_pdf_path, contract_xml_path)

    for upd_file in upd_files:
        # Определяем тип файла (PDF или HTML)
        if upd_file.lower().endswith('.pdf'):
            # Создаем XML файл для каждого UPD PDF
            upd_xml_path = os.path.splitext(upd_file)[0] + ".xml"
            print(f"Обработка UPD PDF: {upd_file}...")
            process_upd_pdf(upd_file, upd_xml_path)
        elif upd_file.lower().endswith('.html'):
            # Обрабатываем HTML файл и создаем XML
            print(f"Обработка UPD HTML: {upd_file}...")
            subprocess.run(["python", "src/HTMLparser.py", upd_file], check=True)
            upd_xml_path = os.path.splitext(upd_file)[0] + ".xml"
        else:
            print(f"Неизвестный формат файла: {upd_file}")
            continue

        print("Проверка дат...")
        contract_root = parse_xml(contract_xml_path)
        acceptance_root = parse_xml(upd_xml_path)

        print("Извлечение дат...")
        contract_dates = get_contract_dates(contract_root, word_doc_path)
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

if __name__ == "__main__":
    main()