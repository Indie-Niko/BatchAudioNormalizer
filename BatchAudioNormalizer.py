# Copyright (c) 2025 Indie-Niko
# This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.
# You must give appropriate credit and may not use it for commercial purposes.
# License details: https://creativecommons.org/licenses/by-nc/4.0/

import os
import sys
from pathlib import Path
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QProgressBar, QSlider, 
                            QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QColor, QPalette, QFont
from pydub import AudioSegment
import librosa
import soundfile as sf

class AudioNormalizerWorker(QThread):
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, input_files, output_folder, target_format, target_level, 
                 normalize_method="peak", bit_depth=16, stereo=True, sample_rate=44100):
        super().__init__()
        self.input_files = input_files
        self.output_folder = output_folder
        self.target_format = target_format
        self.target_level = target_level
        self.normalize_method = normalize_method
        self.bit_depth = bit_depth
        self.stereo = stereo
        self.sample_rate = sample_rate
        self.is_running = True

        
    def run(self):
        total_files = len(self.input_files)
        for i, file_path in enumerate(self.input_files):
            if not self.is_running:
                break
                
            try:
                file_name = os.path.basename(file_path)
                base_name = os.path.splitext(file_name)[0]
                output_file = os.path.join(self.output_folder, f"{base_name}.{self.target_format}")
                
                # Load audio file
                audio, sr = librosa.load(file_path, sr=None, mono=not self.stereo)
                
                # Normalize audio
                if self.normalize_method == "peak":
                    # Peak normalization
                    if audio.ndim > 1:
                        max_amplitude = np.max(np.abs(audio))
                    else:
                        max_amplitude = np.max(np.abs(audio))
                    
                    target_amplitude = 10 ** (self.target_level / 20.0)
                    normalized_audio = audio * (target_amplitude / max_amplitude) if max_amplitude > 0 else audio
                
                elif self.normalize_method == "rms":
                    # RMS normalization
                    target_rms = 10 ** (self.target_level / 20.0)
                    
                    if audio.ndim > 1:
                        # Stereo
                        current_rms_left = np.sqrt(np.mean(audio[0]**2))
                        current_rms_right = np.sqrt(np.mean(audio[1]**2))
                        gain_left = target_rms / current_rms_left if current_rms_left > 0 else 1.0
                        gain_right = target_rms / current_rms_right if current_rms_right > 0 else 1.0
                        normalized_audio = np.vstack((audio[0] * gain_left, audio[1] * gain_right))
                    else:
                        # Mono
                        current_rms = np.sqrt(np.mean(audio**2))
                        gain = target_rms / current_rms if current_rms > 0 else 1.0
                        normalized_audio = audio * gain
                
                elif self.normalize_method == "loudness":
                    # Loudness normalization (simplified LUFS-based approach)
                    target_loudness = self.target_level
                    
                    # Measure current loudness (simplified approximation)
                    if audio.ndim > 1:
                        mono_audio = np.mean(audio, axis=0)
                    else:
                        mono_audio = audio
                        
                    # Simple loudness estimation
                    current_loudness = 20 * np.log10(np.sqrt(np.mean(mono_audio**2))) - 23
                    gain = 10**((target_loudness - current_loudness) / 20)
                    normalized_audio = audio * gain
                
                # Resample if needed
                if sr != self.sample_rate:
                    normalized_audio = librosa.resample(normalized_audio, orig_sr=sr, target_sr=self.sample_rate)
                
                # Save the normalized audio
                if self.target_format in ["wav", "flac", "ogg"]:
                    subtype = f'PCM_{self.bit_depth}' if self.target_format == "wav" else None
                    sf.write(output_file, normalized_audio.T if audio.ndim > 1 else normalized_audio, 
                             self.sample_rate, subtype=subtype)
                elif self.target_format == "mp3":
                    # For mp3 we need to convert to wav first, then use pydub
                    temp_wav = os.path.join(self.output_folder, f"{base_name}_temp.wav")
                    sf.write(temp_wav, normalized_audio.T if audio.ndim > 1 else normalized_audio, 
                             self.sample_rate)
                    
                    # Convert to mp3 using pydub
                    audio_segment = AudioSegment.from_wav(temp_wav)
                    audio_segment.export(output_file, format="mp3", bitrate=f"{self.bit_depth * 8}k")
                    
                    # Remove temp file
                    os.remove(temp_wav)
                
                # Update progress
                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress)
                self.file_processed.emit(file_name)
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                self.file_processed.emit(f"ERROR: {file_name} - {str(e)}")
        
        self.finished.emit()
        
    def stop(self):
        self.is_running = False


class AudioNormalizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batch Audio normalizer")
        # Set window icon

        # Get the correct path to the icon
        icon_path = self.resource_path("icon.ico")

        self.setWindowIcon(QIcon(icon_path))

        self.setMinimumSize(700, 600)
        
        # Set the dark theme
        self.setup_dark_theme()
        
        # Initialize UI
        self.init_ui()
        
        # State variables
        self.selected_folder = None
        self.audio_files = []
        self.worker = None
    
    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return relative_path
        
    def setup_dark_theme(self):
        dark_palette = QPalette()
        
        # Define colors
        dark_color = QColor(45, 45, 45)
        disabled_color = QColor(70, 70, 70)
        text_color = QColor(200, 200, 200)
        highlight_color = QColor(42, 130, 218)
        
        # Set colors
        dark_palette.setColor(QPalette.Window, dark_color)
        dark_palette.setColor(QPalette.WindowText, text_color)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, dark_color)
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        dark_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.Text, text_color)
        dark_palette.setColor(QPalette.Button, dark_color)
        dark_palette.setColor(QPalette.ButtonText, text_color)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, highlight_color)
        dark_palette.setColor(QPalette.Highlight, highlight_color)
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))
        
        self.setPalette(dark_palette)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2d2d2d;
                color: #c8c8c8;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #c8c8c8;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 15px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #6d6d6d;
                border: 1px solid #3d3d3d;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #3d3d3d;
                color: #c8c8c8;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 3px;
                min-height: 20px;
            }
            QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
                background-color: #4d4d4d;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                width: 1px;
            }
            QSlider::groove:horizontal {
                background: #3d3d3d;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2a82da;
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
          
        """)
        
    def init_ui(self):
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        
        

        main_layout.setContentsMargins(20, 0, 20, 0)
        # App title
        title_label = QLabel("Batch Audio Normalizer")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        main_layout.addSpacing(-20) 

        
        credit_label = QLabel("By indie-niko")
        credit_label.setAlignment(Qt.AlignCenter)
        credit_font = QFont()
        credit_font.setItalic(True)
        credit_label.setFont(credit_font)
        credit_label.setStyleSheet("color: #808080;") 
        
        main_layout.addWidget(credit_label)

        main_layout.setContentsMargins(20, 20, 20, 20)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(self.folder_button)
        main_layout.addLayout(folder_layout)
        
        # Options group box
        options_group = QGroupBox("Normalization Options")
        options_layout = QVBoxLayout(options_group)
        
        # Normalization method
        method_layout = QHBoxLayout()
        method_label = QLabel("Normalization Method:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["RMS", "Peak", "Loudness"])
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo, 1)
        options_layout.addLayout(method_layout)
        
        # Target level
        level_layout = QHBoxLayout()
        level_label = QLabel("Target Level (dB):")
        self.level_spin = QDoubleSpinBox()
        self.level_spin.setRange(-60.0, 0.0)
        self.level_spin.setValue(-5.0)
        self.level_spin.setSingleStep(0.1)
        self.level_spin.setSuffix(" dB")
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_spin, 1)
        options_layout.addLayout(level_layout)
        
        # Output format
        format_layout = QHBoxLayout()
        format_label = QLabel("Output Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["wav", "mp3", "flac", "ogg"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo, 1)
        options_layout.addLayout(format_layout)
        
        # Bit depth
        bit_layout = QHBoxLayout()
        bit_label = QLabel("Bit Depth:")
        self.bit_combo = QComboBox()
        self.bit_combo.addItems(["16", "24", "32"])
        bit_layout.addWidget(bit_label)
        bit_layout.addWidget(self.bit_combo, 1)
        options_layout.addLayout(bit_layout)
        
        # Sample rate
        sample_layout = QHBoxLayout()
        sample_label = QLabel("Sample Rate:")
        self.sample_combo = QComboBox()
        self.sample_combo.addItems(["44100", "48000", "96000"])
        sample_layout.addWidget(sample_label)
        sample_layout.addWidget(self.sample_combo, 1)
        options_layout.addLayout(sample_layout)
        
        # Stereo/Mono
        stereo_layout = QHBoxLayout()
        stereo_label = QLabel("Audio Channels:")
        self.stereo_check = QCheckBox("Keep Stereo")
        self.stereo_check.setChecked(True)
        stereo_layout.addWidget(stereo_label)
        stereo_layout.addWidget(self.stereo_check)
        options_layout.addLayout(stereo_layout)
        
        main_layout.addWidget(options_group)
        
        # Status and progress
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        self.process_button = QPushButton("Process Files")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_files)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_processing)
        
        buttons_layout.addWidget(self.process_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)
        

        self.setCentralWidget(main_widget)
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(folder)
            
            # Get all audio files
            self.audio_files = []
            for ext in ["*.wav", "*.mp3", "*.ogg", "*.flac", "*.aiff", "*.aif"]:
                self.audio_files.extend(list(Path(folder).glob(ext)))
            
            if self.audio_files:
                self.status_label.setText(f"Found {len(self.audio_files)} audio files")
                self.process_button.setEnabled(True)
            else:
                self.status_label.setText("No audio files found in the selected folder")
                self.process_button.setEnabled(False)
    
    def process_files(self):
        if not self.audio_files:
            return
            
        # Create output folder
        output_folder = os.path.join(self.selected_folder, "Normalized Audio")
        os.makedirs(output_folder, exist_ok=True)
        
        # Get settings
        target_format = self.format_combo.currentText()
        target_level = self.level_spin.value()
        normalize_method = self.method_combo.currentText().lower()
        bit_depth = int(self.bit_combo.currentText())
        stereo = self.stereo_check.isChecked()
        sample_rate = int(self.sample_combo.currentText())
        
        # Disable UI elements
        self.folder_button.setEnabled(False)
        self.process_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        
        # Start worker thread
        self.worker = AudioNormalizerWorker(
            self.audio_files, output_folder, target_format, 
            target_level, normalize_method, bit_depth, stereo, sample_rate
        )
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.file_processed.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        
    def update_status(self, filename):
        self.status_label.setText(f"Processing: {filename}")
        
    def processing_finished(self):
        self.progress_bar.setValue(100)
        self.status_label.setText("Processing completed")
        
        # Re-enable UI elements
        self.folder_button.setEnabled(True)
        self.process_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        # Open the output folder
        output_folder = os.path.join(self.selected_folder, "Normalized Audio")
        os.startfile(output_folder)
        
    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            
            self.status_label.setText("Processing canceled")
            self.cancel_button.setEnabled(False)
            self.folder_button.setEnabled(True)
            self.process_button.setEnabled(True)

def main():
    
    app = QApplication(sys.argv)


    window = AudioNormalizerApp()
    
    # Get the correct path to the icon
    icon_path = window.resource_path("icon.ico")

    # Set the taskbar icon
    app.setWindowIcon(QIcon(icon_path))

    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()