import sys
import csv
from pathlib import Path
import logging
from mapplotter3d.ui.data_chooser_panel import DataChooserPanel
from mapplotter3d.ui.plot_area import PlotPanel
from mapplotter3d.mapplotter import get_mapplott

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

logger = logging.getLogger(__name__)


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
        self.plot_area = PlotPanel()

        self.plot_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.data_panel)
        layout.addWidget(self.plot_area, 1)

        self.data_panel.data_config_changed.connect(self.on_data_config_changed)
        self.data_panel.plot_requested.connect(self._handle_plot_request)

    def on_data_config_changed(self, config: dict):
        logging.info("Current data config: %s", str(config))

    def _handle_plot_request(self, config: dict):
        logging.info("Passing the Plot requst on")

        df = self.data_panel.plottable_df

        if df is None or df.empty:
            return
        
        logger.info("Generating Map")
        map_res = get_mapplott(df, loc_col=config["location"], val_col=config["value"], label_col=config["label"])
        
        logger.info("Setting map")
        self.plot_area.set_map(map_res)
        


def start_gui():

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
