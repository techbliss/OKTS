import sys
import os
import webbrowser
from os import *
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QLabel, QGridLayout, QMessageBox, QToolTip,
    QTabWidget, QWidget, QVBoxLayout, QToolButton, QToolBar, QCheckBox, QFileDialog,QPushButton, QGridLayout
)
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QFile
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings,QWebEngineCookieStore

# ---------------------- IPSC Calculator Tab ---------------------
# IPSC Power Factor Divisions
DIVISIONS = {
    "Production": {"minor": 125, "major": None},  # No Major
    "Standard": {"minor": 125, "major": 170},
   # "Modified": {"minor": 125, "major": 160},
    "Revolver": {"minor": 125, "major": 170},
    "Open": {"minor": 125, "major": 160},
    "Classic": {"minor": 125, "major": 170},
}

def calculate_power_factor(bullet_weight, velocity):
    try:
        weight = float(bullet_weight)
        velocity = float(velocity)
        return (weight * velocity) / 1000
    except ValueError:
        return None

def validate_and_update_status(power_factor, division_labels):
    for division, thresholds in DIVISIONS.items():
        label = division_labels[division]
        label.setText(division)

        if power_factor is not None:
            if thresholds["major"] and power_factor >= thresholds["major"]:
                label.setText(f"{division} - Major Okay")
                label.setStyleSheet("background-color: blue;")
            elif thresholds["minor"] and power_factor >= thresholds["minor"]:
                label.setText(f"{division} - Minor Okay")
                label.setStyleSheet("background-color: green;")
            else:
                label.setStyleSheet("background-color: red;")

class IPSCCalculatorTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()

        # Input widgets
        self.bullet_weight_input = QLineEdit()
        layout.addWidget(QLabel("Bullet Weight (gr):"), 0, 0)
        layout.addWidget(self.bullet_weight_input, 0, 1)

        self.velocity_input = QLineEdit()
        layout.addWidget(QLabel("Velocity (fps):"), 1, 0)
        layout.addWidget(self.velocity_input, 1, 1)

        # Results label
        self.power_factor_result = QLabel()
        layout.addWidget(QLabel("Power Factor:"), 2, 0)
        layout.addWidget(self.power_factor_result, 2, 1)

        # Division status labels
        self.division_labels = {}
        row = 3
        for division, thresholds in DIVISIONS.items():
            label = QLabel(division)
            label.setToolTip(f"Minimum Minor PF: {thresholds['minor']}\nMinimum Major PF: {thresholds['major']}")
            label.setFont(QFont('Arial', 10))
            self.division_labels[division] = label
            layout.addWidget(label, row, 0, 1, 2)
            row += 1

        # Connect input change to calculation
        self.bullet_weight_input.textChanged.connect(self.update_power_factor)
        self.velocity_input.textChanged.connect(self.update_power_factor)

        self.setLayout(layout)

    def update_power_factor(self):
        power_factor = calculate_power_factor(self.bullet_weight_input.text(), self.velocity_input.text())

        if power_factor is not None:
            self.power_factor_result.setText(str(power_factor))
        else:
            self.power_factor_result.setText("Invalid Input")

        validate_and_update_status(power_factor, self.division_labels)

