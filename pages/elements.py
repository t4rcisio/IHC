from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QColor

class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self._checked = checked
        self._circle_position = 1 if checked else 0



        self.setFixedSize(50, 25)
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setDuration(200)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.animate()
        self.update()
        self.toggled.emit(self._checked)  # <----- EMITE O SINAL
        super().mousePressEvent(event)


    def animate(self):
        start = 0 if self._checked else 1
        end = 1 if self._checked else 0
        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fundo do switch
        rect = QRectF(0, 0, self.width(), self.height())
        if self._checked:
            p.setBrush(QColor("#34C759"))  # Verde iOS (ligado)
        else:
            p.setBrush(QColor("#E5E5EA"))  # Cinza iOS (desligado)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 15, 15)

        # Círculo
        x = self._circle_position * (self.width() - 22)
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(int(x), 2, 22, 22)

    # propriedade animada
    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circle_position = pyqtProperty(float, get_circle_position, set_circle_position)

    # obter estado ON/OFF
    def isChecked(self):
        return self._checked





class FlameLevelBar(QWidget):
    def __init__(self, level=0, color="#FF9500", parent=None):
        super().__init__(parent)
        self.level = level
        self.color = QColor(color)
        self.bg = QColor("#E5E5EA")  # fundo estilo iOS
        self.setMinimumHeight(20)

    def setLevel(self, value):
        self.level = max(0, min(1, int(value)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # fundo (barra cinza)
        painter.setBrush(self.bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, w, h, 8, 8)

        # barra preenchida (proporcional ao level)
        bar_width = w * self.level
        painter.setBrush(self.color)
        painter.drawRoundedRect(0, 0, int(bar_width), int(h), 8, 8)

        pct = int(self.level * 100)

        k_text = ""
        if self.level == 0:
            k_text = "Desligado"
        elif self.level <0.5:
            k_text = "Fogo baixo"
        elif self.level >=0.5 and self.level <0.75:
            k_text = "Fogo médio"
        elif self.level >= 0.75:
            k_text = "Fogo alto"


        # texto de porcentagem

        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{k_text}")
