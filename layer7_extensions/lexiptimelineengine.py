# lexip_editor_timeline.py
# Timeline panel for Lexip Editor - keyframes, scrubbing, recording

from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QListWidget, QFileDialog
from PySide6.QtCore import QTimer, Qt

# Maintain localized module isolation without dynamic environment overrides
from .lexip_timeline import LexipTimeline, Keyframe

class LexipTimelinePanel(QWidget):
    def __init__(self, editor_ref=None):
        super().__init__()
        self.editor = editor_ref
        self.timeline = LexipTimeline(duration=5.0)
        self.current_time = 0.0
        self.playing = False
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def init_ui(self):
        layout = QVBoxLayout()
        controls = QHBoxLayout()
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        controls.addWidget(self.play_btn)
        
        add_kf_btn = QPushButton("Add Keyframe")
        add_kf_btn.clicked.connect(self.add_keyframe)
        controls.addWidget(add_kf_btn)
        
        del_kf_btn = QPushButton("Delete Keyframe")
        del_kf_btn.clicked.connect(self.delete_keyframe)
        controls.addWidget(del_kf_btn)
        
        save_btn = QPushButton("Save .lxa")
        save_btn.clicked.connect(self.save_lxa)
        controls.addWidget(save_btn)
        
        layout.addLayout(controls)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.valueChanged.connect(self.slider_changed)
        layout.addWidget(self.slider)

        self.kf_list = QListWidget()
        layout.addWidget(self.kf_list)
        
        self.setLayout(layout)

    def toggle_play(self):
        self.playing = not self.playing
        self.play_btn.setText("Pause" if self.playing else "Play")

    def update_frame(self):
        if self.playing and self.timeline:
            self.current_time += 1.0 / 60.0
            if self.current_time > self.timeline.duration:
                self.current_time = 0.0
            self.slider.blockSignals(True)
            self.slider.setValue(int((self.current_time / self.timeline.duration) * 1000))
            self.slider.blockSignals(False)
            self.apply_timeline_state()

    def slider_changed(self, value):
        self.current_time = (value / 1000.0) * self.timeline.duration
        self.apply_timeline_state()

    def add_keyframe(self):
        if not self.editor or not getattr(self.editor, "curves", None):
            return
        for cid, curve in enumerate(self.editor.curves):
            track = self.timeline.add_track(cid)
            track.add_keyframe(Keyframe(self.current_time, list(curve["points"]), list(curve["color"]), curve["thickness"]))
        self.refresh_kf_list()

    def delete_keyframe(self):
        selected = self.kf_list.currentRow()
        if selected < 0:
            return
        all_kf = []
        for cid, track in self.timeline.tracks.items():
            for kf in track.keyframes:
                all_kf.append((cid, kf))
        if selected < len(all_kf):
            cid, kf = all_kf[selected]
            self.timeline.tracks[cid].keyframes.remove(kf)
            self.refresh_kf_list()

    def refresh_kf_list(self):
        self.kf_list.clear()
        for cid, track in self.timeline.tracks.items():
            for kf in track.keyframes:
                self.kf_list.addItem(f"Curve {cid} - t={kf.time:.2f}")

    def apply_timeline_state(self):
        if not self.editor or not getattr(self.editor, "curves", None) or not self.timeline:
            return
        state = self.timeline.evaluate(self.current_time)
        for cid, curve_state in state.items():
            idx = int(cid)
            if idx < len(self.editor.curves):
                self.editor.curves[idx]["points"] = curve_state["points"]
                self.editor.curves[idx]["color"] = curve_state["color"]
                self.editor.curves[idx]["thickness"] = curve_state["thickness"]
        self.editor.update()

    def save_lxa(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Animation", "", "Lexip Animation (*.lxa)")
        if path:
            self.timeline.save_lxa(path)