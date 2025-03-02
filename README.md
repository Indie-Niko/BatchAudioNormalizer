# Batch Audio Normalizer & Converter 🎶
[![Version](https://img.shields.io/github/v/release/Indie-Niko/BatchAudioNormalizer?display_name=release)](https://github.com/Indie-Niko/BatchAudioNormalizer/releases/latest)
[![License](https://img.shields.io/github/license/Indie-Niko/BatchAudioNormalizer)](https://github.com/Indie-Niko/BatchAudioNormalizer/blob/main/LICENSE)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
[![Issues](https://img.shields.io/github/issues/Indie-Niko/BatchAudioNormalizer)](https://github.com/Indie-Niko/BatchAudioNormalizer/issues)

A Python application to batch normalize and convert audio files to different formats. The app allows you to normalize audio to a desired dB level and convert between `.wav`, `.mp3`, `.flac`, and `.ogg` formats. A pre-built executable is included for easy use, and the Python script is also available for custom modifications.

![image](https://github.com/user-attachments/assets/03527d83-3e97-4b55-ad9b-cc52a915608b)

## Features:
- **Batch Normalize Audio**: Normalize multiple audio files to a target dB level.
- **Format Conversion**: Convert audio files between `.wav`, `.mp3`, `.flac`, and `.ogg`.
- **Customizable Settings**:
  - **Target Format**: Choose the output format (`.wav`, `.mp3`, `.flac`, `.ogg`).
  - **Target dB Level**: Normalize audio files to the desired dB level.
  - **Normalization Method**: Select between different normalization methods (e.g., peak or RMS).
  - **Bit Depth**: Set the bit depth for output files.
  - **Stereo or Mono**: Choose between stereo or mono output.
  - **Sample Rate**: Select the sample rate for the output files.



## Download the Executable
For quick usage, download the pre-built `.exe` for Windows from the link below. This allows you to run the app without needing to install Python or dependencies.

[Download BatchAudioNormalizer.zip (Latest Version)](https://github.com/Indie-Niko/BatchAudioNormalizer/releases/download/Latest/BatchAudioNormalizer.zip)

## Running from Source
If you'd like to run the app from the source code or modify it for your own needs, follow the instructions below:

### Prerequisites:
- Python 3.x installed (can be downloaded from [python.org](https://www.python.org/))
- A virtual environment (recommended)

### Installation:
1. Clone the repository:
   ```sh
   git clone https://github.com/Indie-Niko/BatchAudioNormalizer.git
   ```

2. Navigate to the project directory:
   ```sh
   cd BatchAudioNormalizer
   ```

3. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

4. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Script:
After installation, run the script with:
```sh
python BatchAudioNormalizer.py
```

### Custom Modifications:
Feel free to modify the Python script (`BatchAudioNormalizer.py`) for your specific needs.

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

## Tags
`audio-normalizer` `batch-processing` `audio-converter` `python` `pyqt5` `pydub` `librosa` `soundfile` `numpy` `executable` `windows`

## Author
**Indie-Niko**  
[GitHub Profile](https://github.com/Indie-Niko)

## Contact
For support or contributions, feel free to open an issue on [GitHub](https://github.com/Indie-Niko/BatchAudioNormalizer/issues).
