import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

def select_file(entry, filetypes):
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def select_files(entry):
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf"), ("HTML files", "*.html")])
    entry.delete(0, tk.END)
    entry.insert(0, ";".join(file_paths))

def run_main_script():
    contract_pdf_path = contract_pdf_entry.get()
    word_doc_path = word_doc_entry.get()
    upd_files = upd_files_entry.get().split(";")

    if not contract_pdf_path or not word_doc_path or not upd_files:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите все необходимые файлы.")
        return

    # Запуск основного скрипта с переданными параметрами
    try:
        subprocess.run(["python", "src/main.py", contract_pdf_path, word_doc_path] + upd_files, check=True)
        messagebox.showinfo("Успех", "Скрипт успешно выполнен.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Ошибка", f"Ошибка при выполнении скрипта: {e}")

app = tk.Tk()
app.title("GUI для main.py")

tk.Label(app, text="Выберите contract_pdf_path:").grid(row=0, column=0, padx=10, pady=5)
contract_pdf_entry = tk.Entry(app, width=50)
contract_pdf_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(app, text="Выбрать", command=lambda: select_file(contract_pdf_entry, [("PDF files", "*.pdf")])).grid(row=0, column=2, padx=10, pady=5)

tk.Label(app, text="Выберите word_doc_path:").grid(row=1, column=0, padx=10, pady=5)
word_doc_entry = tk.Entry(app, width=50)
word_doc_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(app, text="Выбрать", command=lambda: select_file(word_doc_entry, [("Word files", "*.docx")])).grid(row=1, column=2, padx=10, pady=5)

tk.Label(app, text="Выберите upd_files (разделенные точкой с запятой):").grid(row=2, column=0, padx=10, pady=5)
upd_files_entry = tk.Entry(app, width=50)
upd_files_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(app, text="Выбрать", command=lambda: select_files(upd_files_entry)).grid(row=2, column=2, padx=10, pady=5)

tk.Button(app, text="Запустить", command=run_main_script).grid(row=3, column=0, columnspan=3, pady=20)

app.mainloop()