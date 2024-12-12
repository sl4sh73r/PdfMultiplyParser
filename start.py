import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

def run_main(main_pdf_path, docx_path, html_paths, additional_pdf_paths):
    args = [
        "python", "main.py",
        main_pdf_path,
        docx_path,
        ",".join(html_paths),
        ",".join(additional_pdf_paths)
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    messagebox.showinfo("Результат", result.stdout)

def select_file(entry):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def select_files(entry):
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        entry.delete(0, tk.END)
        entry.insert(0, ",".join(file_paths))

def create_gui():
    root = tk.Tk()
    root.title("PDF и DOCX Парсер")

    tk.Label(root, text="Основной PDF файл:").grid(row=0, column=0, padx=10, pady=5)
    main_pdf_entry = tk.Entry(root, width=50)
    main_pdf_entry.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="Выбрать", command=lambda: select_file(main_pdf_entry)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(root, text="DOCX файл:").grid(row=1, column=0, padx=10, pady=5)
    docx_entry = tk.Entry(root, width=50)
    docx_entry.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(root, text="Выбрать", command=lambda: select_file(docx_entry)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(root, text="HTML файлы (через запятую):").grid(row=2, column=0, padx=10, pady=5)
    html_entry = tk.Entry(root, width=50)
    html_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(root, text="Выбрать", command=lambda: select_files(html_entry)).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(root, text="Дополнительные PDF файлы (через запятую):").grid(row=3, column=0, padx=10, pady=5)
    additional_pdf_entry = tk.Entry(root, width=50)
    additional_pdf_entry.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(root, text="Выбрать", command=lambda: select_files(additional_pdf_entry)).grid(row=3, column=2, padx=10, pady=5)

    tk.Button(root, text="Запустить", command=lambda: run_main(
        main_pdf_entry.get(),
        docx_entry.get(),
        html_entry.get().split(","),
        additional_pdf_entry.get().split(",")
    )).grid(row=4, column=0, columnspan=3, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()