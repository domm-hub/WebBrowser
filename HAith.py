import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QFileDialog, QDialog, QVBoxLayout, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon


class PasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Password")
        self.setGeometry(400, 200, 300, 150)

        # Layout for the password dialog
        layout = QVBoxLayout()
        
        self.label = QLabel("Enter password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # Mask the input
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.check_password)

        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.ok_button)
        
        self.setLayout(layout)

        self.password = "Adam@1612"  # Set the desired password here

    def check_password(self):
        if self.password_input.text() == self.password:
            self.accept()  # Close the dialog and allow the main window
        else:
            self.label.setText("Incorrect password! Try again.")
            self.password_input.clear()


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Web Browser")
        self.setGeometry(100, 100, 1000, 700)

        self.setWindowIcon(QIcon('global.png'))

        # Create the tab widget and set it as the central widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Add a new tab by default
        self.add_new_tab()

        # Set up the URL bar and buttons
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.navigate_to_url)

        self.new_tab_button = QPushButton("New Tab")
        self.new_tab_button.clicked.connect(self.add_new_tab)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.reload)

        # Layout for the URL bar and buttons
        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_bar)
        url_layout.addWidget(self.go_button)
        url_layout.addWidget(self.new_tab_button)
        url_layout.addWidget(self.reload_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(url_layout)
        main_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Styling buttons and tabs
        self.setStyle()

    def setStyle(self):
        # Styling the buttons
        button_style = """
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-size: 14px; 
                border-radius: 5px; 
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        self.go_button.setStyleSheet(button_style)
        self.new_tab_button.setStyleSheet(button_style.replace("#4CAF50", "#007BFF"))
        self.reload_button.setStyleSheet(button_style.replace("#4CAF50", "#FFC107"))

        # Styling tabs
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #f1f1f1;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #008CBA;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #ddd;
            }
        """)

    def add_new_tab(self, tab_name="New Tab", home_url="https://www.google.com"):
        browser = QWebEngineView()
        browser.setUrl(QUrl(home_url))

        # Connect to titleChanged signal to update tab title dynamically
        browser.titleChanged.connect(lambda title: self.update_tab_title(title, browser))

        # Add the tab with the correct label
        index = self.tabs.addTab(browser, str(tab_name))  # Ensure tab_name is a string
        self.tabs.setCurrentIndex(index)

    def update_tab_title(self, title, browser):
        # Find the index of the browser widget in the tab widget
        index = self.tabs.indexOf(browser)
        if index != -1:
            # Update the tab's title
            self.tabs.setTabText(index, title)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def reload(self):
        self.tabs.currentWidget().reload()

    def handle_download(self, download):
        suggested_name = download.downloadFileName()
        dialog = QFileDialog(self)
        save_path, _ = dialog.getSaveFileName(self, "Save File As", suggested_name)

        if save_path:
            download.setDownloadDirectory("")
            download.setDownloadFileName(save_path)
            download.accept()
            self.notify_download_complete(save_path)

    def notify_download_complete(self, path):
        print(f"Download complete: {path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show password dialog before opening the main browser window
    password_dialog = PasswordDialog()
    if password_dialog.exec() == QDialog.DialogCode.Accepted:
        window = BrowserWindow()
        window.show()
        app.exec()
    else:
        print("Access denied.")
        sys.exit()