# ------------------------ Web Browser Tab -----------------------
class WebBrowserTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)

        # Address bar and buttons
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.address_bar)


        back_button = QToolButton()
        back_button.setText("<")
        back_button.clicked.connect(self.go_back)
        toolbar.addWidget(back_button)


        forward_button = QToolButton()
        forward_button.setText(">")
        forward_button.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_button)

        # Toolbar Additions
        #self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        #toolbar.addWidget(self.case_sensitive_checkbox)  # Add the checkbox to the toolbar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_text)
        toolbar.addWidget(self.search_bar)

        search_button = QToolButton()
        search_button.setText("Find")
        search_button.clicked.connect(self.search_text)
        toolbar.addWidget(search_button)

        # Web View
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

        self.web_view.load(QUrl("https://www.okts.no/profile/1101668018/dynamisk"))
        self.web_view.urlChanged.connect(self.update_address_bar)
        layout.addWidget(self.web_view)

    def search_text(self, found=None):
        try:
            text_to_find = self.search_bar.text()

            # Clear Previous Highlights (Optional)
            self.web_view.page().findText("")

            # Perform the search (PyQt6 Compatibility)
            if self.case_sensitive_checkbox.isChecked():
                self.web_view.page().findText(text_to_find, QWebEnginePage.FindFlags.FindCaseSensitive)
            else:
                self.web_view.page().findText(text_to_find)

            if found:
                # Scroll to the found text (Approximate)
                self.web_view.page().runJavaScript("window.scrollTo(0,0);")
    
                # Apply highlighting style
                self.web_view.page().runJavaScript(
                    f"window.find('{text_to_find}');"
                    )
            else:
                print("Not Found.")


        except Exception as e:

            print(f"Search Error: {e}")



    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def handle_link_clicked(self, url):
        self.web_view.load(url)  # Navigate to the new URL


    def load_url(self):
        url = QUrl(self.address_bar.text())
        self.web_view.load(url)

    def go_back(self):
        self.web_view.back()

    def go_forward(self):
        self.web_view.forward()


#tab 3 web
class WebBrowserTab1(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)

        # Address bar and buttons
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.address_bar)

        back_button = QToolButton()
        back_button.setText("<")
        back_button.clicked.connect(self.go_back)
        toolbar.addWidget(back_button)

        forward_button = QToolButton()
        forward_button.setText(">")
        forward_button.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_button)

        # Toolbar Additions
        #self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        #toolbar.addWidget(self.case_sensitive_checkbox)  # Add the checkbox to the toolbar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_text)
        toolbar.addWidget(self.search_bar)

        search_button = QToolButton()
        search_button.setText("Find")
        search_button.clicked.connect(self.search_text)
        toolbar.addWidget(search_button)

        # Web View
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

        self.web_view.load(QUrl("https://shootnscoreit.com/"))
        self.web_view.urlChanged.connect(self.update_address_bar)
        layout.addWidget(self.web_view)

    def search_text(self, found=None):
        try:
            text_to_find = self.search_bar.text()

            # Clear Previous Highlights (Optional)
            self.web_view.page().findText("")

            # Perform the search (PyQt6 Compatibility)
            if self.case_sensitive_checkbox.isChecked():
                self.web_view.page().findText(text_to_find, QWebEnginePage.FindFlags.FindCaseSensitive)
            else:
                self.web_view.page().findText(text_to_find)

            if found:
                # Scroll to the found text (Approximate)
                self.web_view.page().runJavaScript("window.scrollTo(0,0);")

                # Apply highlighting style
                self.web_view.page().runJavaScript(
                    f"window.find('{text_to_find}');"
                )
            else:
                print("Not Found.")


        except Exception as e:

            print(f"Search Error: {e}")

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def handle_link_clicked(self, url):
        self.web_view.load(url)  # Navigate to the new URL

    def load_url(self):
        url = QUrl(self.address_bar.text())
        self.web_view.load(url)

    def go_back(self):
        self.web_view.back()

    def go_forward(self):
        self.web_view.forward()

