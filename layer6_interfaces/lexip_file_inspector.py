# lexip_file_inspector.py
# Lexip File Inspector GUI stats, heatmaps, metadata
import sys
import numpy as np
import os

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer3_geometric_conditioning"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer4_structural_translation"))

from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QPointF
from lexip_decoder import decode_curves
from lexip_curve_analysis import curve_length, bounding_box, centroid, curvature

class LexipInspector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lexip File Inspector")
        self.resize(1400, 900)
        self.curves = []
        self.selected_curve = None
        self.heatmap_mode = False
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        left = QVBoxLayout()
        
        open_btn = QPushButton("Open .lxp")
        open_btn.clicked.connect(self.open_file)
        left.addWidget(open_btn)
        
        heat_btn = QPushButton("Toggle Heatmap")
        heat_btn.clicked.connect(self.toggle_heatmap)
        left.addWidget(heat_btn)
        
        self.info_label = QLabel("No file loaded")
        left.addWidget(self.info_label)
        
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.select_curve)
        left.addWidget(self.list_widget)
        
        layout.addLayout(left, 1)
        
        self.canvas = QWidget()
        self.canvas.paintEvent = self.paint_canvas
        self.canvas.mousePressEvent = self.mouse_press
        self.canvas.mouseMoveEvent = self.mouse_move
        self.canvas.mouseReleaseEvent = self.mouse_release
        self.canvas.wheelEvent = self.mouse_wheel
        layout.addWidget(self.canvas, 4)
        
        self.setLayout(layout)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Lexip File", "", "Lexip Files (*.lxp)")
        if path:
            self.curves = decode_curves(path)
            self.selected_curve = None
            self.list_widget.clear()
            for i, c in enumerate(self.curves):
                self.list_widget.addItem(f"Curve {i} - length: {curve_length(c['points']):.1f}")
            self.update_stats()
            self.canvas.update()

    def update_stats(self):
        if not self.curves:
            return
        all_pts = []
        for c in self.curves:
            all_pts.extend(c["points"])
        bbox = bounding_box(all_pts)
        cent = centroid(all_pts)
        self.info_label.setText(f"Curves: {len(self.curves)}\nBBox: {bbox}\nCentroid: {cent}")

    def select_curve(self, idx):
        if 0 <= idx < len(self.curves):
            self.selected_curve = idx
            self.canvas.update()

    def toggle_heatmap(self):
        self.heatmap_mode = not self.heatmap_mode
        self.canvas.update()

    def paint_canvas(self, event):
        if not self.curves:
            return
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.offset_x, self.offset_y)
        painter.scale(self.scale, self.scale)
        for idx, curve in enumerate(self.curves):
            pts = curve["points"]
            curv = curvature(pts) if self.heatmap_mode else None
            max_c = max(curv) if curv is not None and len(curv) > 0 and max(curv) > 0 else 1.0
            for i in range(len(pts) - 1):
                if self.heatmap_mode:
                    k = curv[i] / max_c
                    pen = QPen(QColor(int(255 * k), int(255 * (1 - k)), 0), curve["thickness"])
                else:
                    pen = QPen(QColor(*curve["color"]), curve["thickness"])
                if idx == self.selected_curve:
                    pen.setWidthF(curve["thickness"] + 2)
                painter.setPen(pen)
                painter.drawLine(QPointF(pts[i][0], pts[i][1]), QPointF(pts[i+1][0], pts[i+1][1]))

    def mouse_press(self, event):
        self.dragging = True
        self.last_mouse_pos = event.position()

    def mouse_move(self, event):
        if self.dragging and self.last_mouse_pos:
            pos = event.position()
            self.offset_x += pos.x() - self.last_mouse_pos.x()
            self.offset_y += pos.y() - self.last_mouse_pos.y()
            self.last_mouse_pos = pos
            self.canvas.update()

    def mouse_release(self, event):
        self.dragging = False

    def mouse_wheel(self, event):
        delta = event.angleDelta().y()
        self.scale *= 1.1 if delta > 0 else (1.0 / 1.1)
        self.canvas.update()
