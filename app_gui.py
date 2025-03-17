import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import requests
import base64

def upload_file():
    file_path = filedialog.askopenfilename(
        title="Выберите файл",
        filetypes=(("Изображения", "*.jpg *.jpeg *.png"), ("Все файлы", "*.*"))
    )
    if not file_path:
        return

    component_name = simpledialog.askstring("Ввод", "Введите название компонента:")
    if not component_name:
        messagebox.showerror("Ошибка", "Название компонента не введено!")
        return

    with open(file_path, "rb") as file:
        encoded_file = base64.b64encode(file.read()).decode('utf-8')

    url = "http://127.0.0.1:8000/evaluate/"
    payload = {
        "component_name": component_name
    }
    files = {
        "file": ("file", encoded_file)
    }
    try:
        response = requests.post(url, data=payload, files=files)
        response.raise_for_status()

        result = response.json()
        # print(result)
        result_text = (
            f"Label: {result['label']}\n"
            f"Signature: {result['signature']}\n"
            f"Stamp: {result['stamp']}\n"
            f"ESP: {result['esp']}"
        )
        messagebox.showinfo("Результат", result_text)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка при отправке файла: {e}")

root = tk.Tk()
root.title("Тестирование API")

upload_button = tk.Button(root, text="Выбрать файл и отправить", command=upload_file)
upload_button.pack(pady=20)

root.mainloop()