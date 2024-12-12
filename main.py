import parse_pdf
import parse_docx
from datetime import datetime

def main():
    # Ввод пути к основному PDF файлу
    main_pdf_path = 'docs\example-2\contract_6910851.pdf'

    # Ввод путей к дополнительным PDF файлам для поиска даты отгрузки и даты подписания
    additional_pdf_paths = [
        'docs\\example-1\\UPD-589.pdf',
        'docs\\example-1\\UPD-602.pdf'
    ]

    # Ввод пути к DOCX файлу
    docx_path = 'docs\\example-2\\ПТЗ 178_2023.docx'

    # Ввод путей к HTML файлам
    html_paths = [
        'docs\\example-2\\UPD-13.html',
        'docs\\example-2\\UPD-23.html'
    ]

    # Парсинг основного и дополнительных PDF файлов
    main_dates, additional_dates, article_4_number = parse_pdf.parse_multiple_pdfs(main_pdf_path, additional_pdf_paths)
    if main_dates and len(additional_dates) == 4:
        print(f"Сроки выполнения работ: с {main_dates[0]} по {main_dates[1]}")
        print(f"Дата отгрузки (сдачи) по первому документу: {additional_dates[0]}")
        print(f"Дата подписания первого документа: {additional_dates[1]}")
        print(f"Дата отгрузки (сдачи) по второму документу: {additional_dates[2]}")
        print(f"Дата подписания второго документа: {additional_dates[3]}")
        if article_4_number:
            print(f"Срок предоставления комплекта отчетной документации: {article_4_number} рабочих дней")

            # Расчет срока предоставления комплекта отчетной документации
            shipping_dates = [additional_dates[0], additional_dates[2]]
            for index, shipping_date in enumerate(shipping_dates):
                shipping_date_dt = datetime.strptime(shipping_date, '%d.%m.%Y')
                deadline_date_dt = parse_pdf.add_business_days(shipping_date_dt, article_4_number)
                deadline_date_str = deadline_date_dt.strftime('%d.%m.%Y')
                print(f"Окончательный срок для документа {index + 1}: {deadline_date_str}")

                signed_date = additional_dates[1] if index == 0 else additional_dates[3]
                signed_date_dt = datetime.strptime(signed_date, '%d.%m.%Y')
                if signed_date_dt <= deadline_date_dt:
                    print(f"Дата подписания документа {index + 1} удовлетворяет сроку предоставления комплекта отчетной документации")
                else:
                    print(f"Дата подписания документа {index + 1} не удовлетворяет сроку предоставления комплекта отчетной документации")
    else:
        print("Даты не найдены в PDF. Открытие .docx для поиска...")

        # Парсинг DOCX и PDF файлов
        dates_from_docx, payment_period, article_4_number = parse_docx.parse_docx_and_pdf(docx_path, main_pdf_path)
        if dates_from_docx:
            if len(dates_from_docx) == 2:
                print(f"Сроки выполнения работ: с {dates_from_docx[0]} по {dates_from_docx[1]}")
                if payment_period:
                    print(f"Период оплаты: {', '.join(payment_period)}")
                if article_4_number:
                    print(f"Срок предоставления комплекта отчетной документации: {article_4_number} рабочих дней")

                    # Парсинг HTML файлов и расчет срока предоставления комплекта отчетной документации
                    html_dates = parse_docx.parse_multiple_html(html_paths)
                    if html_dates:
                        print(f"Дата подписания первого документа: {html_dates[0]}")
                        print(f"Дата подписания второго документа: {html_dates[1]}")
                        deadline_dates = parse_docx.calculate_deadline_dates(article_4_number, html_dates)
                        print(f"Расчетные даты дедлайнов: {deadline_dates}")

                        for i, html_date in enumerate(html_dates):
                            html_date_dt = datetime.strptime(html_date, '%d.%m.%Y')
                            deadline_date_dt = datetime.strptime(deadline_dates[i], '%d.%m.%Y')
                            if html_date_dt <= deadline_date_dt:
                                print(f"Дата подписания {html_date} удовлетворяет дедлайну {deadline_dates[i]}")
                            else:
                                print(f"Дата подписания {html_date} НЕ удовлетворяет дедлайну {deadline_dates[i]}")
            elif len(dates_from_docx) == 1:
                print(f"Сроки выполнения работ: {dates_from_docx[0]}")
                if article_4_number:
                    print(f"Срок предоставления комплекта отчетной документации: {article_4_number} рабочих дней")
            else:
                print("Не удалось найти даты в таблице DOCX.")
        else:
            print("Не удалось найти даты в DOCX документе.")

if __name__ == "__main__":
    main()
