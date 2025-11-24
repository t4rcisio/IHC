from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt

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
