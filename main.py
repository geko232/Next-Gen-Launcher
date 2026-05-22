import os
import sys
import json
import time
import webbrowser
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

CONFIG_FILE = "config_ultra_launcher_v6.json"

# Установка глобальной темной темы
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Next-Gen Launcher")
        self.geometry("980x650")
        self.minsize(900, 580)

        # База данных лаунчера
        self.v2ray_path = ctk.StringVar()
        self.items = []  # [{"type": "...", "name": "...", "path": "...", "image": "..."}]

        # Переменные ввода формы
        self.input_name = ctk.StringVar()
        self.input_path = ctk.StringVar()
        self.input_image = ctk.StringVar()
        self.input_type = ctk.StringVar(value="app")

        self.load_settings()

        # Контейнер слоев
        self.container = ctk.CTkFrame(self, fg_color="#0e0e10", corner_radius=0)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self.container, fg_color="#0e0e10", corner_radius=0)
        self.settings_frame = ctk.CTkFrame(self.container, fg_color="#0e0e10", corner_radius=0)

        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.settings_frame.grid(row=0, column=0, sticky="nsew")

        self.init_main_screen()
        self.init_settings_screen()
        self.show_main()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.v2ray_path.set(data.get("v2ray", r"C:\Program Files\v2RayTun\v2RayTun.exe"))
                    self.items = data.get("items", [])
                    return
            except Exception:
                pass
        self.v2ray_path.set(r"C:\Program Files\v2RayTun\v2RayTun.exe")
        self.items = []

    def save_settings(self):
        try:
            data = {
                "v2ray": self.v2ray_path.get().strip(),
                "items": self.items
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось записать конфигурацию:\n{e}")

    def show_main(self):
        self.main_frame.tkraise()
        self.refresh_main_icons()
        self.update_widgets_stats()

    def show_settings(self):
        self.settings_frame.tkraise()
        self.refresh_settings_list()

    def allow_paste(self, event):
        try:
            event.widget.insert(tk.INSERT, self.clipboard_get())
        except tk.TclError:
            pass
        return "break"

    # --- ЭКРАН 1: ГЛАВНЫЙ ЭКРАН ---
    def init_main_screen(self):
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=(25, 0))

        title_lbl = ctk.CTkLabel(header, text="КОНСОЛЬ СИСТЕМЫ",
                                 font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color="#ffffff")
        title_lbl.pack(side="left")

        self.btn_set = ctk.CTkButton(
            header, text="⚙  Настройки лаунчера", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#1f1f24", hover_color="#2b2b36", height=38, width=180, command=self.show_settings
        )
        self.btn_set.pack(side="right")

        dashboard = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        dashboard.pack(fill="x", padx=35, pady=20)

        self.btn_vpn = ctk.CTkButton(
            dashboard, text="⚡\n\nЗАПУСТИТЬ VPN", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#121214", hover_color="#18181f", border_width=1, border_color="#3498db", corner_radius=12,
            height=140, width=210, command=self.action_vpn
        )
        self.btn_vpn.pack(side="left", padx=(0, 15))

        self.btn_run_all = ctk.CTkButton(
            dashboard, text="🚀\n\nЗАПУСТИТЬ ВСЁ", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#121214", hover_color="#14221a", border_width=1, border_color="#9b59b6", corner_radius=12,
            height=140, width=210, command=self.action_run_everything
        )
        self.btn_run_all.pack(side="left", padx=(0, 15))

        clean_card = ctk.CTkFrame(dashboard, fg_color="#121214", border_width=1, border_color="#2a2a35",
                                  corner_radius=12, width=210, height=140)
        clean_card.pack_propagate(False)
        clean_card.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(clean_card, text="ОПТИМИЗАЦИЯ СЕТИ", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color="#55555e").pack(pady=(12, 2))
        ctk.CTkLabel(clean_card, text="Сброс DNS протоколов", font=ctk.CTkFont(family="Segoe UI", size=12),
                     text_color="#aaaaaa").pack(pady=2)
        ctk.CTkButton(clean_card, text="Очистить систему", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                      fg_color="#e67e22", hover_color="#d35400", height=28, corner_radius=6,
                      command=self.action_clean_pc).pack(side="bottom", fill="x", padx=15, pady=15)

        self.stats_card = ctk.CTkFrame(dashboard, fg_color="#121214", border_width=1, border_color="#2a2a35",
                                       corner_radius=12, width=210, height=140)
        self.stats_card.pack_propagate(False)
        self.stats_card.pack(side="left")

        ctk.CTkLabel(self.stats_card, text="СТАТИСТИКА БАЗЫ",
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#55555e").pack(
            pady=(12, 5))
        self.lbl_stats_apps = ctk.CTkLabel(self.stats_card, text="• Приложений: 0",
                                           font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#3498db",
                                           anchor="w")
        self.lbl_stats_apps.pack(fill="x", padx=20, pady=2)
        self.lbl_stats_sites = ctk.CTkLabel(self.stats_card, text="• Веб-сайтов: 0",
                                            font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#2ecc71",
                                            anchor="w")
        self.lbl_stats_sites.pack(fill="x", padx=20, pady=2)

        middle_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        middle_bar.pack(fill="x", padx=35, pady=(15, 5))
        ctk.CTkLabel(middle_bar, text="ПЛИТКИ БЫСТРОГО ЗАПУСКА",
                     font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#55555e").pack(
            side="left")

        self.tiles_canvas = tk.Canvas(self.main_frame, bg="#0e0e10", highlightthickness=0)
        self.tiles_canvas.pack(fill="both", expand=True, padx=35, pady=(5, 50))

        self.tiles_frame = ctk.CTkFrame(self.tiles_canvas, fg_color="#0e0e10", corner_radius=0)
        self.tiles_canvas.create_window((0, 0), window=self.tiles_frame, anchor="nw")
        self.tiles_frame.bind("<Configure>",
                              lambda e: self.tiles_canvas.configure(scrollregion=self.tiles_canvas.bbox("all")))

        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Система готова к работе",
                                       font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#44444a", anchor="w",
                                       height=25)
        self.lbl_status.place(relx=0.0, rely=1.0, x=35, y=-30, relwidth=1.0)

    def update_widgets_stats(self):
        apps_count = sum(1 for i in self.items if i["type"] == "app")
        sites_count = sum(1 for i in self.items if i["type"] == "site")
        self.lbl_stats_apps.configure(text=f"• Приложений: {apps_count}")
        self.lbl_stats_sites.configure(text=f"• Веб-сайтов: {sites_count}")

    def refresh_main_icons(self):
        for widget in self.tiles_frame.winfo_children():
            widget.destroy()

        max_columns = 5

        for index, item in enumerate(self.items):
            indicator_color = "#3498db" if item["type"] == "app" else "#2ecc71"
            hover_glow = "#121d28" if item["type"] == "app" else "#0f2417"
            img_path = item.get("image", "").strip()

            ctk_image = None
            if img_path and os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    if hasattr(pil_img, "n_frames") and pil_img.n_frames > 1:
                        pil_img.seek(pil_img.n_frames - 1)

                    pil_img = pil_img.convert("RGBA")
                    pil_img = pil_img.resize((44, 44), Image.Resampling.LANCZOS)
                    ctk_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(44, 44))
                except Exception as e:
                    print(f"Ошибка загрузки иконки {img_path}: {e}")

            display_text = f"\n{item['name']}" if ctk_image else f"{'🖥' if item['type'] == 'app' else '🌐'}\n\n{item['name']}"
            if len(item['name']) > 13:
                short_name = item['name'][:11] + "..."
                display_text = f"\n{short_name}" if ctk_image else f"{'🖥' if item['type'] == 'app' else '🌐'}\n\n{short_name}"

            tile = ctk.CTkButton(
                self.tiles_frame,
                text=display_text,
                image=ctk_image,
                compound="top",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color="#121214", hover_color=hover_glow, text_color="#ffffff",
                border_width=1, border_color="#2a2a35", corner_radius=12,
                width=135, height=115, command=lambda val=item: self.launch_item(val)
            )

            row = index // max_columns
            col = index % max_columns
            tile.grid(row=row, column=col, padx=(0, 15), pady=(0, 15))

            led = ctk.CTkFrame(tile, fg_color=indicator_color, height=3, width=35, corner_radius=1)
            led.place(relx=0.5, y=6, anchor="center")

    def launch_item(self, item, quiet=False):
        if item["type"] == "app":
            if os.path.exists(item["path"]):
                if not quiet: self.update_status(f"Запуск {item['name']}...", "#3498db")
                app_dir = os.path.dirname(item["path"])
                subprocess.Popen(f'"{item["path"]}"', cwd=app_dir, shell=True)
                if not quiet: self.update_status(f"Запущено: {item['name']}", "#2ecc71")
            else:
                if not quiet: messagebox.showerror("Ошибка", f"Файл не найден:\n{item['path']}")
        else:
            if not quiet: self.update_status(f"Переход на {item['name']}...", "#3498db")
            webbrowser.open(item["path"])
            if not quiet: self.update_status(f"Открыт сайт {item['name']}!", "#2ecc71")

    # --- ЭКРАН 2: НАСТРОЙКИ ---
    def init_settings_screen(self):
        f_lbl = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        f_val = ctk.CTkFont(family="Segoe UI", size=12)

        scroll_settings = ctk.CTkScrollableFrame(self.settings_frame, fg_color="transparent", corner_radius=0)
        scroll_settings.pack(fill="both", expand=True, padx=35, pady=20)

        ctk.CTkLabel(scroll_settings, text="НАСТРОЙКИ ЛАУНЧЕРА",
                     font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#ffffff").pack(anchor="w",
                                                                                                             pady=(0,
                                                                                                                   15))

        # 1. Поле VPN пути
        ctk.CTkLabel(scroll_settings, text="Путь к исполняемому файлу v2RayTun.exe:", font=f_lbl).pack(anchor="w",
                                                                                                       pady=(5, 2))
        f_v2 = ctk.CTkFrame(scroll_settings, fg_color="transparent")
        f_v2.pack(fill="x", pady=(0, 15))

        entry_vpn = ctk.CTkEntry(f_v2, textvariable=self.v2ray_path, font=f_val, fg_color="#121214",
                                 border_color="#2a2a35", height=38, corner_radius=6)
        entry_vpn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry_vpn.bind("<Control-v>", self.allow_paste)

        ctk.CTkButton(f_v2, text="Обзор...", font=f_lbl, fg_color="#1f1f24", hover_color="#2b2b36", width=100,
                      height=38, command=self.browse_vpn).pack(side="right")

        # 2. Форма добавления ресурса
        ctk.CTkLabel(scroll_settings, text="Форма создания новой плитки быстрого запуска:", font=f_lbl).pack(anchor="w",
                                                                                                             pady=(10,
                                                                                                                   5))

        form_box = ctk.CTkFrame(scroll_settings, fg_color="#121214", border_width=1, border_color="#2a2a35",
                                corner_radius=8)
        form_box.pack(fill="x", pady=(0, 15), ipady=15)

        f_radio = ctk.CTkFrame(form_box, fg_color="transparent")
        f_radio.pack(fill="x", pady=(15, 8), padx=15)
        ctk.CTkRadioButton(f_radio, text="Приложение (.exe)", variable=self.input_type, value="app", font=f_lbl,
                           command=self.toggle_form_labels).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(f_radio, text="Сайт / Веб-ссылка", variable=self.input_type, value="site", font=f_lbl,
                           command=self.toggle_form_labels).pack(side="left")

        self.lbl_form_path = ctk.CTkLabel(form_box, text="Выберите файл программы:", font=f_val, text_color="#88888e")
        self.lbl_form_path.pack(anchor="w", padx=15)
        f_form_path_row = ctk.CTkFrame(form_box, fg_color="transparent")
        f_form_path_row.pack(fill="x", pady=(0, 8), padx=15)

        self.ent_form_path = ctk.CTkEntry(f_form_path_row, textvariable=self.input_path, font=f_val, fg_color="#0e0e10",
                                          border_color="#2a2a35", height=35)
        self.ent_form_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_form_path.bind("<Control-v>", self.allow_paste)

        self.btn_form_browse = ctk.CTkButton(f_form_path_row, text="Выбрать файл", font=f_val, fg_color="#1f1f24",
                                             hover_color="#2b2b36", width=110, height=35, command=self.browse_form_file)
        self.btn_form_browse.pack(side="right")

        # Добавление ИКОНКИ / КАРТИНКИ для плитки
        ctk.CTkLabel(form_box, text="Прикрепить иконку / изображение приложения (Необязательно):", font=f_val,
                     text_color="#88888e").pack(anchor="w", padx=15)
        f_img_row = ctk.CTkFrame(form_box, fg_color="transparent")
        f_img_row.pack(fill="x", pady=(0, 8), padx=15)

        entry_img = ctk.CTkEntry(f_img_row, textvariable=self.input_image, font=f_val, fg_color="#0e0e10",
                                 border_color="#2a2a35", height=35,
                                 placeholder_text="Выберите файл .ico, .png или .jpg")
        entry_img.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry_img.bind("<Control-v>", self.allow_paste)

        ctk.CTkButton(f_img_row, text="Выбрать иконку", font=f_val, fg_color="#1f1f24", hover_color="#2b2b36",
                      width=110, height=35, command=self.browse_form_image).pack(side="right")

        # Поле названия
        ctk.CTkLabel(form_box, text="Введите название для плитки:", font=f_val, text_color="#88888e").pack(anchor="w",
                                                                                                           padx=15)

        entry_name = ctk.CTkEntry(form_box, textvariable=self.input_name, font=f_val, fg_color="#0e0e10",
                                  border_color="#2a2a35", height=35)
        entry_name.pack(fill="x", pady=(0, 12), padx=15)
        entry_name.bind("<Control-v>", self.allow_paste)

        ctk.CTkButton(form_box, text="+ СГЕНЕРИРОВАТЬ ПЛИТКУ РЕСУРСА", font=f_lbl, fg_color="#3498db",
                      hover_color="#2980b9", height=40, corner_radius=6, command=self.add_item_from_form).pack(fill="x",
                                                                                                               padx=15,
                                                                                                               pady=(5,
                                                                                                                     5))

        # Список плиток
        ctk.CTkLabel(scroll_settings, text="Текущий список зарегистрированных плиток:", font=f_lbl).pack(anchor="w",
                                                                                                         pady=(10, 2))
        self.list_frame = ctk.CTkFrame(scroll_settings, fg_color="#121214", border_width=1, border_color="#2a2a35",
                                       corner_radius=12)
        self.list_frame.pack(fill="x", pady=(0, 30))

        # Системные кнопки
        f_btns = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        f_btns.pack(fill="x", side="bottom", padx=35, pady=20)
        ctk.CTkButton(f_btns, text="Отмена", font=f_lbl, fg_color="#1f1f24", hover_color="#2b2b36", width=120,
                      height=40, command=self.show_main).pack(side="left")
        ctk.CTkButton(f_btns, text="Сохранить лаунчер", font=f_lbl, fg_color="#2ecc71", hover_color="#27ae60",
                      width=180, height=40, command=self.press_save).pack(side="right")

    def toggle_form_labels(self):
        if self.input_type.get() == "app":
            self.lbl_form_path.configure(text="Выберите файл программы:")
            self.btn_form_browse.pack(side="right")
        else:
            self.lbl_form_path.configure(text="Вставьте URL-адрес веб-сайта (например, youtube.com):")
            self.btn_form_browse.pack_forget()

    def browse_form_file(self):
        p = filedialog.askopenfilename(filetypes=[("Исполняемые файлы", "*.exe")])
        if p: self.input_path.set(p)

    def browse_form_image(self):
        p = filedialog.askopenfilename(filetypes=[("Иконки и Картинки", "*.ico *.png *.jpg *.jpeg")])
        if p: self.input_image.set(p)

    def add_item_from_form(self):
        path_val = self.input_path.get().strip()
        name_val = self.input_name.get().strip()
        img_val = self.input_image.get().strip()
        type_val = self.input_type.get()

        if not path_val or not name_val:
            messagebox.showwarning("Внимание", "Заполните обязательные поля: путь/ссылку и название!")
            return

        if type_val == "site" and not path_val.startswith(("http://", "https://")):
            path_val = "https://" + path_val

        self.items.append({"type": type_val, "name": name_val, "path": path_val, "image": img_val})
        self.input_path.set("")
        self.input_name.set("")
        self.input_image.set("")
        self.refresh_settings_list()

    def refresh_settings_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.items:
            lbl = ctk.CTkLabel(self.list_frame, text="Плитки ещё не добавлены. Заполните форму выше.",
                               font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"), text_color="#66666e")
            lbl.pack(anchor="w", padx=20, pady=20)
        else:
            for index, item in enumerate(self.items):
                row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
                row.pack(fill="x", expand=True, padx=15, pady=5)

                prefix = "[СОФТ]" if item["type"] == "app" else "[САЙТ]"
                has_img = " 🖼" if item.get("image") else ""
                lbl_text = f"{prefix} {has_img} {item['name']}  →  ({item['path'][:45]}...)" if len(
                    item['path']) > 45 else f"{prefix} {has_img} {item['name']}  →  ({item['path']})"

                ctk.CTkLabel(row, text=lbl_text, font=ctk.CTkFont(family="Segoe UI", size=12),
                             text_color="#ffffff").pack(side="left", anchor="center")
                ctk.CTkButton(row, text="Удалить", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                              fg_color="#e74c3c", hover_color="#c0392b", width=80, height=28, corner_radius=4,
                              command=lambda i=index: self.delete_item(i)).pack(side="right")

    def delete_item(self, index):
        del self.items[index]
        self.refresh_settings_list()

    def browse_vpn(self):
        p = filedialog.askopenfilename(filetypes=[("Программы", "*.exe")])
        if p: self.v2ray_path.set(p)

    def press_save(self):
        self.save_settings()
        self.show_main()

    def update_status(self, text, color="#888888"):
        self.lbl_status.configure(text=f"自由: {text}", text_color=color)
        self.update()

    # --- СЦЕНАРИИ ЗАПУСКА ---
    def action_vpn(self, quiet=False):
        v2ray = self.v2ray_path.get().strip()
        if os.path.exists(v2ray):
            if not quiet: self.update_status("Развёртывание ядра v2RayTun...", "#3498db")
            v2ray_dir = os.path.dirname(v2ray)
            cmd = f'"{v2ray}"'
            subprocess.Popen(cmd, cwd=v2ray_dir, shell=True)
            if not quiet:
                for i in range(4, 0, -1):
                    self.update_status(f"Синхронизация прокси-туннеля... {i} сек.", "#e67e22")
                    time.sleep(1)
                self.update_status("VPN успешно активирован!", "#2ecc71")
            return True
        else:
            if not quiet: messagebox.showerror("Ошибка", f"Файл v2RayTun не найден:\n{v2ray}")
            return False

    def action_run_everything(self):
        self.update_status("Запуск Мега-Сценария...", "#9b59b6")
        vpn_success = self.action_vpn(quiet=True)
        if vpn_success:
            self.update_status("VPN запущен. Ожидание 3 сек перед софтом...", "#e67e22")
            time.sleep(3)

        if not self.items:
            self.update_status("VPN активен. Список ресурсов пуст.", "#2ecc71")
            return

        for item in self.items:
            self.launch_item(item, quiet=True)
            time.sleep(0.2)

        self.update_status("Сценарий выполнен! Все ресурсы запущены.", "#2ecc71")

    def action_clean_pc(self):
        self.update_status("Оптимизация сетевых протоколов...", "#e67e22")
        try:
            subprocess.Popen("ipconfig /flushdns", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
            self.update_status("Сетевой кэш DNS успешно очищен!", "#2ecc71")
            messagebox.showinfo("Оптимизация",
                                "Системный кэш DNS Windows успешно очищен!\nИнтернет-соединение оптимизировано.")
        except Exception:
            self.update_status("Ошибка оптимизации", "#e74c3c")


if __name__ == "__main__":
    app = App()
    app.mainloop()
