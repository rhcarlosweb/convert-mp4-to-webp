# MP4 to WebP Converter

A powerful desktop application built with Python and CustomTkinter that converts MP4 videos to WebP animations with advanced optimization options.

![Application Screenshot](screenshot.png) <!-- You should add a screenshot of your app here -->

## Features

- **User-Friendly Interface**: Clean and modern dark-themed GUI
- **Batch Processing**: Convert multiple MP4 files simultaneously
- **Customizable Settings**:
  - Lossless/Lossy compression options
  - Adjustable compression levels and quality
  - FPS control (keep original or set custom)
  - Frame range selection
- **Preset System**:
  - Built-in presets for common use cases
  - Save and load custom presets
  - Quick switching between configurations
- **Real-time Status**: Monitor conversion progress and file size reduction
- **Configuration Persistence**: Automatically saves your preferred settings

## Pre-built Presets

- **Banner Ads - High Quality**: Lossless compression optimized for maximum quality
- **Banner Ads - Balanced**: Balanced settings for good quality and file size
- **Banner Ads - Small Size**: Optimized for minimal file size while maintaining acceptable quality

## Requirements

- Python 3.7+
- FFmpeg (must be installed and accessible in system PATH)
- Required Python packages:
  ```
  customtkinter
  pillow
  ```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/mp4-to-webp-converter.git
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg:
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent

## Usage

1. Run the application:
   ```bash
   python mp4_to_webp_converter.py
   ```

2. Click "Add Files" to select MP4 files for conversion

3. Adjust conversion settings:
   - Choose between lossless and lossy compression
   - Set compression level or quality
   - Configure FPS settings
   - Select specific frame ranges (optional)

4. Click "Convert" to start the process

5. Monitor progress in the file list

## Advanced Settings

### Compression Modes

- **Lossless Mode**: 
  - Compression levels from 0-6
  - Level 6 provides best compression with no quality loss
  - Ideal for animations requiring perfect quality

- **Lossy Mode**:
  - Quality settings from 0-100
  - Higher values maintain better quality at larger file sizes
  - Recommended range: 65-85 for balanced results

### Frame Control

- **Use All Frames**: Convert the entire video
- **Frame Range**: Select specific start and end frames
- **FPS Options**: 
  - Keep original video FPS
  - Set custom FPS for output

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI components
- [FFmpeg](https://ffmpeg.org/) for the powerful video processing capabilities

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/mp4-to-webp-converter/issues) on GitHub.