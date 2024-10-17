import re
pdf_path = "/Users/sl4sh73r/Documents/added/PdfMultiplyParser/docs/example-2/contract_6910851.pdf"

text = "5 Aпреля 2013"

date_patterns = [
    re.compile(r'\b(0?[1-9]|[12][0-9]|3[01])[-\/\.](0?[1-9]|1[012])[-\/\.](\d{4})\b'),
    re.compile(
        r'\b(0?[1-9]|[12][0-9]|3[01])\s+(?:[AaаА]пр(?:\w*)?|[ЯяYy][нН](?:в(?:\w*)?|е(?:в(?:\w*)?)?)|ф(?:ев(?:\w*)?|Е(?:в(?:\w*)?)?)|ма(?:р(?:\w*)?|Я(?:р(?:\w*)?)?)|ию(?:н(?:\w*)?|л(?:\w*)?)|авг(?:\w*)?|сен(?:\w*)?|окт(?:\w*)?|ноя(?:\w*)?|дек(?:\w*)?)\s+(\d{4})(?:\s+года)?\b',
        re.IGNORECASE
    )
]

for pattern in date_patterns:
    match = pattern.search(text)
    if match:
        print(f"Найдена дата: {match.group()}")
