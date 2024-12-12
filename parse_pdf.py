import fitz  # PyMuPDF
import re
from datetime import datetime, timedelta

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def find_section(text, start_pattern, end_pattern):
    pattern = re.compile(rf'({start_pattern}.*?){end_pattern}', re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(0)
    return None

def find_dates_in_section(section):
    date_pattern = re.compile(r'\b\d{2}\.\d{2}\.\d{4}\b')
    dates = date_pattern.findall(section)
    if len(dates) >= 2:
        return dates[:2]
    return None

def parse_pdf(pdf_path):
    start_pattern = '3\\.1'
    end_pattern = '\\n\\s*\\n'
    extracted_text = extract_text_from_pdf(pdf_path)
    section = find_section(extracted_text, start_pattern, end_pattern)
    if section:
        dates = find_dates_in_section(section)
        if dates:
            return dates
    return None

def find_shipping_date(text):
    pattern = re.compile(r'Дата отгрузки \(сдачи\)\s*\n\s*(\d{2}\s+[А-Яа-я]+\s+\d{4}\s+г\.)')
    match = pattern.search(text)
    if match:
        date_str = match.group(1)
        return convert_date_to_dd_mm_yyyy(date_str)
    return None

def find_signed_date(text):
    pattern = re.compile(r'ДОКУМЕНТ ПОДПИСАН\nЭЛЕКТРОННОЙ ПОДПИСЬЮ\nДОКУМЕНТ ПОДПИСАН\nЭЛЕКТРОННОЙ ПОДПИСЬЮ\n\s*(\d{2}\.\d{2}\.\d{4})')
    match = pattern.search(text)
    if match:
        return match.group(1)
    return None

def convert_date_to_dd_mm_yyyy(date_str):
    months = {
        "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
        "мая": "05", "июня": "06", "июля": "07", "августа": "08",
        "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"
    }
    parts = date_str.split()
    if len(parts) != 4:
        raise ValueError(f"Неправильный формат даты: {date_str}")
    day, month, year, _ = parts
    return f"{day.zfill(2)}.{months[month]}.{year[:4]}"

def find_article_4_number(text):
    section = find_section(text, '4\\.1', '\\n\\s*\\n')
    if section:
        section = section.replace('4.1', '', 1)  # Убираем '4.1' один раз из начала
        match = re.search(r'\b(\d+)\b', section)
        if match:
            return int(match.group(1))  # Преобразуем в число
    return None

def parse_additional_pdfs(additional_pdf_paths):
    all_dates = []
    for path in additional_pdf_paths:
        text = extract_text_from_pdf(path)
        
        shipping_date = find_shipping_date(text)
        if shipping_date:
            all_dates.append(shipping_date)
        
        signed_date = find_signed_date(text)
        if signed_date:
            all_dates.append(signed_date)
    
    return all_dates

def add_business_days(start_date, num_days):
    current_date = start_date
    while num_days > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Понедельник-пятница
            num_days -= 1
    return current_date

def parse_multiple_pdfs(main_pdf_path, additional_pdf_paths):
    main_dates = parse_pdf(main_pdf_path)
    additional_dates = parse_additional_pdfs(additional_pdf_paths)
    article_4_number = find_article_4_number(extract_text_from_pdf(main_pdf_path))
    return main_dates, additional_dates, article_4_number
