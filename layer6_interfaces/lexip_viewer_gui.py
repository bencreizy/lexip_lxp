# lexip_viewer_gui.py
# Lexip GUI Viewer using PySide6 + QPainter
import sys
import os

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer4_structural_translation"))

from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QVBoxLayout, QPushButton
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QPointF
from lexip_decoder import decode_curves

class LexipViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lexip Viewer")
        self.resize(1000, 800)
        self.curves = []
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = None
        
        layout = QVBoxLayout()
        btn = QPushButton("Open .lxp")
        btn.clicked.connect(self.open_file)
        layout.addWidget(btn)
        self.setLayout(layout)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Lexip File", "", "Lexip Files (*.lxp)")
        if path:
            self.curves = decode_curves(path)
            self.update()

    def paintEvent(self, event):
        if not self.curves:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.offset_x, self.offset_y)
        painter.scale(self.scale, self.scale)
        for curve in self.curves:
            pen = QPen(QColor(*curve["color"]), curve["thickness"])
            painter.setPen(pen)
            pts = curve["points"]
            for i in range(len(pts) - 1):
                painter.drawLine(QPointF(pts[i][0], pts[i][1]), QPointF(pts[i+1][0], pts[i+1][1]))

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.scale *= 1.1 if delta > 0 else (1.0 / 1.1)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
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
        if event.button() == Qt.LeftButton:
            self.dragging = False

def run_viewer():
    app = QApplication(sys.argv)
    viewer = LexipViewer()
    viewer.show()
    sys.exit(app.exec())