class WebBrowserTab2(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)

        # Address bar and buttons
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.address_bar)

        back_button = QToolButton()
        back_button.setText("<")
        back_button.clicked.connect(self.go_back)
        toolbar.addWidget(back_button)

        forward_button = QToolButton()
        forward_button.setText(">")
        forward_button.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_button)

        # Toolbar Additions
        #self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        #toolbar.addWidget(self.case_sensitive_checkbox)  # Add the checkbox to the toolbar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_text)
        toolbar.addWidget(self.search_bar)

        search_button = QToolButton()
        search_button.setText("Find")
        search_button.clicked.connect(self.search_text)
        toolbar.addWidget(search_button)

        # Web View
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

        self.web_view.load(QUrl("https://www.google.com/maps/dir//sankthanshaugen+okts/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x46416f995d1eb63d:0xe60aa231c80e0831?sa=X&ved=2ahUKEwjUzsDis7KEAxXxPhAIHazrBkcQ9Rd6BAgxEAA"))
        self.web_view.urlChanged.connect(self.update_address_bar)
        layout.addWidget(self.web_view)

    def search_text(self, found=None):
        try:
            text_to_find = self.search_bar.text()

            # Clear Previous Highlights (Optional)
            self.web_view.page().findText("")

            # Perform the search (PyQt6 Compatibility)
            if self.case_sensitive_checkbox.isChecked():
                self.web_view.page().findText(text_to_find, QWebEnginePage.FindFlags.FindCaseSensitive)
            else:
                self.web_view.page().findText(text_to_find)

            if found:
                # Scroll to the found text (Approximate)
                self.web_view.page().runJavaScript("window.scrollTo(0,0);")

                # Apply highlighting style
                self.web_view.page().runJavaScript(
                    f"window.find('{text_to_find}');"
                )
            else:
                print("Not Found.")


        except Exception as e:

            print(f"Search Error: {e}")

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def handle_link_clicked(self, url):
        self.web_view.load(url)  # Navigate to the new URL

    def load_url(self):
        url = QUrl(self.address_bar.text())
        self.web_view.load(url)

    def go_back(self):
        self.web_view.back()

    def go_forward(self):
        self.web_view.forward()

# --------------------- Main Window Setup ------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OKTS Dynamisk APP")

        tab_widget = QTabWidget()
        tab_widget.addTab(IPSCCalculatorTab(), "IPSC Powerfactor")
        tab_widget.addTab(WebBrowserTab(), "OKTS Dynamiske gruppe")
        tab_widget.addTab(WebBrowserTab1(), "Shootandscoreit")
        tab_widget.addTab(WebBrowserTab2(), "sankthanshaugen Maps")
        tab_widget.addTab(WebBrowserTab3(), "Tåsen Maps")
        tab_widget.addTab(WebBrowserTab4(), "DSSN")
        tab_widget.addTab(WebBrowserTab5(), "IPSC Rules books")
        tab_widget.addTab(LinkOpener(), "Eksterne links")
        tab_widget.addTab(LinkOpener1(), "Rabatt for okts medlemmer")
        self.setCentralWidget(tab_widget)

class WebBrowserTab3(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)

        # Address bar and buttons
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.address_bar)

        back_button = QToolButton()
        back_button.setText("<")
        back_button.clicked.connect(self.go_back)
        toolbar.addWidget(back_button)

        forward_button = QToolButton()
        forward_button.setText(">")
        forward_button.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_button)

        # Toolbar Additions
        #self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        #toolbar.addWidget(self.case_sensitive_checkbox)  # Add the checkbox to the toolbar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_text)
        toolbar.addWidget(self.search_bar)

        search_button = QToolButton()
        search_button.setText("Find")
        search_button.clicked.connect(self.search_text)
        toolbar.addWidget(search_button)

        # Web View
        self.web_view = QWebEngineView()
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
        )
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)



        self.web_view.load(QUrl("https://www.google.com/maps/dir/59.920621,10.660327/OKTS+T%C3%A5sen,+T%C3%A5sen+Terrasse,+0873+Oslo/@59.9388828,10.6693672,13z/data=!3m1!4b1!4m18!1m7!3m6!1s0x46416f26e31bcfd1:0x59dd91ba2f13eff3!2sOKTS+T%C3%A5sen!8m2!3d59.9578229!4d10.7537873!16s%2Fg%2F11pyzfqnsl!4m9!1m1!4e1!1m5!1m1!1s0x46416f26e31bcfd1:0x59dd91ba2f13eff3!2m2!1d10.7537873!2d59.9578229!3e0?entry=ttu"))
        self.web_view.urlChanged.connect(self.update_address_bar)
        layout.addWidget(self.web_view)

    def search_text(self, found=None):
        try:
            text_to_find = self.search_bar.text()

            # Clear Previous Highlights (Optional)
            self.web_view.page().findText("")

            # Perform the search (PyQt6 Compatibility)
            if self.case_sensitive_checkbox.isChecked():
                self.web_view.page().findText(text_to_find, QWebEnginePage.FindFlags.FindCaseSensitive)
            else:
                self.web_view.page().findText(text_to_find)

            if found:
                # Scroll to the found text (Approximate)
                self.web_view.page().runJavaScript("window.scrollTo(0,0);")

                # Apply highlighting style
                self.web_view.page().runJavaScript(
                    f"window.find('{text_to_find}');"
                )
            else:
                print("Not Found.")


        except Exception as e:

            print(f"Search Error: {e}")

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def handle_link_clicked(self, url):
        self.web_view.load(url)  # Navigate to the new URL

    def load_url(self):
        url = QUrl(self.address_bar.text())
        self.web_view.load(url)

    def go_back(self):
        self.web_view.back()

    def go_forward(self):
        self.web_view.forward()

