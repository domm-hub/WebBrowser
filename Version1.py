import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QFileDialog, QDialog, QProgressDialog, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIcon


class PasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Password")
        self.setGeometry(400, 200, 300, 150)

        layout = QVBoxLayout()
        self.label = QLabel("Enter password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.check_password)

        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.ok_button)
        
        self.setLayout(layout)

        self.password = "Adam@1612"

    def check_password(self):
        if self.password_input.text() == self.password:
            self.accept()
        else:
            self.label.setText("Incorrect password! Try again.")
            self.password_input.clear()


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Webby")
        self.setGeometry(100, 100, 1000, 700)

        self.setWindowIcon(QIcon('global.png'))

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.add_new_tab()

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.navigate_to_url)

        self.new_tab_button = QPushButton("")
        self.new_tab_button.setIcon(QIcon("plus-symbol-button.png"))
        self.new_tab_button.clicked.connect(self.add_new_tab)

        self.reload_button = QPushButton("")
        self.reload_button.setIcon(QIcon("reload.png"))
        self.reload_button.clicked.connect(self.reload)

        self.forward_button = QPushButton("")
        self.forward_button.setIcon(QIcon("next.png"))
        self.forward_button.clicked.connect(self.go_forward)

        self.back_button = QPushButton("")
        self.back_button.setIcon(QIcon("back.png"))
        self.back_button.clicked.connect(self.go_back)

        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_bar)
        url_layout.addWidget(self.go_button)
        url_layout.addWidget(self.new_tab_button)
        url_layout.addWidget(self.reload_button)
        url_layout.addWidget(self.back_button)
        url_layout.addWidget(self.forward_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(url_layout)
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.setStyle()

        self.setup_download_functionality()

    def setStyle(self):
        button_style = """
            QPushButton {
                background-color: #F3F3F3;  
                font-size: 14px; 
                border-radius: 5px; 
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #CCCCCC;
            }
        """
        self.go_button.setStyleSheet(button_style)
        self.new_tab_button.setStyleSheet(button_style)
        self.reload_button.setStyleSheet(button_style)
        self.back_button.setStyleSheet(button_style)
        self.forward_button.setStyleSheet(button_style)

        self.tabs.setStyleSheet(""" 
            QTabWidget::pane { border: 1px solid #ccc; }
            QTabBar::tab { background-color: #f1f1f1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #008CBA; color: white; }
            QTabBar::tab:hover { background-color: #ddd; }
        """)

    def setup_download_functionality(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

    def add_new_tab(self, tab_name="New Tab", home_url="https://www.google.com"):
        browser = QWebEngineView()
        browser.setUrl(QUrl(home_url))
        
        browser.urlChanged.connect(lambda url: self.update_url(url))
        browser.titleChanged.connect(lambda title: self.update_tab_title(title, browser))
        browser.iconChanged.connect(lambda: self.update_tab_icon(browser))

        index = self.tabs.addTab(browser, tab_name)
        self.tabs.setCurrentIndex(index)

    def update_tab_icon(self, browser):
        favicon = browser.icon()
        index = self.tabs.indexOf(browser)
        if not favicon.isNull() and index != -1:
            self.tabs.setTabIcon(index, favicon)

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)

    def update_url(self, url):
        self.url_bar.setText(url.toString())

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()  # Strip extra spaces
        
        # Check if the input starts with http/https
        if url.startswith("http://") or url.startswith("https://"):
            self.tabs.currentWidget().setUrl(QUrl(url))  # Directly navigate to the URL
        elif "." in url:  # Assume it's a domain name
            self.tabs.currentWidget().setUrl(QUrl(f"https://{url}"))  # Prepend https://
        else:
            # If invalid, perform a Google search
            search_query = QUrl(f"https://www.google.com/search?q={url}")
            self.tabs.currentWidget().setUrl(search_query)

    def reload(self):
        self.tabs.currentWidget().reload()
    

    def handle_download(self, download):
        suggested_name = download.suggestedFileName()
        dialog = QFileDialog(self)
        save_path, _ = dialog.getSaveFileName(self, "Save File", suggested_name)

        if save_path:
            download.setDownloadFileName(save_path)
            download.accept()

            self.progress_dialog = QProgressDialog("Downloading...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setAutoClose(True)
            self.progress_dialog.show()

            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_progress(download.receivedBytes(), download, self.progress_dialog))
            self.timer.start(100)

    def update_progress(self, bytes_received, download, progress_dialog):
        total_bytes = download.totalBytes()
        if total_bytes > 0:
            percent = (bytes_received / total_bytes) * 100
            progress_dialog.setValue(int(percent))
            progress_dialog.setLabelText(f"{bytes_received / 1_000_000:.2f}MB / {total_bytes / 1_000_000:.2f}MB")
        if bytes_received == total_bytes:
            progress_dialog.setValue(100)
            self.notify_download_complete(download.downloadFileName())
            self.timer.stop()

    def notify_download_complete(self, path):
        print(f"Download complete: {path}")

    def go_back(self):
        self.tabs.currentWidget().back()

    def go_forward(self):
        self.tabs.currentWidget().forward()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    password_dialog = PasswordDialog()
    if password_dialog.exec() == QDialog.DialogCode.Accepted:
        window = BrowserWindow()
        window.show()
        app.exec()
    else:
        print("Access denied.")
        sys.exit()
