import fitz  # PyMuPDF
import re
import xml.etree.ElementTree as ET

def extract_headings(pdf_path):
    # Открываем PDF-документ
    document = fitz.open(pdf_path)
    headings = []
    current_article = None

    # Регулярные выражения для поиска подзаголовков
    subarticle_pattern = re.compile(r'^\d+(\.\d+)*\s+.+$')
    number_pattern = re.compile(r'^\d+(\.\d+)*$')

    # Проходим по всем страницам
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        font_size = span["size"]

                        # Ищем заголовки, начинающиеся со слова "Статья" и имеющие больший размер шрифта
                        if text.startswith("Статья") and font_size > 10:  # Предположим, что обычный текст имеет размер шрифта <= 10
                            current_article = {"title": text, "subarticles": [], "dates": [], "text": ""}  # Создаем новую статью с пустым списком подстатей и текстом
                            headings.append(current_article)
                        # Ищем подзаголовки, соответствующие определенной структуре
                        elif subarticle_pattern.match(text):
                            if current_article:
                                current_article["subarticles"].append({"title": text, "dates": [], "text": ""})  # Добавляем подстатью к текущей статье
                        # Проверяем, является ли текст числом, чтобы объединить его с предыдущим заголовком
                        elif number_pattern.match(text):
                            if current_article and current_article["subarticles"]:
                                current_article["subarticles"][-1]["title"] += " " + text
                        # Добавляем текст к текущей статье или подстатье
                        elif current_article:
                            if current_article["subarticles"]:
                                current_article["subarticles"][-1]["text"] += " " + text
                            else:
                                current_article["text"] += " " + text

    # Проверяем, что после подзаголовка идет нужное число
    for article in headings:
        for i in range(len(article["subarticles"]) - 1):
            current_subarticle = article["subarticles"][i]["title"].split()[0]
            next_subarticle = article["subarticles"][i + 1]["title"].split()[0]
            if current_subarticle.count('.') == next_subarticle.count('.') and int(next_subarticle.split('.')[-1]) != int(current_subarticle.split('.')[-1]) + 1:
                print(f"Ошибка: после подзаголовка {current_subarticle} идет {next_subarticle}, а должно идти {current_subarticle.split('.')[0]}.{int(current_subarticle.split('.')[-1]) + 1}")

    return headings

def extract_dates(pdf_path, headings):
    # Открываем PDF-документ
    document = fitz.open(pdf_path)

    # Регулярные выражения для поиска дат
    date_patterns = [
        re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](\d{4})\b'),  # Формат даты: ДД.ММ.ГГГГ, ДД/ММ/ГГГГ, ДД-ММ-ГГГГ
        re.compile(r'\b(0?[1-9]|[12][0-9]|3[01]) (янв(?:аря)?|фев(?:раля)?|мар(?:та)?|апр(?:еля)?|мая|июн(?:я)?|июл(?:я)?|авг(?:уста)?|сен(?:тября)?|окт(?:ября)?|ноя(?:бря)?|дек(?:абря)?) (\д{4}) года\b', re.IGNORECASE),  # Формат даты: ДД месяц ГГГГ года
        re.compile(r'\bс (0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](\д{4}) по (0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](\д{4})\b', re.IGNORECASE)  # Формат диапазона дат: с ДД.ММ.ГГГГ по ДД.ММ.ГГГГ
    ]

    # Проходим по всем страницам и ищем даты
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()

                        # Ищем даты
                        for date_pattern in date_patterns:
                            match = date_pattern.search(text)
                            if match:
                                date_text = match.group()

                                # Проверяем, к какой статье или подстатье относится дата
                                for article in headings:
                                    added = False
                                    for subarticle in article["subarticles"]:
                                        if date_text in subarticle["text"]:
                                            if date_text not in subarticle["dates"]:
                                                subarticle["dates"].append(date_text)
                                            added = True
                                            break
                                    if not added:
                                        if date_text in article["text"]:
                                            if date_text not in article["dates"]:
                                                article["dates"].append(date_text)

    return headings

def save_to_xml(headings, xml_path):
    root = ET.Element("Document")

    for article in headings:
        article_element = ET.SubElement(root, "Article", title=article["title"])
        article_text_element = ET.SubElement(article_element, "Text")
        article_text_element.text = article["text"]
        for subarticle in article["subarticles"]:
            subarticle_element = ET.SubElement(article_element, "Subarticle", title=subarticle["title"])
            subarticle_text_element = ET.SubElement(subarticle_element, "Text")
            subarticle_text_element.text = subarticle["text"]
            for date in subarticle["dates"]:
                ET.SubElement(subarticle_element, "Date").text = date
        for date in article["dates"]:
            ET.SubElement(article_element, "Date").text = date

    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

def process_pdf(pdf_path, xml_path):
    headings = extract_headings(pdf_path)
    headings_with_dates = extract_dates(pdf_path, headings)
    save_to_xml(headings_with_dates, xml_path)
    print(f"XML файл сохранен по пути: {xml_path}")

    # Выводим найденные заголовки, подзаголовки и даты
    #Диагностика
    # for article in headings_with_dates:
    #     print(f"Article: {article['title']}")
    #     for subarticle in article["subarticles"]:
    #         print(f"  Subarticle: {subarticle['title']}")
    #         for date in subarticle["dates"]:
    #             print(f"    Date: {date}")
    #     for date in article["dates"]:
    #         print(f"  Date: {date}")