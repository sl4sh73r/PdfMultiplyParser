import fitz  # PyMuPDF
import re
import xml.etree.ElementTree as ET

def extract_text_from_pdf(pdf_path):
    # Открываем PDF файл
    document = fitz.open(pdf_path)
    text = ""

    # Проходим по всем страницам и извлекаем текст
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()

    # Удаляем лишние переносы строк
    text = re.sub(r'\n+', '\n', text).strip()
    return text

def extract_dates_and_signatures(text):
    # Регулярные выражения для поиска дат и информации о электронной подписи
    date_patterns = {
        "Счет фактура от": re.compile(r'Счет-фактура\s*№\s*\d+\s*от\s*(\d{1,2} \w+ \d{4} г\.)', re.MULTILINE),
        "Контракт от": re.compile(r'Контракт \(Номер: [^)]+ от (\d{2}\.\d{2}\.\d{4})\)'),
        "Дата отгрузки": re.compile(r'Дата\s*отгрузки\s*\(сдачи\)\s*(\d{1,2}\s*\w+\s*\d{4}\s*г\.)'),
        "Дата Приёмки": re.compile(r'Дата\s*получения\s*\(приемки\)\s*(\d{1,2}\s*\w+\s*\d{4}\s*г\.)'),
    }

    signature_pattern = re.compile(
        r'(\d{2}\.\d{2}\.\d{4})\s*\n'  # Дата подписи
        r'(\d{2}\.\d{2}\.\d{4})\s*\n'  # Дата подписи(2)
        r'\s*Сертификат:\s*\n([0-9A-F ]+)\s*\n'  # Сертификат
        r'\s*Сертификат:\s*\n([0-9A-F ]+)\s*\n',  # Сертификат(2)
        re.IGNORECASE
    )

    extracted_data = {}

    # Извлекаем даты
    for label, pattern in date_patterns.items():
        match = pattern.search(text)
        if match:
            extracted_data[label] = match.group(1)
        else:
            print(f"Не удалось найти: {label}")

    # Извлекаем информацию о электронной подписи
    signatures = []
    for match in signature_pattern.finditer(text):
        signature_info = {
            "Датаподписи": match.group(1),
            "Сертификат": match.group(3).strip(),
            "Датаподписи2": match.group(2),
            "Сертификат2": match.group(4).strip(),
        }
        signatures.append(signature_info)

    if signatures:
        extracted_data["Электронные подписи"] = signatures
    else:
        print("Не найдено электронных подписей.")

    # Поиск дат действительности
    valid_date_pattern = re.compile(r'Действителен:\s*\n(.*?)\n', re.MULTILINE | re.IGNORECASE)
    matches = valid_date_pattern.findall(text)
    unique_valid_dates = set(match.strip() for match in matches)  # Уникальные даты
    if unique_valid_dates:
        extracted_data["Даты действительности"] = list(unique_valid_dates)
    else:
        print("Не найдены даты действительности.")

    return extracted_data

def save_to_xml(extracted_data, xml_path):
    root = ET.Element("Document")

    # Основной документ
    main_doc = ET.SubElement(root, "ОсновнойДокумент")
    for label, data in extracted_data.items():
        if label != "Электронные подписи" and label != "Даты действительности":
            element = ET.SubElement(main_doc, label.replace(" ", ""))
            element.text = data

    # Подписи
    signatures = ET.SubElement(root, "Подписи")
    for idx, signature in enumerate(extracted_data.get("Электронные подписи", []), start=1):
        signature_element = ET.SubElement(signatures, f"Подпись{idx}")
        date_signing = ET.SubElement(signature_element, f"Датаподписи{idx}")
        date_signing.text = signature["Датаподписи"]
        cert = ET.SubElement(signature_element, f"Сертификат{idx}")
        cert.text = signature["Сертификат"]
        
        # Даты действительности
        if idx <= len(extracted_data.get("Даты действительности", [])):
            valid_date = ET.SubElement(signature_element, f"ДатаДействительности{idx}")
            valid_date.text = extracted_data["Даты действительности"][idx - 1]

    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    pdf_path = "docs/example-1/UPD-589.pdf"
    xml_path = "docs/example-1/UPD-589.xml"
    extracted_text = extract_text_from_pdf(pdf_path)
    
    extracted_data = extract_dates_and_signatures(extracted_text)
    
    save_to_xml(extracted_data, xml_path)
    print(f"Данные сохранены в {xml_path}")
