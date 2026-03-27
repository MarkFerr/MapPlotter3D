from pathlib import Path
import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from mapplotter3d.io.data_reader import (
    read_file,
    get_dataframe_preview,
    get_column_info,
    infer_default_columns,
)


logger = logging.getLogger(__name__)


class DataChooserPanel(QFrame):
    data_config_changed = Signal(dict)
    plot_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_path = None
        self.df = None
        self.plottable_df = None
        self.column_info = []
        self.defaults = {}


        self.duplicate_value_combos = {}
        self.current_contributing_cols = []

        self.setMinimumWidth(280)
        self.setMaximumWidth(360)
        self.setFrameShape(QFrame.StyledPanel)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel("Data chooser")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        root.addWidget(title)

        root.addWidget(self._build_source_group())
        root.addWidget(self._build_parse_group())
        root.addWidget(self._build_columns_group())
        root.addWidget(self._build_plot_button())
        root.addWidget(self._build_status_group())
        root.addWidget(self._build_preview_group(), 1)
        #todo add a section for custom geojson chooser (checkbox "Use custom geojson" and filepicker)

    def _build_source_group(self):
        box = QGroupBox("Data source")
        layout = QGridLayout(box)

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Choose a file...")

        self.browse_btn = QPushButton("Browse...")

        layout.addWidget(QLabel("File"), 0, 0)
        layout.addWidget(self.path_edit, 1, 0)
        layout.addWidget(self.browse_btn, 1, 1)

        return box

    def _build_parse_group(self):
        box = QGroupBox("Parse options")
        layout = QGridLayout(box)

        self.header_check = QCheckBox("First row contains headers")
        self.header_check.setChecked(True)

        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItem("Comma (,)", ",")
        self.delimiter_combo.addItem("Tab (\\t)", "\t")
        self.delimiter_combo.addItem("Semicolon (;)", ";")
        self.delimiter_combo.addItem("Pipe (|)", "|")

        self.preview_rows_spin = QSpinBox()
        self.preview_rows_spin.setRange(5, 500)
        self.preview_rows_spin.setValue(5)

        self.reload_btn = QPushButton("Reload")

        layout.addWidget(self.header_check, 0, 0, 1, 2)
        layout.addWidget(QLabel("Delimiter"), 1, 0)
        layout.addWidget(self.delimiter_combo, 1, 1)
        layout.addWidget(QLabel("Preview rows"), 2, 0)
        layout.addWidget(self.preview_rows_spin, 2, 1)
        layout.addWidget(self.reload_btn, 3, 0, 1, 2)

        return box

    def _build_columns_group(self):
        box = QGroupBox("Column mapping")
        layout = QGridLayout(box)

        self.value_combo = QComboBox()
        self.location_combo = QComboBox()
        self.label_combo = QComboBox()

        for combo in [self.value_combo, self.location_combo, self.label_combo]:
            combo.setEnabled(False)

        layout.addWidget(QLabel("Value"), 0, 0)
        layout.addWidget(self.value_combo, 0, 1)

        layout.addWidget(QLabel("Location"), 1, 0)
        layout.addWidget(self.location_combo, 1, 1)

        layout.addWidget(QLabel("Label"), 2, 0)
        layout.addWidget(self.label_combo, 2, 1)

        self.duplicate_filters_box = QGroupBox("Resolve ambiguities")
        self.duplicate_filters_layout = QGridLayout(self.duplicate_filters_box)
        self.duplicate_filters_box.setVisible(False)

        layout.addWidget(self.duplicate_filters_box, 4, 0, 1, 2)

        return box
    
    def _build_plot_button(self):
        self.plot_btn = QPushButton("Plot Data")
        self.plot_btn.setEnabled(False)
        self.plot_btn.setToolTip("No data loaded yet")

        return self.plot_btn

    def _build_status_group(self):
        box = QGroupBox("Status")
        layout = QVBoxLayout(box)

        self.file_label = QLabel("No file loaded")
        self.file_label.setWordWrap(True)

        self.shape_label = QLabel("Rows: -   Columns: -")
        self.columns_label = QLabel("Columns: -")
        self.columns_label.setWordWrap(True)

        layout.addWidget(self.file_label)
        layout.addWidget(self.shape_label)
        layout.addWidget(self.columns_label)

        return box

    def _build_preview_group(self):
        box = QGroupBox("Preview")
        layout = QVBoxLayout(box)

        self.preview_table = QTableWidget()
        self.preview_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.preview_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.preview_table.setAlternatingRowColors(True)

        layout.addWidget(self.preview_table)
        return box

    def _clear_duplicate_filter_widgets(self):
        while self.duplicate_filters_layout.count():
            item = self.duplicate_filters_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.duplicate_value_combos.clear()
        self.current_contributing_cols = []

    def _populate_duplicate_filter_widgets(self, contributing_cols: list[str], duplicated_df):
        self._clear_duplicate_filter_widgets()

        if not contributing_cols:
            self.duplicate_filters_box.setVisible(False)
            return

        self.current_contributing_cols = list(contributing_cols)

        for row, col in enumerate(contributing_cols):
            label = QLabel(col)
            combo = QComboBox()
            combo.addItem("<select>", None)

            values = duplicated_df[col].drop_duplicates().tolist()
            values = sorted(values, key=lambda x: str(x))

            for value in values:
                combo.addItem(str(value), value)

            combo.activated.connect(self._on_duplicate_filter_changed)

            self.duplicate_filters_layout.addWidget(label, row, 0)
            self.duplicate_filters_layout.addWidget(combo, row, 1)

            self.duplicate_value_combos[col] = combo

        self.duplicate_filters_box.setVisible(True)

    def _connect_signals(self):
        self.browse_btn.clicked.connect(self._browse_for_file)
        self.reload_btn.clicked.connect(self._reload_current_file)
        self.plot_btn.clicked.connect(self._on_plot_clicked)

        for combo in [self.value_combo, self.label_combo, self.location_combo]:
            combo.activated.connect(self._on_user_changed_combo)

    def _browse_for_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose data file",
            "",
            "Supported Files (*.csv *.xml *.pickle);;CSV Files (*.csv);;XML Files (*.xml);;Pickle Files (*.pickle);;All Files (*)"
        )
        if file_path:
            logger.info("Loading file from %s", file_path)
            self.load_data_file(file_path)

    def _reload_current_file(self):
        logging.info("Reloading current file")
        if self.file_path:
            self.load_data_file(self.file_path)

    def _on_plot_clicked(self):
        logger.info("Sending plot request")
        self.plot_requested.emit(self._current_config())


    def load_data_file(self, file_path: str):
        try:
            kwargs = {}

            # Only CSV needs delimiter/header behavior.
            suffix = Path(file_path).suffix.lower()
            if suffix == ".csv":
                kwargs["delimiter"] = self.delimiter_combo.currentData()
                kwargs["has_header"] = self.header_check.isChecked()

            df = read_file(file_path, **kwargs)

        except Exception as exc:
            QMessageBox.critical(self, "Load error", str(exc))
            return

        self.file_path = file_path
        self.df = df
        self.column_info = get_column_info(df)
        self.defaults = infer_default_columns(df)

        self._update_status()
        self._populate_column_combos()
        self._populate_preview()
        self._emit_config()
        self._update_plot_button_state()
    
    def _on_user_changed_combo(self):
        self._update_plot_button_state()
        self._emit_config()
        self._update_duplicate_list()

    def _update_plot_button_state(self):
        logger.info("Updating plot button.")

        #* Check if data is loaded
        if self.df is None:
            self.plot_btn.setEnabled(False)
            self.plot_btn.setToolTip("No data loaded yet")
            return

        #* Get selected value and location column
        value_txt = self._optional_combo_value(self.value_combo)
        location_txt = self._optional_combo_value(self.location_combo)

        #* Make sure value and location column are selected
        if not value_txt or not location_txt:
            self.plot_btn.setEnabled(False)
            self.plot_btn.setToolTip("Select at least a value and location column")
            return

        #* Get the DataFrame filtered by the chosen values to remove ambiguous values
        filtered_df = self._get_filtered_df()

        #* Check that there is still data after filtering 
        if filtered_df is None or filtered_df.empty:
            self.plot_btn.setEnabled(False)
            self.plot_btn.setToolTip("Current ambiguity filters remove all rows")
            return

        #* Get remaining duplicates for location values
        duplicates_mask = filtered_df.duplicated(subset=[location_txt, value_txt], keep=False)

        #* Check if there are still ambiguities to be resolved
        if duplicates_mask.any():
            self.plot_btn.setEnabled(False)
            self.plot_btn.setToolTip("Please resolve remaining ambiguities")
            return

        #* All looks good, ready to plot!
        logging.info("DataFrame looks good. Ready to plot!")
        self.plottable_df = filtered_df.copy()
        logging.info("Plottable DF: %s", self.plottable_df.info())
        self.plot_btn.setEnabled(True)
        self.plot_btn.setToolTip("Generate plot from selected data")

    def _update_status(self):
        if self.df is None:
            return

        self.path_edit.setText(self.file_path)
        self.file_label.setText(f"Loaded: {Path(self.file_path).name}")
        self.shape_label.setText(f"Rows: {len(self.df)}   Columns: {len(self.df.columns)}")

        cols = [str(c) for c in self.df.columns]
        preview = ", ".join(cols[:8])
        if len(cols) > 8:
            preview += " ..."
        self.columns_label.setText(f"Columns: {preview}")

    def _update_duplicate_list(self):
        location_text = self._optional_combo_value(self.location_combo)
        value_text = self._optional_combo_value(self.value_combo)

        if self.df is None or location_text is None or value_text is None:
            self._clear_duplicate_filter_widgets()
            self.duplicate_filters_box.setVisible(False)
            return

        duplicates_mask = self.df.duplicated(subset=[location_text, value_text], keep=False)

        if not duplicates_mask.any():
            self._clear_duplicate_filter_widgets()
            self.duplicate_filters_box.setVisible(False)
            return

        duplicated_df = self.df[duplicates_mask]

        contributing_cols = []

        for col in self.df.columns:
            col = str(col)

            if col in {location_text, value_text}:
                continue

            nunique_per_group = (
                duplicated_df.groupby([location_text, value_text])[col]
                .nunique(dropna=False)
            )

            if (nunique_per_group > 1).any():
                contributing_cols.append(col)

        if not contributing_cols:
            self._clear_duplicate_filter_widgets()
            self.duplicate_filters_box.setVisible(False)
            return

        logging.info("Found %i columns causing duplicates", len(contributing_cols))

        self._populate_duplicate_filter_widgets(contributing_cols, duplicated_df)

    def _on_duplicate_filter_changed(self):
        self._update_plot_button_state()
        self._emit_config()

    def _get_duplicate_filters(self) -> dict:
        filters = {}

        for col, combo in self.duplicate_value_combos.items():
            value = combo.currentData()
            if value is not None:
                filters[col] = value

        return filters

    def _populate_column_combos(self):
        if self.df is None:
            return

        numeric_cols = [c["name"] for c in self.column_info if c["numeric"]]
        all_cols = [c["name"] for c in self.column_info]

        #* Required numeric
        for combo in [self.value_combo]:
            combo.clear()
            combo.addItems(numeric_cols)
            combo.setEnabled(bool(numeric_cols))

        #* Optional numeric
        self.value_combo.clear()
        self.value_combo.addItem("<none>")
        self.value_combo.addItems(numeric_cols)
        self.value_combo.setEnabled(True)

        #* Optional any type
        self.location_combo.clear()
        self.location_combo.addItem("<none>")
        self.location_combo.addItems(all_cols)
        self.location_combo.setEnabled(True)

        #* Optional any type
        self.label_combo.clear()
        self.label_combo.addItem("<none>")
        self.label_combo.addItems(all_cols)
        self.label_combo.setEnabled(True)

        self._set_combo_value(self.value_combo, self.defaults.get("value"), allow_none=True)
        self._set_combo_value(self.location_combo, self.defaults.get("location"), allow_none=True)
        self._set_combo_value(self.label_combo, self.defaults.get("label"), allow_none=True)

        self._update_plot_button_state()

    def _set_combo_value(self, combo: QComboBox, value: str | None, allow_none: bool = False):
        if value is None:
            if allow_none:
                idx = combo.findText("<none>")
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            return

        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        elif allow_none:
            idx = combo.findText("<none>")
            if idx >= 0:
                combo.setCurrentIndex(idx)

    def _populate_preview(self):
        if self.df is None:
            return

        preview_rows = self.preview_rows_spin.value()
        preview_df = get_dataframe_preview(self.df, n=preview_rows)

        self.preview_table.clear()
        self.preview_table.setRowCount(len(preview_df))
        self.preview_table.setColumnCount(len(preview_df.columns))
        self.preview_table.setHorizontalHeaderLabels([str(c) for c in preview_df.columns])

        for row_idx in range(len(preview_df)):
            for col_idx, col_name in enumerate(preview_df.columns):
                value = preview_df.iloc[row_idx, col_idx]
                item = QTableWidgetItem("" if value is None else str(value))
                self.preview_table.setItem(row_idx, col_idx, item)

        self.preview_table.resizeColumnsToContents()

    def _optional_combo_value(self, combo: QComboBox):
        text = combo.currentText()
        return None if text == "<none>" else text
    
    def _get_filtered_df(self):
        if self.df is None:
            return None
        
        filtered_df = self.df.copy()
        logging.info("Original Length: %s", len(self.df))

        for col, value in self._get_duplicate_filters().items():
            filtered_df = filtered_df[filtered_df[col] == value]
        
        logging.info("Filtered Length: %s", len(filtered_df))
        return filtered_df

    def _current_config(self) -> dict:
        return {
            "file_path": self.file_path,
            "value": self._optional_combo_value(self.value_combo),
            "location": self._optional_combo_value(self.location_combo),
            "label": self._optional_combo_value(self.label_combo),
            "duplicate_filters": self._get_duplicate_filters(),
        }

    def _emit_config(self):
        if self.df is None:
            return

        self.data_config_changed.emit(self._current_config())