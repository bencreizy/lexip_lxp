# lexip_viewer_gui.py
# Lexip Viewer GUI using PySide6 - read-only curve visualization
import numpy as np

from PySide6.QtWidgets import (QApplication, QWidget, QFileDialog, QVBoxLayout, 
                               QPushButton, QHBoxLayout, QLabel)
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QPointF

from .lexip_decoder import decode_curves
from .lexip_curve_analysis import curve_length, bounding_box, centroid

class LexipViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lexip Viewer")
        self.resize(1200, 900)
        self.curves = []
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.dragging = False
        self.last_mouse_pos = None
        self.selected_curve = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        btn_row = QHBoxLayout()
        
        open_btn = QPushButton("Open .lxp")
        open_btn.clicked.connect(self.open_file)
        btn_row.addWidget(open_btn)
        
        self.info_label = QLabel("No file loaded")
        btn_row.addWidget(self.info_label)
        layout.addLayout(btn_row)
        
        self.setLayout(layout)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Lexip File", "", "Lexip Files (*.lxp)")
        if path:
            self.curves = decode_curves(path)
            self.selected_curve = None
            self.update_stats()
            self.update()

    def update_stats(self):
        if not self.curves:
            self.info_label.setText("No curves loaded")
            return
        
        all_pts = []
        for c in self.curves:
            all_pts.extend(c["points"])
            
        if all_pts:
            pts_arr = np.asarray(all_pts, dtype=np.float64)
            bbox = bounding_box(pts_arr)
            cent = centroid(pts_arr)
        else:
            bbox = (0.0, 0.0, 0.0, 0.0)
            cent = (0.0, 0.0)
            
        self.info_label.setText(f"Curves: {len(self.curves)} | BBox: {bbox} | Centroid: {cent}")

    def paintEvent(self, event):
        if not self.curves:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.offset_x, self.offset_y)
        painter.scale(self.scale, self.scale)
        
        for idx, curve in enumerate(self.curves):
            color = QColor(255, 0, 0) if idx == self.selected_curve else QColor(*curve["color"])
            painter.setPen(QPen(color, curve["thickness"]))
            pts = curve["points"]
            
            for i in range(len(pts) - 1):
                painter.drawLine(QPointF(pts[i][0], pts[i][1]), QPointF(pts[i+1][0], pts[i+1][1]))
                
            if idx == self.selected_curve:
                painter.setPen(QPen(Qt.green, 6))
                for pt in pts:
                    painter.drawPoint(QPointF(pt[0], pt[1]))

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

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.scale *= 1.1 if delta > 0 else (1.0 / 1.1)
        self.update()
