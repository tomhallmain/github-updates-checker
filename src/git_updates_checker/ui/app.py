import sys
import os
import logging
import traceback
from typing import Dict, Any, List
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLineEdit, QTabWidget,
                            QTableWidget, QTableWidgetItem, QLabel, QComboBox,
                            QTextEdit, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
from dotenv import load_dotenv
from git_updates_checker.analyzers.fork import ForkAnalyzer
from git_updates_checker.analyzers.ecosystem import EcosystemAnalyzer
from git_updates_checker.ui.styles import DARK_STYLESHEET

class AnalysisWorker(QThread):
    """Worker thread for running analyses without freezing the GUI."""
    finished = pyqtSignal(object)  # dict from ecosystem analysis, tuple from fork analysis
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, analyzer_type: str, repo_name: str, github_token: str):
        super().__init__()
        self.analyzer_type = analyzer_type
        self.repo_name = repo_name
        self.github_token = github_token
    
    def run(self):
        try:
            if self.analyzer_type == "fork":
                analyzer = ForkAnalyzer(self.github_token)
                self.progress.emit("Analyzing repository forks...")
                results = analyzer.analyze_repository(self.repo_name)
            else:  # ecosystem
                analyzer = EcosystemAnalyzer(self.github_token)
                self.progress.emit("Analyzing repository ecosystem...")
                results = analyzer.analyze_ecosystem(self.repo_name)
            
            self.finished.emit(results)
        except Exception as e:
            full_error = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.error.emit(full_error)

class GitHubAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Repository Analyzer")
        self.setMinimumSize(1200, 800)
        
        # Load GitHub token
        load_dotenv()
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            msg = "GITHUB_TOKEN environment variable not set"
            logging.error(msg)
            QMessageBox.critical(self, "Error", msg)
            sys.exit(1)
        
        self.init_ui()
    
    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Repository input
        input_layout = QHBoxLayout()
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("Enter repository name (owner/repo)")
        input_layout.addWidget(self.repo_input)
        
        # Analysis type selector
        self.analysis_type = QComboBox()
        self.analysis_type.addItems(["Fork Analysis", "Ecosystem Analysis"])
        input_layout.addWidget(self.analysis_type)
        
        # Analyze button
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setObjectName("analyzeButton")
        self.analyze_button.clicked.connect(self.start_analysis)
        input_layout.addWidget(self.analyze_button)
        
        layout.addLayout(input_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Create tab widget for different views
        self.tabs = QTabWidget()
        
        # Table view tab
        self.table_tab = QWidget()
        self.table_layout = QVBoxLayout(self.table_tab)
        self.table = QTableWidget()
        self.table_layout.addWidget(self.table)
        self.tabs.addTab(self.table_tab, "Table View")
        
        # Search tab
        self.search_tab = QWidget()
        self.search_layout = QVBoxLayout(self.search_tab)
        
        # Search input
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.filter_results)
        search_input_layout.addWidget(self.search_input)
        
        # Search field selector
        self.search_field = QComboBox()
        self.search_field.addItems(["All Fields", "Name", "Description", "URL"])
        search_input_layout.addWidget(self.search_field)
        
        self.search_layout.addLayout(search_input_layout)
        
        # Search results table
        self.search_table = QTableWidget()
        self.search_layout.addWidget(self.search_table)
        self.tabs.addTab(self.search_tab, "Search")
        
        # Details tab
        self.details_tab = QWidget()
        self.details_layout = QVBoxLayout(self.details_tab)
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_layout.addWidget(self.details_text)
        self.tabs.addTab(self.details_tab, "Details")
        
        layout.addWidget(self.tabs)
        
        # Initialize data storage
        self.current_data = None
        self.df = None
    
    def start_analysis(self):
        repo_name = self.repo_input.text().strip()
        if not repo_name:
            msg = "Please enter a repository name"
            logging.warning(msg)
            QMessageBox.warning(self, "Error", msg)
            return
        
        # Disable UI elements during analysis
        self.analyze_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Create and start worker thread
        analyzer_type = "fork" if self.analysis_type.currentText() == "Fork Analysis" else "ecosystem"
        self.worker = AnalysisWorker(analyzer_type, repo_name, self.github_token)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.handle_results)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
    
    def update_progress(self, message: str):
        self.progress_bar.setFormat(message)
    
    def handle_results(self, results: Dict[str, Any]):
        self.current_data = results
        
        if isinstance(results, tuple):  # Fork analysis results
            fork_results, file_changes = results
            self.process_fork_results(fork_results, file_changes)
        else:  # Ecosystem analysis results
            self.process_ecosystem_results(results)
        
        # Re-enable UI elements
        self.analyze_button.setEnabled(True)
        self.progress_bar.hide()
    
    def handle_error(self, error_message: str):
        logging.error("Analysis failed:\n%s", error_message)
        first_line = error_message.split("\n")[0] if error_message else "Unknown error"
        popup_msg = f"Analysis failed: {first_line}\n\nFull error and stack trace have been written to the log."
        QMessageBox.critical(self, "Error", popup_msg)
        self.analyze_button.setEnabled(True)
        self.progress_bar.hide()
    
    def process_fork_results(self, fork_results: List[Dict[str, Any]], 
                           file_changes: Dict[str, List[Dict[str, Any]]]):
        # Convert results to DataFrame
        self.df = pd.DataFrame(fork_results)
        
        # Update table view
        self.update_table_view(self.df)
        
        # Update search table
        self.update_search_table(self.df)
        
        # Update details view with file changes
        details_text = "File Changes Summary:\n\n"
        for filename, changes in file_changes.items():
            details_text += f"File: {filename}\n"
            details_text += f"Total changes: {len(changes)}\n"
            for change in changes:
                details_text += f"\nFork: {change['fork_name']}\n"
                details_text += f"URL: {change['fork_url']}\n"
                if change['commit_message']:
                    details_text += f"Commit: {change['commit_message']}\n"
                details_text += f"Changes: +{change['additions']} -{change['deletions']}\n"
            details_text += "\n" + "-"*80 + "\n"
        
        self.details_text.setText(details_text)
    
    def process_ecosystem_results(self, results: Dict[str, Any]):
        # Convert results to DataFrame
        common_interests = results['common_interests']
        
        # Create DataFrames for each type of interest
        dfs = {}
        for interest_type, counter in common_interests.items():
            df = pd.DataFrame(counter.most_common(), 
                            columns=['Repository', 'Count'])
            dfs[interest_type] = df
        
        # Combine all DataFrames
        self.df = pd.concat(dfs.values(), keys=dfs.keys(), 
                          names=['Interest Type', 'Index'])
        self.df = self.df.reset_index(level=0)
        
        # Update table view
        self.update_table_view(self.df)
        
        # Update search table
        self.update_search_table(self.df)
        
        # Update details view with network information
        details_text = "Contributor Network Analysis:\n\n"
        details_text += f"Total Contributors: {len(results['contributors'])}\n\n"
        
        for interest_type, counter in common_interests.items():
            details_text += f"\n{interest_type.replace('_', ' ').title()}:\n"
            for repo, count in counter.most_common(10):
                details_text += f"{repo}: {count} contributors\n"
        
        self.details_text.setText(details_text)
    
    def update_table_view(self, df: pd.DataFrame):
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        
        for i, row in enumerate(df.itertuples(index=False)):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table.setItem(i, j, item)
        
        self.table.resizeColumnsToContents()
    
    def update_search_table(self, df: pd.DataFrame):
        self.search_table.setRowCount(len(df))
        self.search_table.setColumnCount(len(df.columns))
        self.search_table.setHorizontalHeaderLabels(df.columns)
        
        for i, row in enumerate(df.itertuples(index=False)):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.search_table.setItem(i, j, item)
        
        self.search_table.resizeColumnsToContents()
    
    def filter_results(self):
        if self.df is None:
            return
        
        search_text = self.search_input.text().lower()
        search_field = self.search_field.currentText()
        
        if not search_text:
            self.update_search_table(self.df)
            return
        
        if search_field == "All Fields":
            mask = self.df.astype(str).apply(
                lambda x: x.str.lower().str.contains(search_text, na=False)
            ).any(axis=1)
        else:
            mask = self.df[search_field].astype(str).str.lower().str.contains(
                search_text, na=False
            )
        
        filtered_df = self.df[mask]
        self.update_search_table(filtered_df)

def _setup_logging() -> None:
    """Configure logging to console and file with tracebacks."""
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(log_dir, "github_analyzer.log")
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for h in list(root.handlers):
        root.removeHandler(h)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(fh)

    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(ch)


def main():
    _setup_logging()
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = GitHubAnalyzerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 