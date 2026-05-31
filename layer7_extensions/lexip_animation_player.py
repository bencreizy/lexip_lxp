# lexip_animation_player.py
# Real-time Lexip Animation Player using PySide6
import sys
import os

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer7_extensions"))

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QSlider, QLabel
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QTimer, QPointF
from lexip_timeline import LexipTimeline

class LexipAnimationPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lexip Animation Player")
        self.resize(1200, 900)
        self.timeline = None
        self.current_time = 0.0
        self.playing = False
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.last_mouse_pos = None
        self.dragging = False
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def init_ui(self):
        layout = QVBoxLayout()
        controls = QHBoxLayout()
        
        open_btn = QPushButton("Open .lxa")
        open_btn.clicked.connect(self.open_file)
        controls.addWidget(open_btn)
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        controls.addWidget(self.play_btn)
        
        self.time_label = QLabel("t = 0.00")
        controls.addWidget(self.time_label)
        layout.addLayout(controls)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.valueChanged.connect(self.slider_changed)
        layout.addWidget(self.slider)
        
        self.setLayout(layout)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Animation", "", "Lexip Animation (*.lxa)")
        if path:
            self.timeline = LexipTimeline.load_lxa(path)
            self.current_time = 0.0
            self.update()

    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.setText("Pause" if self.playing else "Play")

    def update_frame(self):
        if self.timeline and self.playing:
            self.current_time += 1.0 / 60.0
            if self.current_time > self.timeline.duration:
                self.current_time = 0.0
            self.slider.blockSignals(True)
            self.slider.setValue(int((self.current_time / self.timeline.duration) * 1000))
            self.slider.blockSignals(False)
            self.update()

    def slider_changed(self, value):
        if self.timeline:
            self.current_time = (value / 1000.0) * self.timeline.duration
            self.update()

    def paintEvent(self, event):
        if not self.timeline:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.offset_x, self.offset_y)
        painter.scale(self.scale, self.scale)
        state = self.timeline.evaluate(self.current_time)
        self.time_label.setText(f"t = {self.current_time:.2f}")
        for cid, curve in state.items():
            painter.setPen(QPen(QColor(*curve["color"]), curve["thickness"]))
            pts = curve["points"]
            for i in range(len(pts) - 1):
                painter.drawLine(QPointF(pts[i][0], pts[i][1]), QPointF(pts[i+1][0], pts[i+1][1]))

    def mousePressEvent(self, event):
        self.dragging = True
        self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.dragging and self.last_mouse_pos:
            pos = event.position()
            self.offset_x += pos.x() - self.last_mouse_pos.x()
            self.offset_y += pos.y() - self.last_mouse_pos.y()
            self.last_mouse_pos = pos
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False
