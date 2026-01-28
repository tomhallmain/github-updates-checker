"""Dark theme stylesheet for the GitHub Analyzer GUI.

Uses a slate/charcoal palette with blue undertones—not pure black.
"""

# Dark theme palette: slate blues and charcoal
DARK_STYLESHEET = """
/* Main window & base */
QMainWindow, QWidget {
    background-color: #1a1d23;
}

/* Central content area */
QWidget#centralwidget {
    background-color: #1a1d23;
}

/* Input fields */
QLineEdit {
    background-color: #2a2e36;
    color: #e4e6eb;
    border: 1px solid #3d434d;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #3d7ab8;
}

QLineEdit:focus {
    border-color: #4a90d9;
}

QLineEdit::placeholder {
    color: #6b7280;
}

/* Combo box */
QComboBox {
    background-color: #2a2e36;
    color: #e4e6eb;
    border: 1px solid #3d434d;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    min-width: 140px;
}

QComboBox:hover {
    border-color: #4a5568;
}

QComboBox::drop-down {
    border: none;
    background-color: transparent;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8b95a5;
    margin-right: 8px;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #252931;
    color: #e4e6eb;
    selection-background-color: #3d7ab8;
    outline: none;
}

/* Buttons */
QPushButton {
    background-color: #2d3748;
    color: #e4e6eb;
    border: 1px solid #3d434d;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #374151;
    border-color: #4a5568;
}

QPushButton:pressed {
    background-color: #1e293b;
}

QPushButton:disabled {
    background-color: #252931;
    color: #6b7280;
    border-color: #2a2e36;
}

/* Primary action button (Analyze) */
QPushButton#analyzeButton {
    background-color: #2b5a87;
    border-color: #3d7ab8;
}

QPushButton#analyzeButton:hover {
    background-color: #3d7ab8;
    border-color: #5a9ad4;
}

/* Progress bar */
QProgressBar {
    background-color: #252931;
    border: 1px solid #3d434d;
    border-radius: 6px;
    text-align: center;
    color: #e4e6eb;
    font-size: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #3d7ab8,
        stop: 1 #5a9ad4
    );
    border-radius: 5px;
}

/* Tab widget */
QTabWidget::pane {
    background-color: #1e2128;
    border: 1px solid #2d323c;
    border-radius: 8px;
    top: -1px;
    padding: 12px;
}

QTabBar::tab {
    background-color: #252931;
    color: #9ca3af;
    border: 1px solid #2d323c;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 2px;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #1e2128;
    color: #e4e6eb;
    font-weight: 500;
}

QTabBar::tab:hover:!selected {
    background-color: #2a2e36;
    color: #c8ccd4;
}

/* Tables */
QTableWidget {
    background-color: #1e2128;
    alternate-background-color: #252931;
    color: #e4e6eb;
    gridline-color: #2d323c;
    border: 1px solid #2d323c;
    border-radius: 6px;
    font-size: 12px;
}

QTableWidget::item {
    padding: 6px 10px;
}

QTableWidget::item:selected {
    background-color: #3d7ab8;
    color: #ffffff;
}

QTableWidget::item:hover {
    background-color: #2a2e36;
}

QHeaderView::section {
    background-color: #252931;
    color: #9ca3af;
    padding: 10px 12px;
    border: none;
    border-right: 1px solid #2d323c;
    border-bottom: 2px solid #3d434d;
    font-size: 12px;
    font-weight: 600;
}

QHeaderView::section:last {
    border-right: none;
}

/* Text edit (read-only details) */
QTextEdit {
    background-color: #1e2128;
    color: #d1d5db;
    border: 1px solid #2d323c;
    border-radius: 6px;
    padding: 12px;
    font-size: 12px;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #252931;
    width: 12px;
    border-radius: 6px;
    margin: 2px 0;
}

QScrollBar::handle:vertical {
    background-color: #3d434d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a5568;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #252931;
    height: 12px;
    border-radius: 6px;
    margin: 0 2px;
}

QScrollBar::handle:horizontal {
    background-color: #3d434d;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4a5568;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* Message boxes (when shown) inherit from app - set on QApplication */
"""
