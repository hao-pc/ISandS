import os
import json
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class ScreenshotEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор скриншотов")
        self.root.geometry("1200x800")

        # Конфигурация
        self.config = self.load_config()
        self.current_keyword = None
        self.regions = []
        self.selected_region = None
        self.current_image = None
        self.image = None
        self.current_image_index = 0
        self.images_for_keyword = []
        self.dragging_corner = None
        self.corner_radius = 5

        self.create_widgets()
        self.load_keywords_list()

    def load_config(self):
        """Загружает конфигурацию из файла config_screenshot.json."""
        if not os.path.exists("config_screenshot.json"):
            base_config = {}
            with open("config_screenshot.json", "w", encoding="utf-8") as f:
                json.dump(base_config, f, indent=2, ensure_ascii=False)
            return base_config

        with open("config_screenshot.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def create_widgets(self):
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # Левая панель - ключевые слова и управление
        left_panel = ttk.Frame(main_paned, width=200)
        main_paned.add(left_panel, weight=0)

        # Список ключевых слов
        self.keywords_list = ttk.Treeview(left_panel, show="tree")
        self.keywords_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.keywords_list.bind("<<TreeviewSelect>>", self.select_keyword)

        # Кнопки управления
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Добавить область", command=self.add_region).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить область", command=self.delete_region).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить конфиг", command=self.save_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Создать скриншоты", command=self.create_screenshots).pack(side="left", padx=5)

        # Поле для выбора папки с изображениями
        ttk.Button(left_panel, text="Выбрать папку", command=self.select_folder).pack(pady=10)

        # Кнопки для пролистывания изображений
        navigation_frame = ttk.Frame(left_panel)
        navigation_frame.pack(pady=10)

        ttk.Button(navigation_frame, text="Назад", command=self.prev_image).pack(side="left", padx=5)
        ttk.Button(navigation_frame, text="Вперед", command=self.next_image).pack(side="left", padx=5)

        # Центральная панель - холст с прокруткой
        center_panel = ttk.Frame(main_paned)
        main_paned.add(center_panel, weight=1)

        # Холст для изображения
        self.canvas = tk.Canvas(center_panel, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Вертикальная прокрутка
        v_scrollbar = ttk.Scrollbar(center_panel, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        # Горизонтальная прокрутка
        h_scrollbar = ttk.Scrollbar(center_panel, orient="horizontal", command=self.canvas.xview)
        h_scrollbar.pack(side="bottom", fill="x")

        # Настройка холста для работы с прокруткой
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Привязка событий мыши
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        # Правая панель - свойства области
        right_panel = ttk.Frame(main_paned, width=300)
        main_paned.add(right_panel, weight=0)

        # Панель свойств с прокруткой
        self.properties_frame = ttk.LabelFrame(right_panel, text="Свойства области")
        self.properties_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Контейнер для прокрутки
        self.properties_container = ttk.Frame(self.properties_frame)
        self.properties_container.pack(fill="both", expand=True)

        # Полоса прокрутки
        self.properties_canvas = tk.Canvas(self.properties_container)
        self.properties_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.properties_container, orient="vertical", command=self.properties_canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.properties_canvas.configure(yscrollcommand=scrollbar.set)
        self.properties_canvas.bind(
            "<Configure>",
            lambda e: self.properties_canvas.configure(scrollregion=self.properties_canvas.bbox("all"))
        )

        # Внутренний фрейм для элементов управления
        self.properties_inner_frame = ttk.Frame(self.properties_canvas)
        self.properties_canvas.create_window((0, 0), window=self.properties_inner_frame, anchor="nw")

        # Элементы управления свойствами
        self.create_properties_controls()

    def create_properties_controls(self):
        self.prop_vars = {}
        fields = [
            ("x1", "X1:", "spinbox"),
            ("y1", "Y1:", "spinbox"),
            ("x2", "X2:", "spinbox"),
            ("y2", "Y2:", "spinbox"),
        ]

        for field in fields:
            frame = ttk.Frame(self.properties_inner_frame)
            frame.pack(fill="x", padx=5, pady=2)

            ttk.Label(frame, text=field[1]).pack(side="left")

            if field[2] == "spinbox":
                var = tk.IntVar()
                ttk.Spinbox(frame, from_=0, to=10000, textvariable=var).pack(side="right")

            self.prop_vars[field[0]] = var

        ttk.Button(self.properties_inner_frame, text="Применить", command=self.apply_properties).pack(pady=5)

    def apply_properties(self):
        """Применяет изменения свойств выбранной области."""
        if not self.selected_region:
            messagebox.showwarning("Ошибка", "Область не выбрана!")
            return

        for key, var in self.prop_vars.items():
            self.selected_region[key] = var.get()

        self.draw_regions()
        messagebox.showinfo("Успех", "Свойства применены!")

    def load_keywords_list(self):
        """Загружает список ключевых слов в Treeview."""
        for keyword in self.config.keys():
            self.keywords_list.insert("", "end", text=keyword, values=(keyword,))

    def select_keyword(self, event):
        """Обрабатывает выбор ключевого слова."""
        item = self.keywords_list.selection()[0]
        self.current_keyword = self.keywords_list.item(item, "values")[0]
        self.load_images_for_keyword()
        self.current_image_index = 0
        self.load_image()
        self.draw_regions()
        self.clear_properties()

    def load_images_for_keyword(self):
        """Загружает список изображений для текущего ключевого слова."""
        if not self.current_keyword:
            return

        self.images_for_keyword = []
        for filename in os.listdir(os.path.dirname(self.config[self.current_keyword]["image_path"])):
            if filename.startswith(self.current_keyword) and (filename.endswith(".jpg") or filename.endswith(".png")):
                self.images_for_keyword.append(os.path.join(os.path.dirname(self.config[self.current_keyword]["image_path"]), filename))

    def load_image(self):
        """Загружает текущее изображение."""
        if not self.images_for_keyword or self.current_image_index >= len(self.images_for_keyword):
            messagebox.showerror("Ошибка", "Нет изображений для загрузки!")
            return

        image_path = self.images_for_keyword[self.current_image_index]
        self.current_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.current_image)

        self.canvas.config(width=self.current_image.width, height=self.current_image.height)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        self.regions = self.config[self.current_keyword].get("regions", [])
        self.draw_regions()

    def draw_regions(self):
        """Отрисовывает области на холсте."""
        self.canvas.delete("regions")
        self.canvas.delete("corners")

        for region in self.regions:
            x1, y1, x2, y2 = region["x1"], region["y1"], region["x2"], region["y2"]
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)

            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="regions")
            self.canvas.create_oval(x1 - self.corner_radius, y1 - self.corner_radius, x1 + self.corner_radius, y1 + self.corner_radius, fill="blue", tags="corners")
            self.canvas.create_oval(x2 - self.corner_radius, y1 - self.corner_radius, x2 + self.corner_radius, y1 + self.corner_radius, fill="blue", tags="corners")
            self.canvas.create_oval(x1 - self.corner_radius, y2 - self.corner_radius, x1 + self.corner_radius, y2 + self.corner_radius, fill="blue", tags="corners")
            self.canvas.create_oval(x2 - self.corner_radius, y2 - self.corner_radius, x2 + self.corner_radius, y2 + self.corner_radius, fill="blue", tags="corners")

    def start_drag(self, event):
        """Начинает перемещение угла."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        for region in self.regions:
            corners = [
                (region["x1"], region["y1"]),
                (region["x2"], region["y1"]),
                (region["x1"], region["y2"]),
                (region["x2"], region["y2"]),
            ]
            for i, (cx, cy) in enumerate(corners):
                if abs(cx - x) < self.corner_radius and abs(cy - y) < self.corner_radius:
                    self.dragging_corner = (region, i)
                    break

    def on_drag(self, event):
        """Обрабатывает перемещение угла."""
        if self.dragging_corner:
            region, corner_index = self.dragging_corner
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            # Обновляем координаты угла
            if corner_index == 0:
                region["x1"] = x
                region["y1"] = y
            elif corner_index == 1:
                region["x2"] = x
                region["y1"] = y
            elif corner_index == 2:
                region["x1"] = x
                region["y2"] = y
            elif corner_index == 3:
                region["x2"] = x
                region["y2"] = y

            self.draw_regions()

    def end_drag(self, event):
        """Завершает перемещение угла."""
        self.dragging_corner = None

    def add_region(self):
        """Добавляет новую область на изображение."""
        new_region = {
            "x1": 100,
            "y1": 100,
            "x2": 200,
            "y2": 200
        }

        self.regions.append(new_region)
        self.draw_regions()
        self.selected_region = self.regions[-1]
        self.update_properties_controls()

    def delete_region(self):
        """Удаляет выбранную область."""
        if not self.selected_region:
            messagebox.showwarning("Ошибка", "Область не выбрана!")
            return

        self.regions.remove(self.selected_region)
        self.selected_region = None
        self.clear_properties()
        self.draw_regions()

    def save_config(self):
        """Сохраняет конфигурацию в файл."""
        if not self.current_keyword:
            messagebox.showwarning("Ошибка", "Ключевое слово не выбрано!")
            return

        self.config[self.current_keyword] = {
            "image_path": self.config[self.current_keyword].get("image_path", ""),
            "regions": self.regions
        }

        with open("config_screenshot.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Сохранено", "Конфигурация успешно сохранена!")

    def create_screenshots(self):
        """Создает скриншоты по разметке."""
        if not self.current_keyword or not self.current_image:
            messagebox.showerror("Ошибка", "Изображение не загружено!")
            return

        output_folder = filedialog.askdirectory(title="Выберите папку для сохранения скриншотов")
        if not output_folder:
            return

        for i, region in enumerate(self.regions):
            x1, y1, x2, y2 = region["x1"], region["y1"], region["x2"], region["y2"]
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)

            cropped_image = self.current_image.crop((x1, y1, x2, y2))
            cropped_image.save(os.path.join(output_folder, f"{self.current_keyword}_{i}.jpg"))

        messagebox.showinfo("Готово", f"Скриншоты сохранены в папку {output_folder}!")

    def select_folder(self):
        """Выбирает папку с изображениями."""
        folder_path = filedialog.askdirectory(title="Выберите папку с изображениями")
        if not folder_path:
            return

        self.config = {}
        for filename in os.listdir(folder_path):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                keyword = filename.split("_")[0]
                if keyword not in self.config:
                    self.config[keyword] = {
                        "image_path": os.path.join(folder_path, filename),
                        "regions": []
                    }

        self.save_config()
        self.load_keywords_list()
        messagebox.showinfo("Успех", "Папка с изображениями загружена!")

    def update_properties_controls(self):
        """Обновляет значения в панели свойств."""
        if not self.selected_region:
            return

        for key, var in self.prop_vars.items():
            var.set(self.selected_region.get(key, 0))

    def clear_properties(self):
        """Очищает значения в панели свойств."""
        for var in self.prop_vars.values():
            if isinstance(var, tk.IntVar):
                var.set(0)

    def prev_image(self):
        """Переходит к предыдущему изображению."""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()
            self.draw_regions()

    def next_image(self):
        """Переходит к следующему изображению."""
        if self.current_image_index < len(self.images_for_keyword) - 1:
            self.current_image_index += 1
            self.load_image()
            self.draw_regions()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotEditor(root)
    root.mainloop()