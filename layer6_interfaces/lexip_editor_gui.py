# lexip_editor_gui.py
# Full Lexip Editor GUI using PySide6
import copy
import numpy as np

from PySide6.QtWidgets import (QApplication, QWidget, QFileDialog, QVBoxLayout, 
                               QPushButton, QColorDialog, QHBoxLayout, QLabel, QSlider)
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QPointF

from .lexip_decoder import decode_curves
from .lexip_format import save_lxp

class LexipEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lexip Editor")
        self.resize(1200, 900)
        self.curves = []
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.dragging_canvas = False
        self.dragging_point = False
        self.dragging_curve = False
        self.selected_curve = None
        self.selected_point = None
        self.last_mouse_pos = None
        self.undo_stack = []
        self.redo_stack = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        btn_row = QHBoxLayout()
        
        open_btn = QPushButton("Open .lxp")
        open_btn.clicked.connect(self.open_file)
        btn_row.addWidget(open_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_file)
        btn_row.addWidget(save_btn)
        
        del_btn = QPushButton("Delete Curve")
        del_btn.clicked.connect(self.delete_selected_curve)
        btn_row.addWidget(del_btn)

        color_btn = QPushButton("Color")
        color_btn.clicked.connect(self.change_color)
        btn_row.addWidget(color_btn)
        
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.undo)
        btn_row.addWidget(undo_btn)
        
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.redo)
        btn_row.addWidget(redo_btn)
        
        layout.addLayout(btn_row)
        
        thick_row = QHBoxLayout()
        thick_row.addWidget(QLabel("Thickness"))
        self.thick_slider = QSlider(Qt.Horizontal)
        self.thick_slider.setRange(1, 20)
        self.thick_slider.valueChanged.connect(self.change_thickness)
        thick_row.addWidget(self.thick_slider)
        layout.addLayout(thick_row)
        
        self.setLayout(layout)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Lexip File", "", "Lexip Files (*.lxp)")
        if path:
            self.curves = decode_curves(path)
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.update()

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Lexip File", "", "Lexip Files (*.lxp)")
        if path:
            save_lxp(self.curves, path)

    def push_undo(self):
        # Maximum history threshold constraint to keep memory consumption zero-drift
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.undo_stack.append(copy.deepcopy(self.curves))
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(copy.deepcopy(self.curves))
            self.curves = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(copy.deepcopy(self.curves))
            self.curves = self.redo_stack.pop()
            self.update()

    def delete_selected_curve(self):
        if self.selected_curve is not None:
            self.push_undo()
            self.curves.pop(self.selected_curve)
            self.selected_curve = None
            self.selected_point = None
            self.update()

    def change_color(self):
        if self.selected_curve is not None:
            color = QColorDialog.getColor()
            if color.isValid():
                self.push_undo()
                self.curves[self.selected_curve]["color"] = [color.red(), color.green(), color.blue()]
                self.update()

    def change_thickness(self):
        if self.selected_curve is not None:
            self.push_undo()
            self.curves[self.selected_curve]["thickness"] = float(self.thick_slider.value())
            self.update()

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
        self.last_mouse_pos = event.position()
        mx = (self.last_mouse_pos.x() - self.offset_x) / self.scale
        my = (self.last_mouse_pos.y() - self.offset_y) / self.scale
        
        for ci, curve in enumerate(self.curves):
            for pi, (x, y) in enumerate(curve["points"]):
                if abs(mx - x) < 6 and abs(my - y) < 6:
                    self.push_undo()
                    self.selected_curve = ci
                    self.selected_point = pi
                    self.dragging_point = True
                    return
                    
        for ci, curve in enumerate(self.curves):
            pts = curve["points"]
            for i in range(len(pts) - 1):
                if self._dist_to_segment(mx, my, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1]) < 5:
                    self.push_undo()
                    self.selected_curve = ci
                    self.selected_point = None
                    self.dragging_curve = True
                    return
                    
        self.dragging_canvas = True

    def mouseMoveEvent(self, event):
        if not self.last_mouse_pos:
            return
        pos = event.position()
        dx = pos.x() - self.last_mouse_pos.x()
        dy = pos.y() - self.last_mouse_pos.y()
        
        if self.dragging_point and self.selected_curve is not None:
            mx = (pos.x() - self.offset_x) / self.scale
            my = (pos.y() - self.offset_y) / self.scale
            self.curves[self.selected_curve]["points"][self.selected_point] = [mx, my]
        elif self.dragging_curve and self.selected_curve is not None:
            curve = self.curves[self.selected_curve]
            for i in range(len(curve["points"])):
                curve["points"][i][0] += dx / self.scale
                curve["points"][i][1] += dy / self.scale
        elif self.dragging_canvas:
            self.offset_x += dx
            self.offset_y += dy
            
        self.last_mouse_pos = pos
        self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_canvas = False
        self.dragging_point = False
        self.dragging_curve = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.scale *= 1.1 if delta > 0 else (1.0 / 1.1)
        self.update()

    def _dist_to_segment(self, px, py, x1, y1, x2, y2):
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        dot = A * C + B * D
        len_sq = C * C + D * D
        if len_sq == 0:
            return float(np.hypot(px - x1, py - y1))
        t = max(0.0, min(1.0, dot / len_sq))
        return float(np.hypot(px - (x1 + t * C), py - (y1 + t * D)))
