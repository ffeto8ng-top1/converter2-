import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

class ToolkitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер PRO")
        self.root.geometry("640x580")

        # Вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_convert = tk.Frame(self.notebook)
        self.tab_sort = tk.Frame(self.notebook)
        self.tab_rename = tk.Frame(self.notebook)

        self.notebook.add(self.tab_convert, text="Конвертер")
        self.notebook.add(self.tab_sort, text="Сортировка")
        self.notebook.add(self.tab_rename, text="Переименование")

        self.build_convert_tab()
        self.build_sort_tab()
        self.build_rename_tab()

    # ---------------------- КОНВЕРТЕР ----------------------
    def build_convert_tab(self):
        tk.Label(self.tab_convert, text="Выберите файлы или папку:").pack(pady=5)
        self.conv_file_var = tk.StringVar()
        f_frame = tk.Frame(self.tab_convert)
        f_frame.pack(fill="x", padx=10)
        tk.Entry(f_frame, textvariable=self.conv_file_var, width=34).pack(side="left", padx=(0, 5))
        tk.Button(f_frame, text="Файлы", command=self.select_conv_files).pack(side="left")
        tk.Button(f_frame, text="Папка", command=self.select_conv_folder).pack(side="left")

        tk.Label(self.tab_convert, text="Формат на выходе:").pack(pady=(15, 5))
        formats = ["PNG", "JPEG", "BMP", "TIFF", "WEBP", "GIF", "ICO", "PPM", "PGM", "PBM"]
        self.conv_fmt_var = tk.StringVar(value="PNG")
        cb = ttk.Combobox(self.tab_convert, textvariable=self.conv_fmt_var, values=formats, state="readonly", width=12)
        cb.pack()

        # Размер
        tk.Label(self.tab_convert, text="Размер:").pack(pady=(15, 5))
        self.conv_size_mode = tk.StringVar(value="none")
        sz_frame = tk.Frame(self.tab_convert)
        sz_frame.pack()
        # радиокнопки пересоздадим с командой ниже
        self._rebuild_size_radios(sz_frame)

        self.conv_px_frame = tk.Frame(self.tab_convert)
        tk.Label(self.conv_px_frame, text="Ш:").pack(side="left")
        self.conv_w = tk.Entry(self.conv_px_frame, width=6); self.conv_w.insert(0, "1920"); self.conv_w.pack(side="left")
        tk.Label(self.conv_px_frame, text="В:").pack(side="left")
        self.conv_h = tk.Entry(self.conv_px_frame, width=6); self.conv_h.insert(0, "1080"); self.conv_h.pack(side="left")
        self.conv_px_frame.pack(pady=(2, 0)); self.conv_px_frame.pack_forget()

        self.conv_pct_frame = tk.Frame(self.tab_convert)
        tk.Label(self.conv_pct_frame, text="%").pack(side="left")
        self.conv_pct = tk.Entry(self.conv_pct_frame, width=6); self.conv_pct.insert(0, "50"); self.conv_pct.pack(side="left")
        self.conv_pct_frame.pack(pady=(2, 0)); self.conv_pct_frame.pack_forget()

        # Качество JPEG
        tk.Label(self.tab_convert, text="Качество JPEG (1–100):").pack(pady=(10, 5))
        self.conv_quality = tk.IntVar(value=85)
        tk.Entry(self.tab_convert, textvariable=self.conv_quality, width=5).pack()

        # Папка вывода
        tk.Label(self.tab_convert, text="Куда сохранять:").pack(pady=(10, 5))
        self.conv_out_var = tk.StringVar()
        o_frame = tk.Frame(self.tab_convert)
        o_frame.pack(fill="x", padx=10)
        tk.Entry(o_frame, textvariable=self.conv_out_var, width=34).pack(side="left", padx=(0, 5))
        tk.Button(o_frame, text="Выбрать", command=self.select_conv_out).pack(side="left")

        tk.Button(self.tab_convert, text="Конвертировать", command=self.run_convert, bg="#dddddd", height=2, font=("Arial", 11, "bold")).pack(pady=15)
        self.conv_progress = ttk.Progressbar(self.tab_convert, mode="determinate")
        self.conv_progress.pack(fill="x", padx=20, pady=5)
        self.conv_status = tk.Label(self.tab_convert, text="", fg="blue")
        self.conv_status.pack()

        self.conv_input_files = []
        self.conv_input_folder = None

    def _rebuild_size_radios(self, parent):
        for w in parent.winfo_children(): w.destroy()
        tk.Radiobutton(parent, text="Не менять", variable=self.conv_size_mode, value="none", command=self._toggle_size_frames).pack(side="left", padx=5)
        tk.Radiobutton(parent, text="Пиксели", variable=self.conv_size_mode, value="pixels", command=self._toggle_size_frames).pack(side="left", padx=5)
        tk.Radiobutton(parent, text="Процент", variable=self.conv_size_mode, value="percent", command=self._toggle_size_frames).pack(side="left", padx=5)

    def _toggle_size_frames(self):
        mode = self.conv_size_mode.get()
        if mode == "pixels":
            self.conv_px_frame.pack()
            self.conv_pct_frame.pack_forget()
        elif mode == "percent":
            self.conv_px_frame.pack_forget()
            self.conv_pct_frame.pack()
        else:
            self.conv_px_frame.pack_forget()
            self.conv_pct_frame.pack_forget()

    def select_conv_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp *.gif *.ico *.ppm *.pgm *.pbm"), ("Все файлы", "*.*")])
        if files:
            self.conv_input_files = list(files)
            self.conv_input_folder = None
            self.conv_file_var.set(f"{len(files)} файлов")
            self.conv_status.config(text=""); self.conv_progress["value"] = 0

    def select_conv_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.conv_input_folder = folder
            self.conv_input_files = []
            self.conv_file_var.set(f"Папка: {os.path.basename(folder)}")
            self.conv_status.config(text=""); self.conv_progress["value"] = 0

    def select_conv_out(self):
        folder = filedialog.askdirectory()
        if folder: self.conv_out_var.set(folder)

    @staticmethod
    def _resize_image(img, mode, w_str, h_str, pct_str):
        try:
            if mode == "pixels":
                w = int(w_str or 0); h = int(h_str or 0)
                if w <= 0 or h <= 0: return img
                return img.resize((w, h), Image.LANCZOS)
            elif mode == "percent":
                pct = int(pct_str or 100)
                if pct <= 0 or pct > 200: pct = 100
                w = max(1, int(img.width * pct / 100))
                h = max(1, int(img.height * pct / 100))
                return img.resize((w, h), Image.LANCZOS)
            return img
        except Exception: return img

    def run_convert(self):
        fmt = self.conv_fmt_var.get().upper()
        out_dir = self.conv_out_var.get()
        quality = self.conv_quality.get()
        size_mode = self.conv_size_mode.get()
        w = self.conv_w.get() or "0"
        h = self.conv_h.get() or "0"
        pct = self.conv_pct.get() or "100"

        if not out_dir:
            messagebox.showerror("Ошибка", "Выберите папку для сохранения!")
            return

        sources = []
        if self.conv_input_files:
            sources = self.conv_input_files
        elif self.conv_input_folder:
            valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp", ".gif", ".ico", ".ppm", ".pgm", ".pbm"}
            sources = [os.path.join(self.conv_input_folder, f) for f in os.listdir(self.conv_input_folder)
                       if os.path.isfile(os.path.join(self.conv_input_folder, f)) and os.path.splitext(f)[1].lower() in valid_exts]
        else:
            messagebox.showwarning("Внимание", "Сначала выберите файлы или папку!")
            return

        if not sources:
            messagebox.showinfo("Инфо", "Нет поддерживаемых изображений.")
            return

        self.conv_progress["maximum"] = len(sources)
        self.conv_progress["value"] = 0
        self.conv_status.config(text="Конвертация...")
        self.root.update()

        ok_count = 0; fail_count = 0
        for src in sources:
            base, _ = os.path.splitext(src)
            dst = os.path.join(out_dir, os.path.basename(base) + "." + fmt.lower())
            try:
                with Image.open(src) as img:
                    img = self._resize_image(img, size_mode, w, h, pct)
                    if fmt == "JPEG":
                        if img.mode in ("RGBA", "LA", "P"):
                            bg = Image.new("RGB", img.size, (255, 255, 255))
                            if img.mode == "P": img = img.convert("RGBA")
                            mask = img.split()[-1] if img.mode == "RGBA" else None
                            bg.paste(img, mask=mask)
                            img = bg
                        img.save(dst, format="JPEG", quality=quality, optimize=True, progressive=True)
                    else:
                        img.save(dst, format=fmt)
                ok_count += 1
            except Exception as e:
                print(e); fail_count += 1
            self.conv_progress["value"] += 1
            self.root.update()

        msg = f"Готово: {ok_count} успешно, {fail_count} ошибок."
        self.conv_status.config(text=msg)
        messagebox.showinfo("Готово", msg)

    # ---------------------- СОРТИРОВЩИК ----------------------
    def build_sort_tab(self):
        tk.Label(self.tab_sort, text="Папка с файлами:").pack(pady=5)
        self.sort_in_var = tk.StringVar()
        s_frame = tk.Frame(self.tab_sort)
        s_frame.pack(fill="x", padx=10)
        tk.Entry(s_frame, textvariable=self.sort_in_var, width=40).pack(side="left", padx=(0, 5))
        tk.Button(s_frame, text="Выбрать", command=self.select_sort_in).pack(side="left")

        tk.Label(self.tab_sort, text="Куда сортировать:").pack(pady=(15, 5))
        self.sort_out_var = tk.StringVar()
        so_frame = tk.Frame(self.tab_sort)
        so_frame.pack(fill="x", padx=10)
        tk.Entry(so_frame, textvariable=self.sort_out_var, width=40).pack(side="left", padx=(0, 5))
        tk.Button(so_frame, text="Выбрать", command=self.select_sort_out).pack(side="left")

        tk.Button(self.tab_sort, text="Сортировать", command=self.run_sort, bg="#dddddd", height=2, font=("Arial", 11, "bold")).pack(pady=15)
        self.sort_progress = ttk.Progressbar(self.tab_sort, mode="determinate")
        self.sort_progress.pack(fill="x", padx=20, pady=5)
        self.sort_status = tk.Label(self.tab_sort, text="", fg="blue")
        self.sort_status.pack()

    def select_sort_in(self):
        f = filedialog.askdirectory()
        if f: self.sort_in_var.set(f)

    def select_sort_out(self):
        f = filedialog.askdirectory()
        if f: self.sort_out_var.set(f)

    def run_sort(self):
        src = self.sort_in_var.get()
        dst = self.sort_out_var.get()
        if not src or not dst:
            messagebox.showerror("Ошибка", "Укажите обе папки!")
            return

        ext_groups = {
            "images": {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp", ".gif"},
            "docs": {".pdf", ".doc", ".docx", ".txt", ".rtf"},
            "archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
            "code": {".py", ".js", ".html", ".css", ".cpp", ".java"},
            "audio": {".mp3", ".wav", ".ogg", ".flac"},
            "video": {".mp4", ".avi", ".mkv", ".mov"},
        }

        files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
        if not files:
            messagebox.showinfo("Инфо", "В папке нет файлов.")
            return

        self.sort_progress["maximum"] = len(files)
        self.sort_progress["value"] = 0
        self.sort_status.config(text="Сортировка...")
        self.root.update()

        ok_count = 0; fail_count = 0
        for fname in files:
            _, ext = os.path.splitext(fname)
            ext = ext.lower()
            group = "other"
            for g, exts in ext_groups.items():
                if ext in exts:
                    group = g
                    break

            group_dir = os.path.join(dst, group)
            os.makedirs(group_dir, exist_ok=True)

            src_path = os.path.join(src, fname)
            dst_path = os.path.join(group_dir, fname)

            try:
                shutil.move(src_path, dst_path)
                ok_count += 1
            except Exception as e:
                print(e)
                fail_count += 1

            self.sort_progress["value"] += 1
            self.root.update()

        msg = f"Готово: {ok_count} перемещено, {fail_count} ошибок."
        self.sort_status.config(text=msg)
        messagebox.showinfo("Сортировка завершена", msg)

    # ---------------------- ПЕРЕИМЕНОВАНИЕ ----------------------
    def build_rename_tab(self):
        tk.Label(self.tab_rename, text="Папка с файлами:").pack(pady=5)
        self.rename_in_var = tk.StringVar()
        r_frame = tk.Frame(self.tab_rename)
        r_frame.pack(fill="x", padx=10)
        tk.Entry(r_frame, textvariable=self.rename_in_var, width=40).pack(side="left", padx=(0, 5))
        tk.Button(r_frame, text="Выбрать", command=self.select_rename_in).pack(side="left")

        tk.Label(self.tab_rename, text="Шаблон имени (например, img_{:03d}):").pack(pady=(15, 5))
        self.rename_pattern_var = tk.StringVar(value="file_{:03d}")
        tk.Entry(self.tab_rename, textvariable=self.rename_pattern_var, width=30).pack()

        tk.Label(self.tab_rename, text="Расширение фильтра (оставьте пустым для всех):").pack(pady=(10, 5))
        self.rename_ext_var = tk.StringVar()
        tk.Entry(self.tab_rename, textvariable=self.rename_ext_var, width=10).pack()

        tk.Button(self.tab_rename, text="Переименовать", command=self.run_rename, bg="#dddddd", height=2, font=("Arial", 11, "bold")).pack(pady=15)
        self.rename_progress = ttk.Progressbar(self.tab_rename, mode="determinate")
        self.rename_progress.pack(fill="x", padx=20, pady=5)
        self.rename_status = tk.Label(self.tab_rename, text="", fg="blue")
        self.rename_status.pack()

    def select_rename_in(self):
        f = filedialog.askdirectory()
        if f: self.rename_in_var.set(f)

    def run_rename(self):
        folder = self.rename_in_var.get()
        pattern = self.rename_pattern_var.get()
        ext_filter = self.rename_ext_var.get().lower()

        if not folder:
            messagebox.showerror("Ошибка", "Выберите папку!")
            return

        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if ext_filter:
            files = [f for f in files if f.lower().endswith(ext_filter)]
        files.sort()  # чтобы порядок был предсказуемым

        if not files:
            messagebox.showinfo("Инфо", "Нет файлов для переименования.")
            return

        self.rename_progress["maximum"] = len(files)
        self.rename_progress["value"] = 0
        self.rename_status.config(text="Переименование...")
        self.root.update()

        ok_count = 0
        fail_count = 0

        for i, fname in enumerate(files):
            old_path = os.path.join(folder, fname)
            base, ext = os.path.splitext(fname)

            # если в шаблоне нет места под расширение — добавляем его отдельно
            # простой подход: подставляем номер, потом приклеиваем расширение
            try:
                new_name = pattern.format(i + 1)
                if not new_name.lower().endswith(ext.lower()):
                    new_name += ext
                new_path = os.path.join(folder, new_name)

                # защита от перезаписи: если имя уже занято — пропускаем или меняем логику
                if os.path.exists(new_path) and os.path.realpath(new_path) != os.path.realpath(old_path):
                    # можно добавить суффикс или пропустить
                    fail_count += 1
                    continue

                os.rename(old_path, new_path)
                ok_count += 1
            except Exception as e:
                print(e)
                fail_count += 1

            self.rename_progress["value"] += 1
            self.root.update()

        msg = f"Готово: {ok_count} переименовано, {fail_count} пропущено/ошибок."
        self.rename_status.config(text=msg)
        messagebox.showinfo("Переименование завершено", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = ToolkitApp(root)
    root.mainloop()
