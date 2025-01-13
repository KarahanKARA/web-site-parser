import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pytesseract
from PIL import Image
import io
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Tesseract path ayarı
if getattr(sys, 'frozen', False):
    tesseract_cmd = os.path.join(sys._MEIPASS, "Tesseract-OCR", "tesseract.exe")
else:
    tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


class OCRThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        if not self.url.strip():
            self.error.emit("URL boş olamaz!")
            return

        try:
            parsed_url = urlparse(self.url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                self.error.emit("Geçersiz URL formatı!")
                return

            with sync_playwright() as p:
                self.progress.emit("Browser başlatılıyor...")

                # Browser path ayarı
                if getattr(sys, 'frozen', False):
                    chrome_path = os.path.join(sys._MEIPASS, "chrome-win", "chrome.exe")
                else:
                    chrome_path = None

                browser = p.chromium.launch(
                    headless=True,
                    executable_path=chrome_path,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )

                page = browser.new_page()

                try:
                    self.progress.emit(f"Sayfa yükleniyor: {self.url}")
                    response = page.goto(self.url, wait_until='networkidle', timeout=30000)

                    if not response or response.status >= 400:
                        self.error.emit(
                            f"Sayfa yüklenemedi! (Hata Kodu: {response.status if response else 'Bağlantı Hatası'})")
                        return

                    self.progress.emit("Sayfa yüklendi, ekran görüntüsü alınıyor...")
                    page.wait_for_timeout(5000)
                    screenshot = page.screenshot(full_page=True)
                    image = Image.open(io.BytesIO(screenshot))

                    self.progress.emit("OCR işlemi yapılıyor...")
                    text = pytesseract.image_to_string(image, lang='tur')
                    text = '\n'.join(line for line in text.splitlines() if line.strip())

                    if text.strip():
                        self.finished.emit(text)
                    else:
                        self.error.emit("Metin çıkarılamadı veya sayfa boş")

                except PlaywrightTimeout:
                    self.error.emit("Sayfa yükleme zaman aşımına uğradı!")
                except Exception as e:
                    self.error.emit(f"İşlem sırasında hata: {str(e)}")
                finally:
                    browser.close()

        except Exception as e:
            self.error.emit(f"Beklenmeyen hata: {str(e)}")


class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setWindowTitle("KarahanApp")
        self.resize(1000, 800)  # Pencere boyutunu büyüttüm

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # URL girişi ve buton
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://...")
        self.url_input.returnPressed.connect(self.start_process)  # Enter tuşu desteği
        url_layout.addWidget(self.url_input)

        self.start_button = QPushButton("Taramayı Başlat")
        self.start_button.clicked.connect(self.start_process)
        self.start_button.setMinimumWidth(120)
        url_layout.addWidget(self.start_button)
        layout.addLayout(url_layout)

        # Durum göstergesi
        self.status_label = QLabel("URL'yi girin ve Başlat'a tıklayın veya Enter'a basın")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        # Sonuç alanı
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("background-color: white; font-family: Arial;")
        layout.addWidget(self.result_text)

    def start_process(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Lütfen bir URL girin")
            return

        self.status_label.setText(f"İşleniyor: {url}")
        self.start_button.setEnabled(False)
        self.url_input.setEnabled(False)
        self.result_text.clear()

        self.thread = OCRThread(url)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.process_finished)
        self.thread.error.connect(self.process_error)
        self.thread.start()

    def update_progress(self, message):
        self.status_label.setText(message)
        self.result_text.append(f"{message}\n")

    def process_finished(self, result):
        self.start_button.setEnabled(True)
        self.url_input.setEnabled(True)
        self.status_label.setText("İşlem başarıyla tamamlandı")
        self.result_text.setText(result)

    def process_error(self, error_message):
        self.start_button.setEnabled(True)
        self.url_input.setEnabled(True)
        self.status_label.setText(f"Hata: {error_message}")
        self.status_label.setStyleSheet("color: red;")


def main():
    app = QApplication(sys.argv)

    # Uygulama stil ayarları
    app.setStyle('Fusion')

    window = OCRApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()