# pathfinder.py içeriği
import sys
import os
from playwright.sync_api import sync_playwright
import pytesseract
import PyQt5
from PIL import Image


def get_package_paths():
    print("\n=== Python Paths ===")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")

    print("\n=== Package Locations ===")
    print(f"PyQt5 Location: {os.path.dirname(PyQt5.__file__)}")
    print(f"Pillow Location: {os.path.dirname(Image.__file__)}")
    print(f"Pytesseract Location: {os.path.dirname(pytesseract.__file__)}")

    print("\n=== Playwright Info ===")
    with sync_playwright() as p:
        print(f"Playwright Browser Path: {p.chromium.executable_path}")

    print("\n=== Tesseract Info ===")
    print(f"Tesseract Command: {pytesseract.pytesseract.tesseract_cmd}")


if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    get_package_paths()