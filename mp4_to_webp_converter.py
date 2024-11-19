import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import subprocess
import threading
import os
import json

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
        
        self.config_file = Path.home() / '.mp4_to_webp_converter.json'
        self.presets = {
            "Banner Ads - High Quality": {
                "lossless": True,
                "compression": 6,
                "keep_fps": False,
                "fps": "24",
                "use_all_frames": True,
                "start_frame": "0",
                "end_frame": ""
            },
            "Banner Ads - Balanced": {
                "lossless": False,
                "compression": 85,
                "keep_fps": False,
                "fps": "20",
                "use_all_frames": True,
                "start_frame": "0",
                "end_frame": ""
            },
            "Banner Ads - Small Size": {
                "lossless": False,
                "compression": 65,
                "keep_fps": False,
                "fps": "15",
                "use_all_frames": True,
                "start_frame": "0",
                "end_frame": ""
            }
        }

        # Configure window
        self.title("MP4 to WebP Converter")
        self.geometry("800x700")  # Increased window size
        self.minsize(700, 600)    # Added minimum window size
        ctk.set_appearance_mode("dark")
        
        # Create main frame with padding
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Title label with improved styling
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="MP4 to WebP Converter",
            font=("Arial", 28, "bold")
        )
        self.title_label.pack(pady=(20, 10))
        
        # Add Presets Section before Settings Section
        self.presets_frame = ctk.CTkFrame(self.main_frame)
        self.presets_frame.pack(fill="x", padx=10, pady=10)
        
        self.presets_title = ctk.CTkLabel(
            self.presets_frame,
            text="Presets",
            font=("Arial", 16, "bold")
        )
        self.presets_title.pack(pady=5)
        
        # Presets dropdown
        self.preset_var = ctk.StringVar(value="Custom")
        self.preset_dropdown = ctk.CTkOptionMenu(
            self.presets_frame,
            values=["Custom"] + list(self.presets.keys()),
            variable=self.preset_var,
            command=self.load_preset,
            width=200
        )
        self.preset_dropdown.pack(pady=5)
        
        # Save/Load Config buttons
        self.config_buttons_frame = ctk.CTkFrame(self.presets_frame)
        self.config_buttons_frame.pack(fill="x", pady=5)
        
        self.save_config_btn = ctk.CTkButton(
            self.config_buttons_frame,
            text="Save Current Settings",
            command=self.save_config,
            width=150
        )
        self.save_config_btn.pack(side="left", padx=5)
        
        self.save_preset_btn = ctk.CTkButton(
            self.config_buttons_frame,
            text="Save as New Preset",
            command=self.save_new_preset,
            width=150
        )
        self.save_preset_btn.pack(side="right", padx=5)
        
        # Settings Section
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.pack(fill="x", padx=10, pady=10)
        
        # Settings Title
        self.settings_title = ctk.CTkLabel(
            self.settings_frame,
            text="Conversion Settings",
            font=("Arial", 16, "bold")
        )
        self.settings_title.pack(pady=5)
        
        # Encoding Options Frame
        self.encoding_frame = ctk.CTkFrame(self.settings_frame)
        self.encoding_frame.pack(fill="x", padx=10, pady=5)
        
        # Lossless checkbox with tooltip
        self.lossless_var = ctk.BooleanVar(value=True)
        self.lossless_checkbox = ctk.CTkCheckBox(
            self.encoding_frame,
            text="Lossless Mode",
            variable=self.lossless_var,
            command=self.toggle_compression_mode,
            font=("Arial", 12)
        )
        self.lossless_checkbox.pack(side="left", padx=10, pady=5)
        
        # Compression controls in a separate frame
        self.compression_control_frame = ctk.CTkFrame(self.encoding_frame)
        self.compression_control_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        self.compression_label = ctk.CTkLabel(
            self.compression_control_frame,
            text="Compression Level (0-6):",
            font=("Arial", 12)
        )
        self.compression_label.pack(side="left", padx=5)
        
        self.compression_slider = ctk.CTkSlider(
            self.compression_control_frame,
            from_=0,
            to=6,
            number_of_steps=6,
            command=self.update_compression_label,
            width=200
        )
        self.compression_slider.set(6)
        self.compression_slider.pack(side="left", padx=10)
        
        self.compression_value_label = ctk.CTkLabel(
            self.compression_control_frame,
            text="6 (Max)",
            width=70,
            font=("Arial", 12)
        )
        self.compression_value_label.pack(side="left", padx=5)
        
        # Frame Controls Section
        self.frames_section = ctk.CTkFrame(self.main_frame)
        self.frames_section.pack(fill="x", padx=10, pady=10)
        
        self.frames_title = ctk.CTkLabel(
            self.frames_section,
            text="Frame Settings",
            font=("Arial", 16, "bold")
        )
        self.frames_title.pack(pady=5)
        
        # Video Info Frame
        self.video_info_frame = ctk.CTkFrame(self.frames_section)
        self.video_info_frame.pack(fill="x", padx=10, pady=5)
        
        self.fps_info_label = ctk.CTkLabel(
            self.video_info_frame,
            text="Original FPS: -",
            font=("Arial", 12)
        )
        self.fps_info_label.pack(side="left", padx=10)
        
        self.frames_info_label = ctk.CTkLabel(
            self.video_info_frame,
            text="Total Frames: -",
            font=("Arial", 12)
        )
        self.frames_info_label.pack(side="left", padx=10)
        
        # Frame Selection Controls
        self.frame_controls = ctk.CTkFrame(self.frames_section)
        self.frame_controls.pack(fill="x", padx=10, pady=5)
        
        # Use all frames checkbox
        self.use_all_frames_var = ctk.BooleanVar(value=True)
        self.use_all_frames_checkbox = ctk.CTkCheckBox(
            self.frame_controls,
            text="Use all frames",
            variable=self.use_all_frames_var,
            command=self.toggle_frame_entries,
            font=("Arial", 12)
        )
        self.use_all_frames_checkbox.pack(side="left", padx=10)
        
        # Frame range entries
        self.frame_range_frame = ctk.CTkFrame(self.frame_controls)
        self.frame_range_frame.pack(side="left", padx=10)
        
        self.start_frame_label = ctk.CTkLabel(
            self.frame_range_frame,
            text="Start:",
            font=("Arial", 12)
        )
        self.start_frame_label.pack(side="left", padx=5)
        
        self.start_frame_var = ctk.StringVar(value="0")
        self.start_frame_entry = ctk.CTkEntry(
            self.frame_range_frame,
            width=70,
            textvariable=self.start_frame_var
        )
        self.start_frame_entry.pack(side="left", padx=5)
        
        self.end_frame_label = ctk.CTkLabel(
            self.frame_range_frame,
            text="End:",
            font=("Arial", 12)
        )
        self.end_frame_label.pack(side="left", padx=5)
        
        self.end_frame_var = ctk.StringVar(value="")
        self.end_frame_entry = ctk.CTkEntry(
            self.frame_range_frame,
            width=70,
            textvariable=self.end_frame_var
        )
        self.end_frame_entry.pack(side="left", padx=5)
        
        # FPS Controls
        self.fps_frame = ctk.CTkFrame(self.frames_section)
        self.fps_frame.pack(fill="x", padx=10, pady=5)
        
        self.keep_fps_var = ctk.BooleanVar(value=False)
        self.keep_fps_checkbox = ctk.CTkCheckBox(
            self.fps_frame,
            text="Keep original FPS",
            variable=self.keep_fps_var,
            command=self.toggle_fps_entry,
            font=("Arial", 12)
        )
        self.keep_fps_checkbox.pack(side="left", padx=10)
        
        self.fps_control_frame = ctk.CTkFrame(self.fps_frame)
        self.fps_control_frame.pack(side="left", padx=10)
        
        self.fps_label = ctk.CTkLabel(
            self.fps_control_frame,
            text="Output FPS:",
            font=("Arial", 12)
        )
        self.fps_label.pack(side="left", padx=5)
        
        self.fps_var = ctk.StringVar(value="24")
        self.fps_entry = ctk.CTkEntry(
            self.fps_control_frame,
            width=70,
            textvariable=self.fps_var
        )
        self.fps_entry.pack(side="left", padx=5)

        # File Management Section
        self.file_section = ctk.CTkFrame(self.main_frame)
        self.file_section.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File section header frame
        self.file_header_frame = ctk.CTkFrame(self.file_section)
        self.file_header_frame.pack(fill="x", padx=5, pady=5)
        
        self.file_section_title = ctk.CTkLabel(
            self.file_header_frame,
            text="File Management",
            font=("Arial", 16, "bold")
        )
        self.file_section_title.pack(side="left", pady=5, padx=5)
        
        # File selection buttons
        self.select_button = ctk.CTkButton(
            self.file_header_frame,
            text="Add Files",
            command=self.select_files,
            width=120,
            font=("Arial", 12),
            fg_color="#2B7A0B",
            hover_color="#1E5508"
        )
        self.select_button.pack(side="right", padx=5)
        
        self.clear_button = ctk.CTkButton(
            self.file_header_frame,
            text="Clear All",
            command=self.clear_files,
            width=120,
            font=("Arial", 12),
            fg_color="#8B0000",
            hover_color="#660000"
        )
        self.clear_button.pack(side="right", padx=5)
        
        # File List Frame
        self.file_list = FileListFrame(self.file_section)
        self.file_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Convert button and progress frame
        self.convert_frame = ctk.CTkFrame(self.file_section)
        self.convert_frame.pack(fill="x", padx=5, pady=5)
        
        self.convert_button = ctk.CTkButton(
            self.convert_frame,
            text="Convert",
            command=self.start_conversion,
            height=40,
            width=120,
            font=("Arial", 12, "bold"),
            fg_color="#1E88E5",
            hover_color="#1565C0"
        )
        self.convert_button.pack(side="left", padx=5)
        
        self.progress_label = ctk.CTkLabel(
            self.convert_frame,
            text="",
            font=("Arial", 12)
        )
        self.progress_label.pack(side="left", padx=5)

        # Load saved settings
        self.load_config()

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
            if value_int == 6:
                label_text = "6 (Max)"
            elif value_int == 0:
                label_text = "0 (Min)"
            else:
                label_text = f"{value_int}"
        else:
            label_text = f"Quality: {value_int}"
        self.compression_value_label.configure(text=label_text)

    def toggle_fps_entry(self):
        if self.keep_fps_var.get():
            self.fps_entry.configure(state="disabled")
            self.fps_label.configure(text_color="gray")
        else:
            self.fps_entry.configure(state="normal")
            self.fps_label.configure(text_color="white")

    def toggle_frame_entries(self):
        state = "disabled" if self.use_all_frames_var.get() else "normal"
        text_color = "gray" if self.use_all_frames_var.get() else "white"
        
        self.start_frame_entry.configure(state=state)
        self.end_frame_entry.configure(state=state)
        self.start_frame_label.configure(text_color=text_color)
        self.end_frame_label.configure(text_color=text_color)

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
                '-vf', filter_string,
                '-threads', '8',  # Utilizar 8 threads para processamento
                '-movflags', '+faststart',  # Otimização para início rápido
            ]

            if is_lossless:
                command.extend([
                    '-vcodec', 'libwebp',
                    '-lossless', '1',
                    '-quality', '100',
                    '-compression_level', str(compression_value),
                    '-preset', 'drawing',
                    '-tune', 'animation',  # Otimizado para animações
                ])
            else:
                command.extend([
                    '-vcodec', 'libwebp',
                    '-lossless', '0',
                    '-quality', str(compression_value),
                    '-preset', 'picture',
                    '-tune', 'animation',  # Otimizado para animações
                ])

            command.extend([
                '-loop', '0',
                '-metadata', 'alpha_mode="1"',
                '-auto-alt-ref', '0',
                '-pix_fmt', 'yuva420p',
                '-an',  # Remove áudio
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

    def save_config(self):
        """Save current settings to config file"""
        config = {
            "lossless": self.lossless_var.get(),
            "compression": self.compression_slider.get(),
            "keep_fps": self.keep_fps_var.get(),
            "fps": self.fps_var.get(),
            "use_all_frames": self.use_all_frames_var.get(),
            "start_frame": self.start_frame_var.get(),
            "end_frame": self.end_frame_var.get(),
            "last_preset": self.preset_var.get(),
            "presets": self.presets
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            self.show_message("Settings saved successfully!")
        except Exception as e:
            self.show_message(f"Error saving settings: {str(e)}", "error")

    def load_config(self):
        """Load settings from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Update presets with saved ones
                if "presets" in config:
                    self.presets.update(config["presets"])
                    self.preset_dropdown.configure(
                        values=["Custom"] + list(self.presets.keys())
                    )
                
                # Load last used preset if available
                if "last_preset" in config and config["last_preset"] != "Custom":
                    self.preset_var.set(config["last_preset"])
                    self.load_preset(config["last_preset"])
                else:
                    # Load individual settings
                    self.apply_settings(config)
        except Exception as e:
            print(f"Error loading config: {str(e)}")

    def load_preset(self, preset_name):
        """Load settings from selected preset"""
        if preset_name == "Custom":
            return
            
        if preset_name in self.presets:
            self.apply_settings(self.presets[preset_name])

    def apply_settings(self, settings):
        """Apply the given settings to the UI"""
        if "lossless" in settings:
            self.lossless_var.set(settings["lossless"])
            self.toggle_compression_mode()
        
        if "compression" in settings:
            self.compression_slider.set(settings["compression"])
            self.update_compression_label(settings["compression"])
            
        if "keep_fps" in settings:
            self.keep_fps_var.set(settings["keep_fps"])
            self.toggle_fps_entry()
            
        if "fps" in settings:
            self.fps_var.set(settings["fps"])
            
        if "use_all_frames" in settings:
            self.use_all_frames_var.set(settings["use_all_frames"])
            self.toggle_frame_entries()
            
        if "start_frame" in settings:
            self.start_frame_var.set(settings["start_frame"])
            
        if "end_frame" in settings:
            self.end_frame_var.set(settings["end_frame"])

    def save_new_preset(self):
        """Save current settings as a new preset"""
        dialog = ctk.CTkInputDialog(
            text="Enter preset name:",
            title="Save New Preset"
        )
        preset_name = dialog.get_input()
        
        if preset_name:
            self.presets[preset_name] = {
                "lossless": self.lossless_var.get(),
                "compression": self.compression_slider.get(),
                "keep_fps": self.keep_fps_var.get(),
                "fps": self.fps_var.get(),
                "use_all_frames": self.use_all_frames_var.get(),
                "start_frame": self.start_frame_var.get(),
                "end_frame": self.end_frame_var.get()
            }
            
            self.preset_dropdown.configure(
                values=["Custom"] + list(self.presets.keys())
            )
            self.preset_var.set(preset_name)
            self.save_config()
            self.show_message(f"Preset '{preset_name}' saved!")

    def show_message(self, message, level="info"):
        """Show a popup message"""
        if level == "error":
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Information", message)

if __name__ == "__main__":
    app = VideoConverter()
    app.mainloop()
