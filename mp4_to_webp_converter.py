import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import subprocess
import threading
import os

class FileListFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Scrollable frame for file list
        self.scrollable = ctk.CTkScrollableFrame(self, height=200)
        self.scrollable.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.files_dict = {}  # {path: {'label': label_widget, 'status': status_widget}}

    def add_file(self, file_path):
        if file_path in self.files_dict:
            return False
            
        # Create frame for this file
        file_frame = ctk.CTkFrame(self.scrollable)
        file_frame.pack(fill="x", padx=5, pady=2)
        
        # File name label
        file_label = ctk.CTkLabel(
            file_frame,
            text=Path(file_path).name,
            wraplength=350,
            justify="left"
        )
        file_label.pack(side="left", padx=5)
        
        # Status label
        status_label = ctk.CTkLabel(
            file_frame,
            text="Pending",
            width=100,
            justify="right"
        )
        status_label.pack(side="right", padx=5)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            file_frame,
            text="×",
            width=30,
            command=lambda: self.remove_file(file_path)
        )
        remove_btn.pack(side="right", padx=5)
        
        self.files_dict[file_path] = {
            'frame': file_frame,
            'status': status_label
        }
        return True

    def remove_file(self, file_path):
        if file_path in self.files_dict:
            self.files_dict[file_path]['frame'].destroy()
            del self.files_dict[file_path]

    def clear_files(self):
        for file_data in self.files_dict.values():
            file_data['frame'].destroy()
        self.files_dict.clear()

    def update_status(self, file_path, status):
        if file_path in self.files_dict:
            self.files_dict[file_path]['status'].configure(text=status)

    def get_files(self):
        return list(self.files_dict.keys())

class VideoConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("MP4 to WebP Converter")
        self.geometry("600x600")
        ctk.set_appearance_mode("dark")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="MP4 to WebP Converter",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=20)
        
        # Frame para opções de codificação
        self.encoding_frame = ctk.CTkFrame(self.main_frame)
        self.encoding_frame.pack(fill="x", pady=10)
        
        # Checkbox para modo lossless
        self.lossless_var = ctk.BooleanVar(value=True)
        self.lossless_checkbox = ctk.CTkCheckBox(
            self.encoding_frame,
            text="Lossless Mode",
            variable=self.lossless_var,
            command=self.toggle_compression_mode
        )
        self.lossless_checkbox.pack(side="left", padx=10)
        
        # Label para o slider
        self.compression_label = ctk.CTkLabel(
            self.encoding_frame,
            text="Compression Level (0-6):"
        )
        self.compression_label.pack(side="left", padx=10)
        
        # Slider
        self.compression_slider = ctk.CTkSlider(
            self.encoding_frame,
            from_=0,
            to=6,
            number_of_steps=6,
            command=self.update_compression_label,
            width=200
        )
        self.compression_slider.set(6)
        self.compression_slider.pack(side="left", padx=10)
        
        self.compression_value_label = ctk.CTkLabel(
            self.encoding_frame,
            text="6 (Max)",
            width=70
        )
        self.compression_value_label.pack(side="left", padx=5)
        
        # File selection buttons frame
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", pady=10)
        
        # File selection button
        self.select_button = ctk.CTkButton(
            self.button_frame,
            text="Add Files",
            command=self.select_files,
            height=40,
            width=120
        )
        self.select_button.pack(side="left", padx=5)
        
        # Clear files button
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear All",
            command=self.clear_files,
            height=40,
            width=120,
            fg_color="darkred"
        )
        self.clear_button.pack(side="left", padx=5)
        
        # File list
        self.file_list = FileListFrame(self.main_frame)
        self.file_list.pack(fill="both", expand=True, pady=10)
        
        # Convert button
        self.convert_button = ctk.CTkButton(
            self.main_frame,
            text="Convert All to WebP",
            command=self.start_conversion,
            height=40
        )
        self.convert_button.pack(pady=20)
        
        # Overall progress label
        self.progress_label = ctk.CTkLabel(
            self.main_frame,
            text=""
        )
        self.progress_label.pack(pady=10)

    def toggle_compression_mode(self):
        is_lossless = self.lossless_var.get()
        if is_lossless:
            self.compression_label.configure(text="Compression Level (0-6):")
            self.compression_slider.configure(from_=0, to=6, number_of_steps=6)
            self.compression_slider.set(6)
        else:
            self.compression_label.configure(text="Quality (0-100):")
            self.compression_slider.configure(from_=0, to=100, number_of_steps=100)
            self.compression_slider.set(75)
        self.update_compression_label(self.compression_slider.get())

    def update_compression_label(self, value):
        value_int = int(value)
        if self.lossless_var.get():
            label_text = f"{value_int} ({'Max' if value_int == 6 else 'Min' if value_int == 0 else 'Med'})"
        else:
            label_text = f"Q: {value_int}"
        self.compression_value_label.configure(text=label_text)

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=[("MP4 files", "*.mp4")]
        )
        for file_path in file_paths:
            self.file_list.add_file(file_path)

    def clear_files(self):
        self.file_list.clear_files()

    def convert_single_file(self, file_path):
        try:
            self.file_list.update_status(file_path, "Converting...")
            
            output_path = str(Path(file_path).with_suffix('.webp'))
            compression_value = int(self.compression_slider.get())
            is_lossless = self.lossless_var.get()
            
            command = [
                'ffmpeg',
                '-i', file_path,
                '-vf', f'scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=24'
            ]

            if is_lossless:
                command.extend([
                    '-vcodec', 'libwebp',
                    '-lossless', '1',
                    '-quality', '100',
                    '-compression_level', str(compression_value),
                    '-preset', 'drawing',
                ])
            else:
                command.extend([
                    '-vcodec', 'libwebp',
                    '-lossless', '0',
                    '-quality', str(compression_value),
                    '-preset', 'picture',
                ])

            command.extend([
                '-loop', '0',
                '-metadata', 'alpha_mode="1"',
                '-auto-alt-ref', '0',
                '-pix_fmt', 'yuva420p',
                '-an',
                '-vsync', '0',
                '-y',
                output_path
            ])
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                # Verifica o tamanho do arquivo original e convertido
                original_size = os.path.getsize(file_path)
                converted_size = os.path.getsize(output_path)
                ratio = (converted_size / original_size) * 100
                
                self.file_list.update_status(
                    file_path, 
                    f"Done ({ratio:.1f}%)"
                )
            else:
                self.file_list.update_status(file_path, "Error")
                print(f"FFmpeg error: {stderr}")  # Para debug
            
        except Exception as e:
            self.file_list.update_status(file_path, f"Error: {str(e)}")
            print(f"Exception: {str(e)}")  # Para debug

    def convert_all_files(self):
        try:
            files = self.file_list.get_files()
            total_files = len(files)
            
            self.progress_label.configure(text=f"Converting {total_files} files...")
            self.convert_button.configure(state="disabled")
            self.select_button.configure(state="disabled")
            
            for file_path in files:
                self.convert_single_file(file_path)
            
            self.progress_label.configure(text="All conversions completed!")
            
        except Exception as e:
            self.progress_label.configure(text=f"Error: {str(e)}")
        finally:
            self.convert_button.configure(state="normal")
            self.select_button.configure(state="normal")

    def start_conversion(self):
        thread = threading.Thread(target=self.convert_all_files)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    app = VideoConverter()
    app.mainloop()
