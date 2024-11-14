from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys
import os

def extract_text_from_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    return soup

def extract_dates_and_signatures(soup):
    extracted_data = {}

    # Извлекаем информацию о электронной подписи
    signatures = []
    signature_elements = soup.find_all('td', class_='stampTd')
    for i in range(0, len(signature_elements), 4):
        date_element = signature_elements[i + 3].find('b')
        if date_element:
            date_text = date_element.text.strip()
            time_text = signature_elements[i + 3].contents[2].strip() if len(signature_elements[i + 3].contents) > 2 else ""
            signature_info = {
                "Датаподписи": date_text,
                "Времяподписи": time_text,
            }
            signatures.append(signature_info)

    if signatures:
        extracted_data["Электронные подписи"] = signatures
    else:
        print("Не найдено электронных подписей.")

    return extracted_data

def save_to_xml(extracted_data, xml_path):
    root = ET.Element("Document")

    # Подписи
    signatures = ET.SubElement(root, "Подписи")
    for idx, signature in enumerate(extracted_data.get("Электронные подписи", []), start=1):
        signature_element = ET.SubElement(signatures, f"Подпись{idx}")
        date_signing = ET.SubElement(signature_element, f"Датаподписи")
        date_signing.text = signature["Датаподписи"]
        time_signing = ET.SubElement(signature_element, f"Времяподписи")
        time_signing.text = signature["Времяподписи"]

    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

def process_html(html_path):
    xml_path = os.path.splitext(html_path)[0] + ".xml"
    soup = extract_text_from_html(html_path)
    extracted_data = extract_dates_and_signatures(soup)
    save_to_xml(extracted_data, xml_path)
    print(f"Данные сохранены в {xml_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python HTMLparser.py <html_path>")
        sys.exit(1)

    html_path = sys.argv[1]
    process_html(html_path)