import sys
import csv
from pathlib import Path
import logging
from mapplotter3d.ui.data_chooser_panel import DataChooserPanel

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


class PlaceholderPlotArea(QFrame):
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MapPlotter3D")
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.data_panel = DataChooserPanel()
        self.plot_area = PlaceholderPlotArea()

        self.plot_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.data_panel)
        layout.addWidget(self.plot_area, 1)

        self.data_panel.data_config_changed.connect(self.on_data_config_changed)

    def on_data_config_changed(self, config: dict):
        logging.info("Current data config: %s", str(config))


if __name__ == "__main__":
    
    setup_logging()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())