import os
import random
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class TemplateEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор документов")
        self.root.geometry("1200x800")

        # Конфигурация
        self.config = self.load_config()
        self.current_template = None
        self.dragging = None
        self.field_objects = []
        self.selected_field = None
        self.image_objects = []
        self.resizing = None
        self.resize_start_x = None
        self.resize_start_y = None

        # GUI элементы
        self.create_widgets()
        self.load_templates_list()

    def load_config(self):
        """Загружает конфигурацию из файла config.json."""
        if not os.path.exists("config.json"):
            base_config = {
                  "birth": {
                    "image_path": "templates/birth.jpg",
                    "fields": [],
                    "images": []
                  },
                  "death": {
                    "image_path": "templates/death.jpg",
                    "fields": [],
                    "images": []
                  },
                  "divorce": {
                    "image_path": "templates/divorce.jpg",
                    "fields": [],
                    "images": []
                  },
                  "marriage": {
                    "image_path": "templates/marriage.jpg",
                    "fields": [],
                    "images": []
                  },
                  "inn": {
                    "image_path": "templates/inn.jpg",
                    "fields": [],
                    "images": []
                  },
                  "inn_2004": {
                    "image_path": "templates/inn_2004.jpg",
                    "fields": [],
                    "images": []
                  },
                  "inn_2004_2": {
                    "image_path": "templates/inn_2004_2.jpg",
                    "fields": [],
                    "images": []
                  },
                  "inn_esp": {
                    "image_path": "templates/inn_esp.jpg",
                    "fields": [],
                    "images": []
                  }
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(base_config, f, indent=2, ensure_ascii=False)
            return base_config

        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def create_widgets(self):
        # Основной контейнер
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True)

        # Левая панель - шаблоны и управление
        left_panel = ttk.Frame(main_paned, width=200)
        main_paned.add(left_panel, weight=0)

        # Список шаблонов
        self.templates_list = ttk.Treeview(left_panel, show="tree")
        self.templates_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.templates_list.bind("<<TreeviewSelect>>", self.select_template)

        # Кнопки управления
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Добавить поле", command=self.add_field).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить поле", command=self.delete_field).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить", command=self.save_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сгенерировать", command=self.generate_document).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Добавить изображение", command=self.add_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить изображение", command=self.delete_image).pack(side="left", padx=5)

        # Поле для выбора количества изображений
        self.num_images_var = tk.IntVar(value=1)  # По умолчанию 1 изображение
        ttk.Label(left_panel, text="Количество изображений:").pack(pady=5)
        ttk.Spinbox(left_panel, from_=1, to=100, textvariable=self.num_images_var).pack(pady=5)

        # Кнопка для генерации нескольких изображений
        ttk.Button(left_panel, text="Генерировать изображения", command=self.generate_multiple_images).pack(pady=10)

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
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        # Правая панель - свойства поля
        right_panel = ttk.Frame(main_paned, width=300)
        main_paned.add(right_panel, weight=0)

        # Панель свойств с прокруткой
        self.properties_frame = ttk.LabelFrame(right_panel, text="Свойства поля")
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

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)

    def on_mousewheel(self, event):
        """Обрабатывает прокрутку колесом мыши."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def on_shift_mousewheel(self, event):
        """Обрабатывает горизонтальную прокрутку с Shift + колесо мыши."""
        if event.num == 4 or event.delta > 0:
            self.canvas.xview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.xview_scroll(1, "units")

    def add_image(self):
        """Добавляет изображение на холст."""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png")]
        )

        if not file_path:
            return

        try:
            image = Image.open(file_path)
            image = image.resize((100, 100))  #
            photo_image = ImageTk.PhotoImage(image)


            image_id = self.canvas.create_image(100, 100, anchor="nw", image=photo_image)
            image_data = {
                "id": image_id,
                "image": photo_image,
                "original_image": image,
                "x": 100,
                "y": 100,
                "width": 100,
                "height": 100,
                "file_path": file_path
            }
            self.image_objects.append(image_data)

            self.config[self.current_template]["images"].append({
                "file_path": file_path,
                "x": 100,
                "y": 100,
                "width": 100,
                "height": 100
            })

            self.save_config()

            self.canvas.tag_bind(image_id, "<Button-1>", self.start_image_drag)
            self.canvas.tag_bind(image_id, "<B1-Motion>", self.on_image_drag)
            self.canvas.tag_bind(image_id, "<ButtonRelease-1>", self.end_image_drag)
            self.canvas.tag_bind(image_id, "<Button-3>", self.start_image_resize)
            self.canvas.tag_bind(image_id, "<B3-Motion>", self.on_image_resize)
            self.canvas.tag_bind(image_id, "<ButtonRelease-3>", self.end_image_resize)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def delete_image(self):
        """Удаляет выбранное изображение."""
        if not self.image_objects:
            messagebox.showwarning("Ошибка", "Нет изображений для удаления!")
            return

        selected_image = self.image_objects[-1]
        for img_config in self.config[self.current_template]["images"]:
            if img_config["file_path"] == selected_image["file_path"]:
                self.config[self.current_template]["images"].remove(img_config)
                break

        self.canvas.delete(selected_image["id"])
        self.image_objects.remove(selected_image)

        self.save_config()

    def start_image_drag(self, event):
        """Начинает перетаскивание изображения."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.dragging = self.canvas.find_closest(x, y)[0]

    def on_image_drag(self, event):
        """Обрабатывает перетаскивание изображения."""
        if self.dragging:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            self.canvas.coords(self.dragging, x, y)

            for img in self.image_objects:
                if img["id"] == self.dragging:
                    img["x"] = x
                    img["y"] = y
                    break

    def end_image_drag(self, event):
        """Завершает перетаскивание изображения."""
        if self.dragging:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            for img in self.image_objects:
                if img["id"] == self.dragging:
                    img["x"] = x
                    img["y"] = y
                    break

            self.dragging = None

    def start_image_resize(self, event):
        """Начинает масштабирование изображения."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.resizing = self.canvas.find_closest(x, y)[0]

        self.resize_start_x = x
        self.resize_start_y = y

    def on_image_resize(self, event):
        """Обрабатывает масштабирование изображения."""
        if self.resizing:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            delta_x = x - self.resize_start_x
            delta_y = y - self.resize_start_y

            for img in self.image_objects:
                if img["id"] == self.resizing:
                    new_width = img["width"] + delta_x
                    new_height = img["height"] + delta_y

                    min_size = 10
                    new_width = max(new_width, min_size)
                    new_height = max(new_height, min_size)

                    new_width = int(new_width)
                    new_height = int(new_height)

                    resized_image = img["original_image"].resize((new_width, new_height))
                    photo_image = ImageTk.PhotoImage(resized_image)

                    self.canvas.itemconfig(img["id"], image=photo_image)
                    img["image"] = photo_image
                    img["width"] = new_width
                    img["height"] = new_height

                    self.resize_start_x = x
                    self.resize_start_y = y
                    break

    def end_image_resize(self, event):
        """Завершает масштабирование изображения."""
        if self.resizing:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            for img in self.image_objects:
                if img["id"] == self.resizing:
                    img["x"] = x
                    img["y"] = y
                    break

            self.resizing = None

    def create_properties_controls(self):
        self.prop_vars = {}
        fields = [
            ("text", "Текст:", "entry"),
            ("font", "Шрифт:", "combobox"),
            ("font_size", "Размер шрифта:", "spinbox"),
            ("bold", "Жирный:", "check"),
            ("italic", "Курсив:", "check"),
            ("x", "X:", "spinbox"),
            ("y", "Y:", "spinbox")
        ]

        for field in fields:
            frame = ttk.Frame(self.properties_inner_frame)
            frame.pack(fill="x", padx=5, pady=2)

            ttk.Label(frame, text=field[1]).pack(side="left")

            if field[2] == "entry":
                var = tk.StringVar()
                ttk.Entry(frame, textvariable=var).pack(side="right", fill="x", expand=True)
            elif field[2] == "combobox":
                var = tk.StringVar()
                ttk.Combobox(frame, textvariable=var, values=self.get_available_fonts()).pack(side="right")
            elif field[2] == "spinbox":
                var = tk.IntVar()
                ttk.Spinbox(frame, from_=0, to=1000, textvariable=var).pack(side="right")
            elif field[2] == "check":
                var = tk.BooleanVar()
                ttk.Checkbutton(frame, variable=var).pack(side="right")

            self.prop_vars[field[0]] = var

        ttk.Button(
            self.properties_inner_frame,
            text="Случайно",
            command=self.load_random_text
        ).pack(pady=5)

        ttk.Button(self.properties_inner_frame, text="Применить", command=self.apply_properties).pack(pady=5)

        ttk.Button(
            self.properties_inner_frame,
            text="Обновить все поля",
            command=self.update_all_fields
        ).pack(pady=5)

    def load_random_text(self):
        """Загружает случайный текст из выбранного файла."""
        if not self.selected_field:
            messagebox.showwarning("Ошибка", "Поле не выбрано!")
            return

        file_path = filedialog.askopenfilename(
            title="Выберите файл с текстом",
            filetypes=[("Текстовые файлы", "*.txt")]
        )

        if not file_path:
            return  # Пользователь отменил выбор

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

            if not lines:
                messagebox.showwarning("Ошибка", "Файл пуст!")
                return

            random_text = random.choice(lines)

            self.prop_vars["text"].set(random_text)
            self.selected_field["config"]["file_path"] = file_path
            self.apply_properties()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def update_all_fields(self):
        """Обновляет все поля с привязанными файлами."""
        for field in self.field_objects:
            if "file_path" in field["config"]:
                file_path = field["config"]["file_path"]
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        lines = [line.strip() for line in file.readlines() if line.strip()]

                    if not lines:
                        continue  # Пропускаем пустые файлы

                    random_text = random.choice(lines)
                    field["config"]["text"] = random_text
                except Exception as e:
                    print(f"Ошибка при обновлении поля: {str(e)}")

        self.draw_fields()
        messagebox.showinfo("Успех", "Все поля обновлены!")

    def generate_multiple_images(self):
        """Генерирует несколько изображений с обновленными полями."""
        num_images = self.num_images_var.get()

        if not os.path.exists("output"):
            os.makedirs("output")

        template_folder = os.path.join("output", self.current_template)
        if not os.path.exists(template_folder):
            os.makedirs(template_folder)

        existing_files = os.listdir(template_folder)
        existing_numbers = []

        for file_name in existing_files:
            if file_name.startswith(f"{self.current_template}_") and file_name.endswith(".jpg"):
                try:
                    number = int(file_name.split("_")[-1].split(".")[0])
                    existing_numbers.append(number)
                except ValueError:
                    continue

        start_number = max(existing_numbers) + 1 if existing_numbers else 1

        for i in range(start_number, start_number + num_images):
            self.update_all_fields()

            output_path = os.path.join(template_folder, f"{self.current_template}_{i}.jpg")
            self.generate_document_to_path(output_path)

        messagebox.showinfo("Готово", f"Сгенерировано {num_images} изображений в папке {template_folder}!")

    def generate_document_to_path(self, output_path):
        """Генерирует документ и сохраняет его по указанному пути."""
        if not self.current_template:
            messagebox.showerror("Ошибка", "Шаблон не выбран!")
            return

        # Создаем копию изображения шаблона
        image = self.original_image.copy()
        draw = ImageDraw.Draw(image)

        # Отрисовываем изображения (в первую очередь)
        for img in self.image_objects:
            img_data = img["original_image"].resize((img["width"], img["height"]))

            x = int(img["x"])
            y = int(img["y"])
            # Если изображение имеет прозрачность, используем маску
            if img_data.mode == "RGBA":
                image.paste(img_data, (x, y), img_data)
            else:
                image.paste(img_data, (x, y))

        # Отрисовываем текстовые поля (после изображений)
        for field in self.config[self.current_template]["fields"]:
            text = field.get("text", "Текст")
            font_path = os.path.join("fonts", field.get("font", "arial.ttf"))
            font_size = field.get("font_size", 14) + 4  # Увеличиваем размер шрифта на 4
            bold = field.get("bold", False)
            italic = field.get("italic", False)

            try:
                font = ImageFont.truetype(font_path, font_size)
                if bold:
                    font = ImageFont.truetype(font_path, font_size, encoding="unic",
                                             )
                if italic:
                    font = ImageFont.truetype(font_path, font_size, encoding="unic",
                                              )
            except IOError:
                font = ImageFont.load_default()

            x = int(field["x"])
            y = int(field["y"])

            draw.text(
                (x, y),
                text,
                font=font,
                fill="black",
                anchor="mm"  # Центрируем текст относительно координат
            )

        # Сохраняем итоговое изображение
        image.save(output_path)

    def apply_properties(self):
        """Применяет изменения свойств выбранного поля."""
        if not self.selected_field:
            messagebox.showwarning("Ошибка", "Поле не выбрано!")
            return

        self.canvas.delete(self.selected_field["id"])

        for key, var in self.prop_vars.items():
            self.selected_field["config"][key] = var.get()

        self.draw_fields()
        messagebox.showinfo("Успех", "Свойства применены!")

    def get_available_fonts(self):
        """Возвращает список доступных шрифтов из папки fonts."""
        fonts_dir = "fonts"
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir)
            return ["arial.ttf"]

        return [f for f in os.listdir(fonts_dir) if f.endswith(".ttf")]

    def load_templates_list(self):
        """Загружает список шаблонов в Treeview."""
        for template in self.config.keys():
            self.templates_list.insert("", "end", text=template, values=(template,))

    def select_template(self, event):
        """Обрабатывает выбор шаблона."""
        item = self.templates_list.selection()[0]
        self.current_template = self.templates_list.item(item, "values")[0]
        self.load_template_image()
        self.draw_fields()
        self.clear_properties()

    def load_template_image(self):
        """Загружает изображение шаблона и добавленные изображения."""
        image_path = self.config[self.current_template]["image_path"]
        if not os.path.exists(image_path):
            messagebox.showerror("Ошибка", f"Файл шаблона {image_path} не найден!")
            return

        self.original_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.original_image)

        self.canvas.config(width=self.original_image.width, height=self.original_image.height)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        self.image_objects = []
        for img_data in self.config[self.current_template]["images"]:
            try:
                image = Image.open(img_data["file_path"])
                image = image.resize((img_data["width"], img_data["height"]))
                photo_image = ImageTk.PhotoImage(image)

                image_id = self.canvas.create_image(img_data["x"], img_data["y"], anchor="nw", image=photo_image)
                self.image_objects.append({
                    "id": image_id,
                    "image": photo_image,
                    "original_image": image,
                    "x": img_data["x"],
                    "y": img_data["y"],
                    "width": img_data["width"],
                    "height": img_data["height"],
                    "file_path": img_data["file_path"]
                })

                self.canvas.tag_bind(image_id, "<Button-1>", self.start_image_drag)
                self.canvas.tag_bind(image_id, "<B1-Motion>", self.on_image_drag)
                self.canvas.tag_bind(image_id, "<ButtonRelease-1>", self.end_image_drag)
                self.canvas.tag_bind(image_id, "<Button-3>", self.start_image_resize)
                self.canvas.tag_bind(image_id, "<B3-Motion>", self.on_image_resize)
                self.canvas.tag_bind(image_id, "<ButtonRelease-3>", self.end_image_resize)
            except Exception as e:
                print(f"Ошибка при загрузке изображения: {str(e)}")

        self.field_objects = []
        for field in self.config[self.current_template]["fields"]:
            x, y = field["x"], field["y"]
            text = field.get("text", "Текст")

            font_name = field.get("font", "arial.ttf")
            font_size = field.get("font_size", 14)
            bold = field.get("bold", False)
            italic = field.get("italic", False)

            font_str = f"{font_name} {font_size}"
            if bold:
                font_str += " bold"
            if italic:
                font_str += " italic"

            field_id = self.canvas.create_text(
                x, y,
                text=text,
                fill="black",
                font=font_str,
                tags=("field", "draggable")
            )

            self.field_objects.append({
                "id": field_id,
                "config": field
            })

            self.canvas.tag_bind(field_id, "<Button-1>", self.start_drag)
            self.canvas.tag_bind(field_id, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(field_id, "<ButtonRelease-1>", self.end_drag)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def draw_fields(self):
        """Отрисовывает поля на холсте."""
        self.canvas.delete("all")

        if hasattr(self, "image"):
            self.canvas.create_image(0, 0, anchor="nw", image=self.image)

        for img in self.image_objects:
            img["id"] = self.canvas.create_image(img["x"], img["y"], anchor="nw", image=img["image"])

            self.canvas.tag_bind(img["id"], "<Button-1>", self.start_image_drag)
            self.canvas.tag_bind(img["id"], "<B1-Motion>", self.on_image_drag)
            self.canvas.tag_bind(img["id"], "<ButtonRelease-1>", self.end_image_drag)
            self.canvas.tag_bind(img["id"], "<Button-3>", self.start_image_resize)
            self.canvas.tag_bind(img["id"], "<B3-Motion>", self.on_image_resize)
            self.canvas.tag_bind(img["id"], "<ButtonRelease-3>", self.end_image_resize)

        self.field_objects = []
        for field in self.config[self.current_template]["fields"]:
            x, y = field["x"], field["y"]
            text = field.get("text", "Текст")

            font_name = field.get("font", "arial.ttf")
            font_size = field.get("font_size", 14)
            bold = field.get("bold", False)
            italic = field.get("italic", False)

            font_str = f"{font_name} {font_size}"
            if bold:
                font_str += " bold"
            if italic:
                font_str += " italic"

            field_id = self.canvas.create_text(
                x, y,
                text=text,
                fill="black",
                font=font_str,
                tags=("field", "draggable")
            )

            self.field_objects.append({
                "id": field_id,
                "config": field
            })

            self.canvas.tag_bind(field_id, "<Button-1>", self.start_drag)
            self.canvas.tag_bind(field_id, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(field_id, "<ButtonRelease-1>", self.end_drag)

    def add_field(self):
        """Добавляет новое поле в шаблон."""
        # Находим координаты существующих полей
        existing_coords = {(f["config"]["x"], f["config"]["y"]) for f in self.field_objects}

        # Начальные координаты для нового поля
        x, y = 100, 100

        # Смещаем координаты, пока не найдем свободное место
        while (x, y) in existing_coords:
            x += 20
            y += 20

        # Создаем новое поле
        new_field = {
            "text": "Новый текст",
            "x": x,
            "y": y,
            "font": "arial.ttf",
            "font_size": 14,
            "bold": False,
            "italic": False
        }

        self.config[self.current_template]["fields"].append(new_field)
        self.draw_fields()
        self.selected_field = self.field_objects[-1]  # Выбираем последнее добавленное поле
        self.update_properties_controls()

    def delete_field(self):
        """Удаляет выбранное поле."""
        if not self.selected_field:
            messagebox.showwarning("Ошибка", "Поле не выбрано!")
            return

        self.config[self.current_template]["fields"].remove(self.selected_field["config"])

        self.field_objects = [f for f in self.field_objects if f["id"] != self.selected_field["id"]]

        self.canvas.delete(self.selected_field["id"])

        self.selected_field = None
        self.clear_properties()

        self.draw_fields()

    def save_config(self):
        """Сохраняет конфигурацию в файл."""
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Сохранено", "Конфигурация успешно сохранена!")

    def generate_document(self):
        """Генерирует итоговый документ."""
        if not self.current_template:
            messagebox.showerror("Ошибка", "Шаблон не выбран!")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if not output_path:
            return

        # Создаем копию изображения шаблона
        image = self.original_image.copy()
        draw = ImageDraw.Draw(image)

        # Отрисовываем текстовые поля
        for field in self.config[self.current_template]["fields"]:
            text = field.get("text", "Текст")
            font_path = os.path.join("fonts", field.get("font", "arial.ttf"))
            font_size = field.get("font_size", 14) + 4  # Увеличиваем размер шрифта на 4
            bold = field.get("bold", False)
            italic = field.get("italic", False)

            try:
                font = ImageFont.truetype(font_path, font_size)
                if bold:
                    font = ImageFont.truetype(font_path, font_size, encoding="unic",
                                              )
                if italic:
                    font = ImageFont.truetype(font_path, font_size, encoding="unic",
                                              )
            except IOError:
                font = ImageFont.load_default()

            draw.text(
                (field["x"], field["y"]),
                text,
                font=font,
                fill="black",
                anchor="mm"  # Центрируем текст относительно координат
            )

        # Отрисовываем изображения
        for img in self.image_objects:
            img_data = img["original_image"].resize((img["width"], img["height"]))
            image.paste(img_data, (img["x"], img["y"]), img_data)

        image.save(output_path)
        messagebox.showinfo("Готово", f"Документ сохранен: {output_path}")

        self.draw_fields()

    def start_drag(self, event):
        """Начинает перетаскивание текстового поля."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.dragging = self.canvas.find_closest(x, y)[0]

        for field in self.field_objects:
            if field["id"] == self.dragging:
                self.selected_field = field
                self.update_properties_controls()
                break

    def on_drag(self, event):
        """Обрабатывает перетаскивание текстового поля."""
        if self.dragging and self.selected_field:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            self.canvas.coords(self.dragging, x, y)

    def end_drag(self, event):
        """Завершает перетаскивание текстового поля."""
        if self.dragging and self.selected_field:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            self.selected_field["config"]["x"] = x
            self.selected_field["config"]["y"] = y

            self.dragging = None

    def update_properties_controls(self):
        """Обновляет значения в панели свойств."""
        if not self.selected_field:
            return

        for key, var in self.prop_vars.items():
            var.set(self.selected_field["config"].get(key, ""))

    def clear_properties(self):
        """Очищает значения в панели свойств."""
        for var in self.prop_vars.values():
            if isinstance(var, tk.StringVar):
                var.set("")
            elif isinstance(var, tk.IntVar):
                var.set(0)
            elif isinstance(var, tk.BooleanVar):
                var.set(False)


if __name__ == "__main__":
    root = tk.Tk()
    app = TemplateEditor(root)
    root.mainloop()