class WebBrowserTab4(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)

        # Address bar and buttons
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.address_bar)

        back_button = QToolButton()
        back_button.setText("<")
        back_button.clicked.connect(self.go_back)
        toolbar.addWidget(back_button)

        forward_button = QToolButton()
        forward_button.setText(">")
        forward_button.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_button)

        # Toolbar Additions
        #self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        #toolbar.addWidget(self.case_sensitive_checkbox)  # Add the checkbox to the toolbar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_text)
        toolbar.addWidget(self.search_bar)

        search_button = QToolButton()
        search_button.setText("Find")
        search_button.clicked.connect(self.search_text)
        toolbar.addWidget(search_button)

        # Web View
        self.web_view = QWebEngineView()
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
        )
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)


        self.web_view.load(QUrl("https://dssn.no"))
        self.web_view.urlChanged.connect(self.update_address_bar)
        layout.addWidget(self.web_view)

    def search_text(self, found=None):
        try:
            text_to_find = self.search_bar.text()

            # Clear Previous Highlights (Optional)
            self.web_view.page().findText("")

            # Perform the search (PyQt6 Compatibility)
            if self.case_sensitive_checkbox.isChecked():
                self.web_view.page().findText(text_to_find, QWebEnginePage.FindFlags.FindCaseSensitive)
            else:
                self.web_view.page().findText(text_to_find)

            if found:
                # Scroll to the found text (Approximate)
                self.web_view.page().runJavaScript("window.scrollTo(0,0);")

                # Apply highlighting style
                self.web_view.page().runJavaScript(
                    f"window.find('{text_to_find}');"
                )
            else:
                print("Not Found.")


        except Exception as e:

            print(f"Search Error: {e}")

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def handle_link_clicked(self, url):
        self.web_view.load(url)  # Navigate to the new URL

    def load_url(self):
        url = QUrl(self.address_bar.text())
        self.web_view.load(url)

    def go_back(self):
        self.web_view.back()

    def go_forward(self):
        self.web_view.forward()

