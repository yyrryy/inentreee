import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
import subprocess

def start_django_server():
    subprocess.call(["python", "manage.py", "runserver"])

def launch_chrome():
    subprocess.call(["chromium-browser", "http://127.0.0.1:8000/"])

app = QApplication(sys.argv)
view = QWebEngineView()
view.load(QUrl("http://127.0.0.1:8000/"))
view.show()

start_django_server()
launch_chrome()
sys.exit(app.exec_())