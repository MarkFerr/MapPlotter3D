import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)



logger = logging.getLogger(__name__)

class PlotPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("background: #f2f2f2;")
        layout = QVBoxLayout(self)

        top_bar = QFrame()
        top_bar.setFrameShape(QFrame.Box)
        top_bar.setFixedHeight(70)
        top_layout = QHBoxLayout(top_bar)
        top_layout.addWidget(QLabel("Plot options like colormap, export, etc. here"))
        top_layout.addStretch()

        plot_frame = QFrame()
        plot_frame.setFrameShape(QFrame.Box)
        plot_layout = QVBoxLayout(plot_frame)
        center = QLabel("VEDO plot here")
        center.setAlignment(Qt.AlignCenter)
        center.setStyleSheet("font-size: 24px;")
        plot_layout.addWidget(center)

        layout.addWidget(top_bar)
        layout.addWidget(plot_frame, 1)


    def plot_data(self, df, location_col, value_col, label_col):
        logger.info("Plot request received")