# lexip_gpu_renderer.py
# Lexip GPU Renderer - OpenGL accelerated curve rendering
import sys
import ctypes
import numpy as np

# Add paths to enable imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "layer1_data_lattice"))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

VERT_SHADER = """
#version 330 core
layout(location = 0) in vec2 in_pos;
layout(location = 1) in vec3 in_color;
uniform float u_scale;
uniform vec2 u_offset;
out vec3 v_color;
void main() {
    vec2 p = (in_pos * u_scale) + u_offset;
    gl_Position = vec4(p, 0.0, 1.0);
    v_color = in_color;
}
"""

FRAG_SHADER = """
#version 330 core
in vec3 v_color;
out vec4 fragColor;
void main() {
    fragColor = vec4(v_color, 1.0);
}
"""

class LexipGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.curves = []
        self.vbos = []
        self.counts = []
        self.scale = 0.002
        self.offset = np.array([0.0, 0.0], dtype=np.float32)
        self.dragging = False
        self.last_mouse = None

    def initializeGL(self):
        glClearColor(0.05, 0.05, 0.05, 1.0)
        self.program = compileProgram(
            compileShader(VERT_SHADER, GL_VERTEX_SHADER),
            compileShader(FRAG_SHADER, GL_FRAGMENT_SHADER)
        )
        glUseProgram(self.program)
        self.u_scale = glGetUniformLocation(self.program, "u_scale")
        self.u_offset = glGetUniformLocation(self.program, "u_offset")
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def load_curves(self, curves):
        self.makeCurrent()
        if self.vbos:
            glDeleteBuffers(len(self.vbos), self.vbos)
        self.curves = curves
        self.vbos = []
        self.counts = []
        for curve in curves:
            pts = np.array(curve["points"], dtype=np.float32)
            color = np.array(curve["color"], dtype=np.float32) / 255.0
            colors = np.tile(color, (len(pts), 1)).astype(np.float32)
            data = np.hstack([pts, colors]).astype(np.float32)
            
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
            self.vbos.append(vbo)
            self.counts.append(len(pts))
        self.update()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.program)
        glUniform1f(self.u_scale, self.scale)
        glUniform2f(self.u_offset, self.offset[0], self.offset[1])
        for vbo, count, curve in zip(self.vbos, self.counts, self.curves):
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
            glLineWidth(max(1.0, curve.get("thickness", 1.0)))
            glDrawArrays(GL_LINE_STRIP, 0, count)

    def wheelEvent(self, event):
        self.scale *= 1.1 if event.angleDelta().y() > 0 else (1.0 / 1.1)
        self.update()

    def mousePressEvent(self, event):
        self.dragging = True
        self.last_mouse = event.position()

    def mouseMoveEvent(self, event):
        if self.dragging and self.last_mouse:
            pos = event.position()
            self.offset[0] += (pos.x() - self.last_mouse.x()) * 0.002
            self.offset[1] -= (pos.y() - self.last_mouse.y()) * 0.002
            self.last_mouse = pos
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False

class LexipGPURenderer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lexip GPU Renderer")
        self.resize(1200, 900)
        layout = QVBoxLayout()
        self.gl = LexipGLWidget()
        layout.addWidget(self.gl)
        self.setLayout(layout)

    def load_curves(self, curves):
        self.gl.load_curves(curves)

def run_gpu_renderer(curves):
    app = QApplication.instance() or QApplication(sys.argv)
    win = LexipGPURenderer()
    win.load_curves(curves)
    win.show()
    sys.exit(app.exec())
