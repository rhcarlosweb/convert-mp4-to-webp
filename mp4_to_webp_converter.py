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
        
        # Frame para controles de Frames e FPS
        self.frames_control_frame = ctk.CTkFrame(self.main_frame)
        self.frames_control_frame.pack(fill="x", pady=10, padx=10)
        
        # Frame Info (Original)
        self.frame_info_frame = ctk.CTkFrame(self.frames_control_frame)
        self.frame_info_frame.pack(fill="x", pady=5)
        
        self.fps_info_label = ctk.CTkLabel(
            self.frame_info_frame,
            text="Original FPS: -",
            width=120
        )
        self.fps_info_label.pack(side="left", padx=5)
        
        self.frames_info_label = ctk.CTkLabel(
            self.frame_info_frame,
            text="Total Frames: -",
            width=120
        )
        self.frames_info_label.pack(side="left", padx=5)
        
        # Frame Selection Frame
        self.frame_selection_frame = ctk.CTkFrame(self.frames_control_frame)
        self.frame_selection_frame.pack(fill="x", pady=5)
        
        # Start Frame
        self.start_frame_label = ctk.CTkLabel(
            self.frame_selection_frame,
            text="Start Frame:",
            width=80
        )
        self.start_frame_label.pack(side="left", padx=5)
        
        self.start_frame_var = ctk.StringVar(value="0")
        self.start_frame_entry = ctk.CTkEntry(
            self.frame_selection_frame,
            width=60,
            textvariable=self.start_frame_var
        )
        self.start_frame_entry.pack(side="left", padx=5)
        
        # End Frame
        self.end_frame_label = ctk.CTkLabel(
            self.frame_selection_frame,
            text="End Frame:",
            width=80
        )
        self.end_frame_label.pack(side="left", padx=5)
        
        self.end_frame_var = ctk.StringVar(value="")
        self.end_frame_entry = ctk.CTkEntry(
            self.frame_selection_frame,
            width=60,
            textvariable=self.end_frame_var
        )
        self.end_frame_entry.pack(side="left", padx=5)
        
        # FPS Control Frame
        self.fps_control_frame = ctk.CTkFrame(self.frames_control_frame)
        self.fps_control_frame.pack(fill="x", pady=5)
        
        # Output FPS
        self.fps_label = ctk.CTkLabel(
            self.fps_control_frame,
            text="Output FPS:",
            width=80
        )
        self.fps_label.pack(side="left", padx=5)
        
        self.fps_var = ctk.StringVar(value="24")
        self.fps_entry = ctk.CTkEntry(
            self.fps_control_frame,
            width=60,
            textvariable=self.fps_var
        )
        self.fps_entry.pack(side="left", padx=5)
        
        # Keep original FPS checkbox
        self.keep_fps_var = ctk.BooleanVar(value=False)
        self.keep_fps_checkbox = ctk.CTkCheckBox(
            self.fps_control_frame,
            text="Keep original FPS",
            variable=self.keep_fps_var,
            command=self.toggle_fps_entry
        )
        self.keep_fps_checkbox.pack(side="left", padx=10)
        
        # Use all frames checkbox
        self.use_all_frames_var = ctk.BooleanVar(value=True)
        self.use_all_frames_checkbox = ctk.CTkCheckBox(
            self.fps_control_frame,
            text="Use all frames",
            variable=self.use_all_frames_var,
            command=self.toggle_frame_entries
        )
        self.use_all_frames_checkbox.pack(side="left", padx=10)

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

    def toggle_fps_entry(self):
        if self.keep_fps_var.get():
            self.fps_entry.configure(state="disabled")
        else:
            self.fps_entry.configure(state="normal")

    def toggle_frame_entries(self):
        state = "disabled" if self.use_all_frames_var.get() else "normal"
        self.start_frame_entry.configure(state=state)
        self.end_frame_entry.configure(state=state)

    def get_video_info(self, file_path):
        """Get video FPS and frame count using FFprobe"""
        try:
            # Get FPS
            fps_cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=r_frame_rate',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            fps_output = subprocess.check_output(fps_cmd, universal_newlines=True).strip()
            num, den = map(int, fps_output.split('/'))
            fps = num / den

            # Get frame count
            frames_cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-count_packets',
                '-show_entries', 'stream=nb_read_packets',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            frame_count = int(subprocess.check_output(frames_cmd, universal_newlines=True).strip())

            return fps, frame_count
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None, None

    def select_files(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=[("MP4 files", "*.mp4")]
        )
        for file_path in file_paths:
            if self.file_list.add_file(file_path):
                # Get and display video info for the first file
                if len(self.file_list.get_files()) == 1:
                    fps, frames = self.get_video_info(file_path)
                    if fps and frames:
                        self.fps_info_label.configure(text=f"Original FPS: {fps:.2f}")
                        self.frames_info_label.configure(text=f"Frames: {frames}")
                        if self.keep_fps_var.get():
                            self.fps_var.set(f"{fps:.2f}")

    def clear_files(self):
        self.file_list.clear_files()

    def convert_single_file(self, file_path):
        try:
            self.file_list.update_status(file_path, "Converting...")
            
            output_path = str(Path(file_path).with_suffix('.webp'))
            compression_value = int(self.compression_slider.get())
            is_lossless = self.lossless_var.get()
            
            # Prepare frame selection and FPS filter
            filter_parts = ['scale=trunc(iw/2)*2:trunc(ih/2)*2']
            
            # Add frame selection if needed
            if not self.use_all_frames_var.get():
                try:
                    start_frame = int(self.start_frame_var.get())
                    end_frame = int(self.end_frame_var.get())
                    if start_frame >= 0 and end_frame > start_frame:
                        filter_parts.append(f'select=between(n\\,{start_frame}\\,{end_frame})')
                except ValueError:
                    self.file_list.update_status(file_path, "Invalid frame numbers")
                    return
            
            # Add FPS filter
            if not self.keep_fps_var.get():
                try:
                    target_fps = float(self.fps_var.get())
                    filter_parts.append(f'fps={target_fps}')
                except ValueError:
                    self.file_list.update_status(file_path, "Invalid FPS value")
                    return
            
            # Combine filters
            filter_string = ','.join(filter_parts)
            
            command = [
                'ffmpeg',
                '-i', file_path,
                '-vf', filter_string
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
            
            print(f"FFmpeg command: {' '.join(command)}")  # Para debug
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                original_size = os.path.getsize(file_path)
                converted_size = os.path.getsize(output_path)
                ratio = (converted_size / original_size) * 100
                
                self.file_list.update_status(
                    file_path, 
                    f"Done ({ratio:.1f}%)"
                )
            else:
                self.file_list.update_status(file_path, "Error")
                print(f"FFmpeg error: {stderr}")
            
        except Exception as e:
            self.file_list.update_status(file_path, f"Error: {str(e)}")
            print(f"Exception: {str(e)}")

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