class WebBrowserTab5(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Toolbar
        toolbar = QToolBar()
        layout.addWidget(toolbar)

        # Address bar and buttons
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.address_bar)

        back_button = QToolButton()
        back_button.setText("<")
        back_button.clicked.connect(self.go_back)
        toolbar.addWidget(back_button)

        forward_button = QToolButton()
        forward_button.setText(">")
        forward_button.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_button)

        # Toolbar Additions
        #self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        #toolbar.addWidget(self.case_sensitive_checkbox)  # Add the checkbox to the toolbar
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_text)
        toolbar.addWidget(self.search_bar)

        search_button = QToolButton()
        search_button.setText("Find")
        search_button.clicked.connect(self.search_text)
        toolbar.addWidget(search_button)

        # Web View
        self.web_view = QWebEngineView()
        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
        )
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)


        self.web_view.load(QUrl("https://www.ipsc.org/wp-content/uploads/2023/12/IPSC-Handgun-Competition-Rules-Jan-2024-Edition-Final-27-Dec-2023.pdf"))
        self.web_view.urlChanged.connect(self.update_address_bar)
        layout.addWidget(self.web_view)

    def search_text(self, found=None):
        try:
            text_to_find = self.search_bar.text()

            # Clear Previous Highlights (Optional)
            self.web_view.page().findText("")

            # Perform the search (PyQt6 Compatibility)
            if self.case_sensitive_checkbox.isChecked():
                self.web_view.page().findText(text_to_find, QWebEnginePage.FindFlags.FindCaseSensitive)
            else:
                self.web_view.page().findText(text_to_find)

            if found:
                # Scroll to the found text (Approximate)
                self.web_view.page().runJavaScript("window.scrollTo(0,0);")

                # Apply highlighting style
                self.web_view.page().runJavaScript(
                    f"window.find('{text_to_find}');"
                )
            else:
                print("Not Found.")


        except Exception as e:

            print(f"Search Error: {e}")

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def handle_link_clicked(self, url):
        self.web_view.load(url)  # Navigate to the new URL

    def load_url(self):
        url = QUrl(self.address_bar.text())
        self.web_view.load(url)

    def go_back(self):
        self.web_view.back()

    def go_forward(self):
        self.web_view.forward()


class LinkOpener(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Link Opener")
        self.layout = QGridLayout()

        self.links = [
            ("OKTS Dynamisk Facebook", "https://www.facebook.com/groups/670259856359608"),
            ("Oslo-Indoor-Open Facebook", "https://www.facebook.com/p/Oslo-Indoor-Open-100023594956974/"),
            ("Romansys login", "https://nor.romansys.io/login"),
            ("IPSC Rulebooks", "https://www.ipsc.org/ipsc-rules/rule-books/"),
            ("Shootandscoreit", "https://shootnscoreit.com/dashboard/"),
            ("vihtavuori Ladedata riffel", "https://www.vihtavuori.com/reloading-data/rifle-reloading/"),
            ("vihtavuori Ladedata Pistol", "https://www.vihtavuori.com/reloading-data/handgun-reloading/"),
            ("Politiet Våpen", "https://www.politiet.no/tjenester/vapen/"),
            ("Våpen Forum", "https://www.kammeret.no/"),
            ("APP forfatter", "https://github.com"),


        ]

        self.create_buttons()
        self.setLayout(self.layout)

    def create_buttons(self):
        row = 0
        col = 0
        for label, url in self.links:
            button = QPushButton(label)
            button.clicked.connect(lambda _, link=url: webbrowser.open(link))
            self.layout.addWidget(button, row, col)

            col += 1
            if col > 2:
                row += 1
                col = 0

class LinkOpener1(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Link Opener")
        self.layout = QGridLayout()

        self.links = [
            ("Norsegear", "https://www.Norsegear.no"),
            ("Foto", "https://www.foto.no"),
            ("JbShooting.no", "https://nor.romansys.io/login"),
            ("Magne Landrø", "https://www.landro.no/"),
        ]

        self.create_buttons()
        self.setLayout(self.layout)

    def create_buttons(self):
        row = 0
        col = 0
        for label, url in self.links:
            button = QPushButton(label)
            button.clicked.connect(lambda _, link=url: webbrowser.open(link))
            self.layout.addWidget(button, row, col)

            col += 1
            if col > 2:
                row += 1
                col = 0

# -------- Application Execution --------
app = QApplication(sys.argv)
from pathlib import Path
styleFile = Path("blue_mod_style.css").read_text()
app.setStyleSheet(styleFile)
app.setWindowIcon(QIcon('OKTS.png'))

window = MainWindow()
window.show()
sys.exit(app.exec())
