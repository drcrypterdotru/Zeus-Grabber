import sys

from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QThread, pyqtSignal, QDir, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon, QFontDatabase
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QPlainTextEdit,
    QHBoxLayout, QStackedWidget, QLabel, QFrame, QGridLayout, QRadioButton, QButtonGroup, QGroupBox, QSizePolicy, QTextEdit, QLineEdit, QSpinBox, QMessageBox
)
import requests, time, urllib3, socket
import random, os, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Construct an absolute path to the Zeus_Result folder in the user's home directory
current_dir = QDir.currentPath() + "/Zeus_Result"

# Ensure the directory exists
QDir(current_dir).mkpath(".")

try:
    os.mkdir('Zeus_Result')
except:
    pass 

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36 Edg/117.0.2045.60",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Mobile Safari/537.36",
]



def button_start():
    return """
        QPushButton {
            background-color: #8A2BE2;
            color: white;
            font-size: 16px;
            border: none;
        }
        QPushButton:hover {
            background-color: #1ABC9C;
        }
        QPushButton:pressed {
            background-color: cyan;
        }
    """

def input_style():
    return """
        QLineEdit {
            background-color: #2C3E50;
            color: #ECF0F1;
            font-size: 14px;
            padding: 10px;
            border: 2px solid #1ABC9C;
            border-radius: 10px;
        }
        QLineEdit:focus {
            border: 2px solid #16A085;
        }
    """


def button_style():
    return """
        QPushButton {
            background-color: #1ABC9C;
            color: white;
            font-size: 16px;
            border: none;
            padding: 10px;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #16A085;
        }
        QPushButton:pressed {
            background-color: #1ABC9C;
        }
    """

def Editor_TXTStyle():
    return """
        QTextEdit {
            background-color: #2C3E50;
            color: #ECF0F1;
            border: 2px solid #1ABC9C;
            padding: 10px;
            font-size: 14px;
            border-radius: 10px;
        }

        QScrollBar:vertical {
            border: none;
            background: rgb(52, 73, 94);
            width: 14px;
            margin: 15px 0 15px 0;
            border-radius: 7px;
        }

        QScrollBar::handle:vertical {
            background-color: rgb(26, 188, 156);
            min-height: 30px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #1ABC9C;
        }
        QScrollBar::handle:vertical:pressed {
            background-color: #16A085;
        }

        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::add-line:vertical {
            height: 0px;
        }

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            width: 0px;
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """


def read_list(file_path):
    """Read the IP list from the given file and return it as a list of strings."""
    if not os.path.exists(file_path):
        #print(f"Error: The file {file_path} does not exist.")
        return []
    
    with open(file_path, 'r') as file:
        content = file.read().splitlines()
    return content

def robtex(ip):
    try:
        response = requests.get(f'https://freeapi.robtex.com/ipquery/{ip}', verify=False, timeout=10).json()
        domains = []
        if response['status'] == 'ok':
            for value in response.values():
                try:
                    for item in value:
                        domains.append(item['o'])
                except TypeError:
                    continue
        return domains #if domains else None
    except requests.exceptions.RequestException:
        return None
    except:
        return None
"""
Example Qthread

https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html
https://sihabsahariar.medium.com/a-comprehensive-pyqt5-tutorial-on-qthread-and-qthreadpool-66aa5b768496
https://realpython.com/python-pyqt-qthread/#:~:text=In%20PyQt%2C%20you%20use%20QThread,the%20thread%20as%20an%20argument.
class WorkerThread(QThread):

    Q_OBJECT
    def run():
        result = QString()
        /* ... here is the expensive or blocking operation ... */
        resultReady.emit(result)

# signals
    def resultReady(s):

def startWorkInAThread(self):

    workerThread = WorkerThread(self)
    workerThread.resultReady.connect(self.handleResults)
    workerThread.finished.connect(workerThread.deleteLater)
    workerThread.start()
"""
class DomainCheckerWorker(QThread):
    # Signal to update the console with responsed result
    progress = pyqtSignal(str)
    
    def __init__(self, ip_list, save_path, selected_api):
        super().__init__()
        self.ip_list = ip_list
        self.save_path = save_path  
        #print(selected_api) == 'API #1' if selected will print 
        self.selected_api = selected_api  
        self.unique_domains = set()  # To store unique domains
    
    def handle_rate_limiting(self, retry_count):
        wait_time = 2 ** retry_count
        time.sleep(wait_time)

    def reverse_ip_lookup(self, ip, session, retry_count=0):
        url = f"https://rapiddns.io/sameip/{ip}?full=1&t=None#result"
        headers = {"User-Agent": random.choice(user_agents)}

        try:
            response = session.get(url, headers=headers, verify=False, timeout=10)

            if response.status_code == 429:  # 429 is status code of many requests in server
                if retry_count >= 5:
                    return None  # Done after Retrying after 5 times
                else:
                    self.handle_rate_limiting(retry_count)
                    return self.reverse_ip_lookup(ip, session, retry_count + 1)  # Count per time
            soup = BeautifulSoup(response.text, 'html.parser')
            domains = []

            if soup.find('tbody'):
                for row in soup.find('tbody').find_all('tr'):
                    domain = row.find_all('td')[0].text.strip()
                    domains.append(domain)

            return domains

        except:
            return None

    def run(self):
        with requests.Session() as session:
            for ip in self.ip_list:
                time.sleep(random.uniform(1, 3))
                domains = []
                if self.selected_api == "API #1":
                    domains = self.reverse_ip_lookup(ip, session)
                elif self.selected_api == "API #2":
                    domains = robtex(ip)
                elif self.selected_api == "API #BOTH":
                    domains_1 = self.reverse_ip_lookup(ip, session)
                    domains_2 = []
                    if not domains_1:
                        domains_2 = robtex(ip)
                    domains = (domains_1 or []) + (domains_2 or [])

                if domains:
                    try:
                        self.unique_domains.update(domains)  # Add Domain update with Set
                        self.progress.emit(f"{ip} Domains Founded : {len(domains)}")
                        with open(self.save_path, 'a') as file:
                            for domain in domains:
                                if '.*' in str(domain):
                                    domain = str(domain).split('.*')[1]
                                #Emit Domain and WriteFile
                                self.progress.emit(f"{domain}")
                                file.write(f"{domain}\n")
                    except: 
                        pass 
                #No found domain or IP has no domain 
                else:
                    self.progress.emit(f"{ip} : IP has no Domain")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.result_data = ""  #Res Stored
        self.ip_list = []  # ListIP from  selected file
        self.save_path = ""
        self.setWindowTitle("Zeus Grabber v1.0 | By DRCrypter.ru")
        self.setWindowIcon(QIcon(resource_path('Files/icon1.png')))
        self.setGeometry(200, 100, 1000, 600)

        # Main widget with layout
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1C1C1C;
                color: white;
            }
        """)

        # Sidebar Config
        self.sidebar_expanded = True
        self.sidebar_width = 180  
        self.collapsed_sidebar_width = 60 

        # Side_Frame with border_radius
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 9px;
            }
        """)
        self.sidebar.setFixedWidth(self.sidebar_width)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(0)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Logo sidebar
        self.logo = QLabel()
        self.logo.setFixedHeight(120)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(resource_path("Files/logo.png"))
        self.logo.mousePressEvent = self.toggle_sidebar  # Add click event
        self.logo.setPixmap(pixmap.scaled(90, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.sidebar_layout.addWidget(self.logo)

        


        # sidebar_button
        sidebar_button = """
        QPushButton {
            background-color: #34495E;
            color: white;
            font-size: 14px;
            border: none;
            text-align: left;
            padding-left: 10px;
        }
        QPushButton:hover {
            background-color: #1ABC9C;
        }
        QPushButton:pressed {
            background-color: #16A085;
        }
        """

        # Sidebar buttons
        titles = ["Reverse IP", "Generate IP", "Google", "Zone-H"]
        self.page_buttons = []
        self.icon_size = QSize(24, 24)

        for i, title in enumerate(titles):
            button = QPushButton(title)
            button.setStyleSheet(sidebar_button)
            button.setFixedHeight(50)
            button.setIcon(QIcon(resource_path(f"Files/icon{i+1}.png")))
            button.setIconSize(self.icon_size)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked, idx=i: self.animate_page_transition(idx))
            self.page_buttons.append(button)
            self.sidebar_layout.addWidget(button)

        # Add stretch Push_Button to the top
        self.sidebar_layout.addStretch()

        # Sidebar Main_layout
        main_layout.addWidget(self.sidebar)
         
        #https://stackoverflow.com/questions/52596386/slide-qstackedwidget-page
        # Pages container (QStackedWidget) 
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background-color: None; border-radius: 10px;")
        main_layout.addWidget(self.pages)

        # AddPages 2 QStackedWidget 
        self.pages.addWidget(self.ReverseIP_Page0())
        self.pages.addWidget(DomainToIPPage())
        self.pages.addWidget(Google_Grabber())
        self.pages.addWidget(ZoneH_Grabber())


    def ReverseIP_Page0(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        # TopLayer_BTN
        top_layout = QGridLayout()

        # File_Selection_BTN with Hover Effects
        self.file_button = QPushButton("Select *.TXT")
        self.file_button.setFixedSize(150, 40)
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #16A085;
                color: white;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1ABC9C;
            }
            QPushButton:pressed {
                background-color: #16A085;
            }
        """)
        self.file_button.clicked.connect(self.select_file)
        top_layout.addWidget(self.file_button, 0, 0, Qt.AlignmentFlag.AlignLeft)

        # Radio_BTN for API selection
        self.api_group = QButtonGroup()
        self.api1_radio = QRadioButton("API #1")
        self.api1_radio.setChecked(True)
        self.api1_radio.setStyleSheet("font-size: 14px; color: white;")
        self.api_group.addButton(self.api1_radio)

        self.api2_radio = QRadioButton("API #2")
        self.api2_radio.setStyleSheet("font-size: 14px; color: white;")
        self.api_group.addButton(self.api2_radio)

        self.api_both_radio = QRadioButton("API #BOTH")
        self.api_both_radio.setStyleSheet("font-size: 14px; color: white;")
        self.api_group.addButton(self.api_both_radio)

        # Add_Radio_BTN to my Layout
        top_layout.addWidget(self.api1_radio, 0, 1)
        top_layout.addWidget(self.api2_radio, 0, 2)
        top_layout.addWidget(self.api_both_radio, 0, 3)

        layout.addLayout(top_layout)

        # Console area

        #thank info with scollbar custom modern ui : https://github.com/Wanderson-Magalhaes/Custom_ScrollBar_QtDesigner/blob/main/Scroll-Bar-Custom.ui
        self.console_area = QPlainTextEdit()
        self.console_area.setFont(QFont("Arial", 12))
        self.console_area.setPlaceholderText("Console Log")
        self.console_area.setStyleSheet("""
            QPlainTextEdit {
                background-color: #34495E;  /* Background color for the text area */
                border: 2px solid #1ABC9C;  /* Border for the text area */
                padding: 10px;
                color: white;
                border-radius: 10px;        /* Rounded corners for the text area */
            }

            QScrollBar:vertical {
                border: none;
                background: rgb(52, 73, 94);
                width: 14px;
                margin: 15px 0 15px 0;
                border-radius: 7px;  /* Rounded corners for the scrollbar background */
            }

            /* HANDLE BAR VERTICAL */
            QScrollBar::handle:vertical {	
                background-color: rgb(26, 188, 156);
                min-height: 30px;
                border-radius: 7px;  /* Rounded corners for the handle */
            }
            QScrollBar::handle:vertical:hover {	
                background-color: #1ABC9C;
            }
            QScrollBar::handle:vertical:pressed {	
                background-color: #16A085;
            }

            /* BTN TOP - SCROLLBAR */
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            /* BTN BOTTOM - SCROLLBAR */
            QScrollBar::add-line:vertical {
                height: 0px;
            }

            /* RESET ARROW */
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.console_area.setReadOnly(True)  # Allow_USER Permission Read_Only
        layout.addWidget(self.console_area)

        #  START and SAVE
        save_start_layout = QHBoxLayout()

        # Start_BTN
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(150, 40)
        self.start_button.setStyleSheet(button_start())
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.START_Rev)
        save_start_layout.addWidget(self.start_button, Qt.AlignmentFlag.AlignRight)

        # Save_BTN
        self.save_button = QPushButton("Save *.TXT")
        self.save_button.setFixedSize(150, 40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #1ABC9C;
                color: white;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #16A085;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
            }
        """)
        self.save_button.clicked.connect(self.SAVE_REVDATA)
        save_start_layout.addWidget(self.save_button, Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(save_start_layout)

        page.setLayout(layout)
        return page

  
    def select_file(self):
        """OpenFile Dialog todo select File"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text Files (*.txt)")
        if file_path:
            self.ip_list = read_list(file_path) 
            if self.ip_list:
                self.start_button.setEnabled(True)  
            else:
                return 
                #print("The selected file is empty or cannot be read.")

    def START_Rev(self):
        """Function when users click start Reverse IP"""
        if not self.ip_list:
            #print("No IP addresses to process.")
            return
    
        self.console_area.clear()
        self.result_data = ""   

        # Which users was selected
        if self.api1_radio.isChecked():
            selected_api = "API #1"
        elif self.api2_radio.isChecked():
            selected_api = "API #2"
        else:
            selected_api = "API #BOTH"
    
        if not self.save_path:
            return 

        
        self.tasker = DomainCheckerWorker(self.ip_list, self.save_path, selected_api)
        self.tasker.progress.connect(self.update_console)
        self.tasker.start()

    def SAVE_REVDATA(self):
        """Save Result"""
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", f"{current_dir}", "Text Files (*.txt)")
        if save_path:
            try:
                self.save_path = save_path
                with open(save_path, 'w') as file: 
                    file.write(self.result_data) 
            except:
                pass 

    def update_console(self, message):
        self.console_area.appendPlainText(message)

    def animate_page_transition(self, new_index):
        self.pages.setCurrentIndex(new_index)

    def toggle_sidebar(self, event):
        titles = ["Reverse IP", "Generate IP", "Google", "Zone-H"]
        """https://youtu.be/Kp8lA294U1g 
        Toggle with animation on sidebar"""
        if self.sidebar_expanded:
            self.animate_sidebar(self.sidebar_width, self.collapsed_sidebar_width)
            for button in self.page_buttons:
                button.setText("")   
                button.setIconSize(self.icon_size)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #34495E;
                        color: white;
                        font-size: 16px;
                        border: none;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #1ABC9C;
                    }
                    QPushButton:pressed {
                        background-color: #16A085;
                    }
                """)
        else:
            self.animate_sidebar(self.collapsed_sidebar_width, self.sidebar_width)
            for i, button in enumerate(self.page_buttons):
                button.setText(titles[i])  # Restore the text from titles list
                button.setIconSize(self.icon_size)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #34495E;
                        color: white;
                        font-size: 14px;
                        border: none;
                        padding-left: 10px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #1ABC9C;
                    }
                    QPushButton:pressed {
                        background-color: #16A085;
                    }
                """)
        self.sidebar_expanded = not self.sidebar_expanded
    #Smooth animation with func toggle_sidebar
    def animate_sidebar(self, start_width, end_width):
        
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(300)  # Animation duration in milliseconds
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.start()
#############################################################################
#Page 2 

##https://www.digitalocean.com/community/tutorials/python-get-ip-address-from-hostname

class DomainToIP_Func(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, domain, path_result, parent=None):
        super().__init__(parent)
        self.domain = domain
        self.save_file = path_result

    def run(self):
        try:
            #maybe skip result if reduce number with this will make your code slow but make its work without skip IP 
            socket.setdefaulttimeout(7)
            ip_address = socket.gethostbyname(self.domain)
            self.result_signal.emit(f"{self.domain} --> {ip_address}")
            with open(self.save_file, 'a') as data_ip:
                data_ip.write(ip_address + '\n')
        except socket.error:
            self.result_signal.emit(f"{self.domain} --> Failed")

class DomainToIPPage(QWidget):
    def __init__(self):
        super().__init__()
        self.ip_list = []
        self.threads = []
        self.save_path = ""
        self.qt_UI()

    def qt_UI(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # JUST ADD Title 
        title_label = QLabel("Bulk Domain to IP")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Button Row for domain operations (small buttons)
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(20)  # Add spacing between buttons

        # Console Log for Reverse IP Lookup (rich text box)
        reverse_ip_console_section = QGroupBox("")
        reverse_ip_console_layout = QVBoxLayout()
        self.console_log = QTextEdit(self)
        self.console_log.setPlaceholderText("Console Log")
        self.console_log.setReadOnly(True)
        self.console_log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.console_log.setStyleSheet(Editor_TXTStyle())
        # self.console_log.setStyleSheet("""
        #     QTextEdit {
        #         background-color: #2C3E50;
        #         color: #ECF0F1;
        #         border: 2px solid #1ABC9C;
        #         padding: 10px;
        #         font-size: 14px;
        #         border-radius: 10px;
        #     }

        #     QScrollBar:vertical {
        #         border: none;
        #         background: rgb(52, 73, 94);
        #         width: 14px;
        #         margin: 15px 0 15px 0;
        #         border-radius: 7px;  /* Rounded corners for the scrollbar background */
        #     }

        #     /* HANDLE BAR VERTICAL */
        #     QScrollBar::handle:vertical {	
        #         background-color: rgb(26, 188, 156);
        #         min-height: 30px;
        #         border-radius: 7px;  /* Rounded corners for the handle */
        #     }
        #     QScrollBar::handle:vertical:hover {	
        #         background-color: #1ABC9C;
        #     }
        #     QScrollBar::handle:vertical:pressed {	
        #         background-color: #16A085;
        #     }

        #     /* BTN TOP - SCROLLBAR */
        #     QScrollBar::sub-line:vertical {
        #         height: 0px;
        #     }

        #     /* BTN BOTTOM - SCROLLBAR */
        #     QScrollBar::add-line:vertical {
        #         height: 0px;
        #     }

        #     /* RESET ARROW */
        #     QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        #         width: 0px;
        #         height: 0px;
        #     }
        #     QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        #         background: none;
        #     }
        # """)
        reverse_ip_console_layout.addWidget(self.console_log)
        reverse_ip_console_section.setLayout(reverse_ip_console_layout)
        layout.addWidget(reverse_ip_console_section)

        self.load_txt_btn = QPushButton('Domain Load')
        self.load_txt_btn.setFixedSize(150, 40)
        self.load_txt_btn.setStyleSheet(button_style())
        self.load_txt_btn.clicked.connect(self.Select_List)

        self.start_dom2ip_btn = QPushButton('Start Dom2IP')  
        self.start_dom2ip_btn.setFixedSize(150, 40)
        self.start_dom2ip_btn.setStyleSheet(button_start())
        self.start_dom2ip_btn.setEnabled(False)
        self.start_dom2ip_btn.clicked.connect(self.START_DumperIP)

        self.save_result_btn = QPushButton('Save IPList')
        self.save_result_btn.setFixedSize(200, 40)
        self.save_result_btn.setStyleSheet(button_style())
        self.save_result_btn.clicked.connect(self.Save_ReverseIPResults)

        button_layout.addWidget(self.load_txt_btn)
        button_layout.addWidget(self.start_dom2ip_btn)
        button_layout.addWidget(self.save_result_btn)

        layout.addLayout(button_layout)

        ip_output_console_section = QGroupBox("")
        ip_output_console_layout = QVBoxLayout()
        self.ip_console = QTextEdit(self)
        self.ip_console.setPlaceholderText("Generated Log")
        self.ip_console.setReadOnly(True)
        self.ip_console.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ip_console.setStyleSheet(Editor_TXTStyle())
        ip_output_console_layout.addWidget(self.ip_console)
        ip_output_console_section.setLayout(ip_output_console_layout)
        layout.addWidget(ip_output_console_section)

        input_layout = QHBoxLayout()
        self.how_many_ip_input = QLineEdit(self)
        self.how_many_ip_input.setFixedWidth(250)
        self.how_many_ip_input.setPlaceholderText("How many IPs")
        self.how_many_ip_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.how_many_ip_input.setStyleSheet(input_style())

        self.generate_ip_btn = QPushButton("Generate IP")
        self.generate_ip_btn.setFixedSize(150, 40)
        self.generate_ip_btn.setStyleSheet(button_start())
        self.generate_ip_btn.clicked.connect(self.Generator_IP)

        self.save_generated_ip_btn = QPushButton("Save GenerateList")
        self.save_generated_ip_btn.setFixedSize(150, 40)
        self.save_generated_ip_btn.setStyleSheet(button_style())
        self.save_generated_ip_btn.clicked.connect(self.Save_GeneratedIP)

        input_layout.addWidget(self.generate_ip_btn)
        input_layout.addWidget(self.how_many_ip_input)
        input_layout.addWidget(self.save_generated_ip_btn)

        layout.addLayout(input_layout)

    def URL2HOST(self, site):
        if site.startswith("http://"):
            site = site.replace("http://", "")
        elif site.startswith("https://"):
            site = site.replace("https://", "")
        site = site.strip()
        pattern = re.compile(r'([^/]+)')
        match = re.findall(pattern, site)
        if match:
            domain = match[0]
        else:
            domain = urlparse(site).netloc
        return domain

    def Select_List(self):
        """OpenFILE Select IP"""
        iplist_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text Files (*.txt)")
        if iplist_path:
            with open(iplist_path, 'r') as file:
                self.ip_list = [line.strip() for line in file]
            if self.ip_list:  
                self.start_dom2ip_btn.setEnabled(True)  # Enable Domain to IP Start_BTN
            else:
                print("The selected file is empty or cannot be read.")

    def START_DumperIP(self):
        if not self.ip_list:
            self.console_log.setPlainText("No domains loaded.")
            return
        
        if not self.save_path:
            QMessageBox.warning(self, "No Save Path", "Please select a valid save path.")
            return
        
        self.console_log.append("IPLog will show results:")
        for domain in self.ip_list:
            thread = DomainToIP_Func(domain, self.save_path)
            thread.result_signal.connect(self.update_console_log)
            thread.start()
            self.threads.append(thread)
       
    def update_console_log(self, result):
        self.console_log.append(result)

    def Generator_IP(self):
        try:
            count = int(self.how_many_ip_input.text())
            generated_ips = []
            for _ in range(count):
                ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
                generated_ips.append(ip)
            self.ip_console.setPlainText("\n".join(generated_ips))
        except ValueError:
            self.ip_console.setPlainText("Please Type number of IP you want Generate")


    def Save_GeneratedIP(self):
        save_ip, _ = QFileDialog.getSaveFileName(self, "Save File", f"{current_dir}", "Text Files (*.txt)")
        if save_ip:
            try:
                with open(save_ip, 'w') as file:
                    file.write(self.ip_console.toPlainText())
                self.ip_console.setPlainText(f"Generated IPs saved successfully to: {save_ip}")
            except Exception as e:
                self.ip_console.setPlainText(f"Error saving file: {e}")

    def Save_ReverseIPResults(self):
        self.save_path, _ = QFileDialog.getSaveFileName(self, "Save File", f"{current_dir}", "Text Files (*.txt)")
        if self.save_path:
            try:
                with open(self.save_path, 'w') as file:
                    file.write(self.console_log.toPlainText())
                self.console_log.setPlainText(f"Reverse IP results saved successfully to: {self.save_path}")
            except Exception as e:
                self.console_log.setPlainText(f"Error saving file: {e}")



#This coded was operated in 2022-2023 jst remastered 
class KillAllPageWorker(QThread):
    result_signal = pyqtSignal(str)  # SENT RESULT

    def __init__(self, query_list, n_pages, blocked_domains, save_path, domain_radio, url_radio, url_domain_radio, parent=None):
        super().__init__(parent)
        self.path_file = save_path
        self.dork_queries = query_list
        self.n_pages = n_pages
        self.blocked_domains = blocked_domains
        self.domain_radio = domain_radio
        self.url_radio = url_radio
        self.url_domain_radio = url_domain_radio
        
    
    def Domain_Kicker(self, domain):
        domain_data = str(domain).split('/')
        domain_value = domain_data[0] + "//" + domain_data[2] + '/' 
        return domain_value
        
    def captcha_google(self, driver):
        """Handles CAPTCHA detection and waits for it to resolve"""
        try:
            element = driver.find_element(By.XPATH, "//div[@class='g-recaptcha']")
            WebDriverWait(driver, timeout=5000).until(EC.staleness_of(element))  # Wait until CAPTCHA is solved
        except Exception as e:
            print(f"Error handling CAPTCHA: {e}")  # Log any errors encountered

    def run(self):
        driver_path = ChromeDriverManager().install()
        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["disable-logging"])
        driver = webdriver.Chrome(service=Service(driver_path), options=options)

        try:
            for query_x in self.dork_queries:
                for page in range(1, self.n_pages + 1):
                    url = f"http://www.google.com/search?q={query_x}&start={(page - 1) * 10}"
                    TRYNG = True
                    
                    while TRYNG: 
                        driver.get(url)
                        soup = BeautifulSoup(driver.page_source, 'html.parser')

                        # check if search got captcha 
                        if 'Our systems have detected' in soup.text:
                            self.captcha_google(driver)  #manually complete captcha and retry
                        else:
                            TRYNG = False  #Try Again after complete captcha
                            search = soup.find_all('div', class_="yuRUbf")
                            if search:
                                for h in search:
                                    link = h.a['href']
                                    if link:
                                        blocked = False
                                        for blocked_domain in self.blocked_domains:
                                            if blocked_domain in link:
                                                blocked = True
                                                break
                                        if not blocked:
                                            result = f"[{page}] : {link}"
                                            self.result_signal.emit(result)  
                                            
                                            if self.domain_radio:
                                                domain_ = self.Domain_Kicker(link)
                                                with open(f'{self.path_file}_Domain.txt', 'a') as file:
                                                    file.write(domain_ + '\n')

                                            if self.url_radio:
                                                with open(f'{self.path_file}_URLink.txt', 'a') as file:
                                                    file.write(link + '\n')

                                            if self.url_domain_radio:
                                                domain_ = self.Domain_Kicker(link)
                                                with open(f'{self.path_file}_URLink.txt', 'a') as file:
                                                    file.write(link + '\n')
                        
                                                with open(f'{self.path_file}_Domain.txt', 'a') as file:
                                                    file.write(domain_ + '\n')

        except:
            pass


class Google_Grabber(QWidget):
    def __init__(self):
        super().__init__()
        self.save_path = ""
        self.threads = [] 
        self.qt_UI()
        
    def qt_UI(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Just title or you can remove it 
        mode_selection_label = QLabel("Wizard Grabber :D !!")
        mode_selection_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(mode_selection_label)

        radio_and_input_layout = QHBoxLayout()
        radio_font = QFont("Arial", 12)

        self.domain_radio = QRadioButton('Domain        ')
        self.domain_radio.setFont(radio_font)

        self.url_radio = QRadioButton('URL        ')
        self.url_radio.setFont(radio_font)

        self.url_domain_radio = QRadioButton('Domain + URL        ')
        self.url_domain_radio.setFont(radio_font)

        radio_and_input_layout.addWidget(self.domain_radio)
        radio_and_input_layout.addWidget(self.url_radio)
        radio_and_input_layout.addWidget(self.url_domain_radio)
        radio_and_input_layout.addStretch()

        #num input of page you want scrape of google
        self.number_input_label = QLabel("How Many Pages:")
        self.number_input_label.setFont(QFont("Arial", 12))
        self.Num_Page = QSpinBox()
        self.Num_Page.setFixedSize(70, 40)
        self.Num_Page.setFont(QFont("Arial", 12))
        self.Num_Page.setRange(1, 100)
        self.Num_Page.setValue(10)

        self.Num_Page.setStyleSheet("""
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0;
                height: 0;
                border: none;
            }
            QSpinBox {
                padding-right: 5px;  /* Adjust padding to make it look good without arrows */
            }
        """)

        radio_and_input_layout.addWidget(self.number_input_label)
        radio_and_input_layout.addWidget(self.Num_Page)

        layout.addLayout(radio_and_input_layout)

        # TextArea input Dork_List
        self.dork_list = QTextEdit()
        self.dork_list.setPlaceholderText("Dork_List here")
        self.dork_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.dork_list.setStyleSheet(Editor_TXTStyle())

        # TextArea add block_domain
        self.block_domain = QTextEdit()
        self.block_domain.setPlaceholderText("Filter Block Domain : Must add without http/https or www")
        self.block_domain.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.block_domain.setStyleSheet(Editor_TXTStyle())

        # Load Block_domains from file TXT
        self.Load_DomainBlocker()
        
        # Domain_LOG textArea
        self.domain_result = QTextEdit()
        self.domain_result.setPlaceholderText("Domain Logged")
        self.domain_result.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.domain_result.setStyleSheet(Editor_TXTStyle())

        # Dork List, Add Block Domain, and Domain Result
        list_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        left_layout.addWidget(self.dork_list)
        left_layout.addWidget(self.block_domain)

        list_layout.addLayout(left_layout)
        list_layout.addWidget(self.domain_result)
        layout.addLayout(list_layout)

        # Bottom Buttons (Start Grabber, Save Result, Save Blocked Domains)
        button_layout = QHBoxLayout()

        self.start_grabber_btn = QPushButton('Start Grabber')
        self.start_grabber_btn.setFixedSize(150, 40)
        self.start_grabber_btn.setStyleSheet(button_start())
        self.start_grabber_btn.clicked.connect(self.start_grabber)

        self.save_result_btn = QPushButton('Save Result')
        self.save_result_btn.setFixedSize(150, 40)
        self.save_result_btn.setStyleSheet(button_style())

        self.save_blocked_domains_btn = QPushButton('Save Blocked Domains')
        self.save_blocked_domains_btn.setFixedSize(200, 40)
        self.save_blocked_domains_btn.setStyleSheet(button_style())


        self.save_result_btn.clicked.connect(self.SaveResult)
        self.save_blocked_domains_btn.clicked.connect(self.save_blocked_domains)

        button_layout.addWidget(self.save_blocked_domains_btn)
        button_layout.addWidget(self.start_grabber_btn)
        button_layout.addWidget(self.save_result_btn)
        
        
        layout.addLayout(button_layout)
        
    def save_blocked_domains(self):
        blocked_domains = self.block_domain.toPlainText()
        with open('domain_block.txt', 'w') as file:
            file.write(blocked_domains)

    def SaveResult(self):
        self.save_path, _ = QFileDialog.getSaveFileName(self, "Save File", f"{current_dir}", "Text Files (*.txt)")
        if not self.save_path:
            QMessageBox.warning(self, "No Save Path", "Please select a valid save path.")
            return False

        if not (self.domain_radio.isChecked() or self.url_radio.isChecked() or self.url_domain_radio.isChecked()):
            QMessageBox.warning(self, "No Option Selected", "Please select Domain, URL, or Domain + URL option.")
            return False

        self.path_file, file_extension = os.path.splitext(self.save_path)

        try:
            if self.domain_radio.isChecked():
                domain_file_path = f'{self.path_file}_Domain.txt'
                with open(domain_file_path, 'w') as domain_file:
                    domain_file.write(self.domain_result.toPlainText())

            elif self.url_radio.isChecked():
                url_file_path = f'{self.path_file}_URLink.txt'
                with open(url_file_path, 'w') as url_file:
                    url_file.write(self.domain_result.toPlainText())

            elif self.url_domain_radio.isChecked():
                domain_file_path = f'{self.path_file}_Domain.txt'
                with open(domain_file_path, 'w') as domain_file:
                    domain_file.write(self.domain_result.toPlainText())

                url_file_path = f'{self.path_file}_URLink.txt'
                with open(url_file_path, 'w') as url_file:
                    url_file.write(self.domain_result.toPlainText())

            QMessageBox.information(self, "Save Successful", "Files saved successfully!")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error Saving", f"Error Saving : {e}")
            return False
        
    
    def start_grabber(self):
        self.path_file, file_extension = os.path.splitext(self.save_path)
        if not self.path_file:
            QMessageBox.information(self, "Not Found", "Please Save Result *txt")
            return

        #dork_input
        dork_queries = self.dork_list.toPlainText().splitlines()
        n_pages = self.Num_Page.value()
        blocked_domains = self.Load_DomainBlocker()

        # Check if a domain filter is selected
        domain_radio_checked = self.domain_radio.isChecked()
        url_radio_checked = self.url_radio.isChecked()
        url_domain_radio_checked = self.url_domain_radio.isChecked()

        if not (domain_radio_checked or url_radio_checked or url_domain_radio_checked):
            QMessageBox.warning(self, "No Option Selected", "Please select Domain, URL, or Domain + URL option.")
            return
        
        self.task_th = KillAllPageWorker(dork_queries, n_pages, blocked_domains, self.path_file,
                                               domain_radio_checked, url_radio_checked, url_domain_radio_checked)
        self.task_th.result_signal.connect(self.update_result)
        self.task_th.start()


       
    def update_result(self, result):
        self.domain_result.append(result)



    def Load_DomainBlocker(self):
        blocked_domains_list = []
        if os.path.exists('domain_block.txt'):
            with open('domain_block.txt', 'r') as file:
                blocked_domains = file.readlines()  
                blocked_domains_list = [domain.strip() for domain in blocked_domains]  # Strip spaces/newlines
                self.block_domain.setPlainText("\n".join(blocked_domains_list))  # Set Display in the txtArea
        else:
            self.block_domain.setPlainText("")  # Clear if no file domain_block.txt
        return blocked_domains_list 

        



class ZoneH_GrabThread(QThread):
    update_output = pyqtSignal(str)

    def __init__(self, attacker_name, save_path, n_pages):
        super().__init__()
        self.attacker_name = attacker_name
        self.n_pages = n_pages
        self.save_located = save_path

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--log-level=0')
        # chrome_options.add_argument('--headless') #dont run with headless will be hidden chrome and users cant see captcha to complete in manually

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver


    def captcha(self, driver):
        element = driver.find_element('xpath', "//*[text() = 'Copy the code:']")
        datax = WebDriverWait(driver, timeout=2000).until(EC.staleness_of(element))
        return datax

    def run(self):
        driver = self.setup_driver()
        i = 0
        try:
            for page in range(self.n_pages):
                url = f"https://www.zone-h.org/archive/notifier={self.attacker_name}/page={page}"
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                if 'Copy the code:' in soup.text and 'If you often get this captcha when gathering data, please contact us' in soup.text:
                    self.update_output.emit("[INFO] Please solve Captcha in manually.")
                    self.captcha(driver)
                else:
                    if 'Total notifications' in soup.text and 'Legend' in soup.text:
                        try:
                            tablezoneh = soup.find('table', {'id': 'ldeface'})
                            bodyzoneh = tablezoneh.find('tbody')

                            for tr in bodyzoneh.find_all('tr'):
                                tds = tr.find_all('td')
                                if len(tds) < 8:
                                    continue

                                date = tds[0].text.strip()
                                domain = tds[7].text.strip()

                                if 'Domain' not in domain:
                                    i += 1

                                    if '/' in domain:
                                        domain = str(domain.split('/', 1)[0]).replace('...', '')

                                    output = f'[{i}] Domain : {domain} ---> Page >>> {page} | {date}'
                                    self.update_output.emit(output)
                                
                                    with open(f'{self.save_located}', 'a') as f_takedown:
                                        f_takedown.write(domain + '\n')
                                    with open('Zeus_Result/AllZoneH_Domain.txt', 'a') as f_all:
                                        f_all.write(domain + '\n')

                        except Exception as e:
                            self.update_output.emit(f"Error Page {page}: {e}")
            driver.quit()                
        except Exception as e:
            self.update_output.emit(f"Error: {e}")
        
        
#Func has coded in 2022-23 
#Warning page 51 no need change all just 51 pages only no more less
class ZoneH_Grabber(QWidget):
    def __init__(self):
        super().__init__()
        self.save_path = ""
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("ZoneH Grabber")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        attacker_label = QLabel("Attacker Name:")
        attacker_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ECF0F1;")
        layout.addWidget(attacker_label)

        self.attacker_input = QLineEdit(self)
        self.attacker_input.setPlaceholderText("Enter Attacker Name")
        self.attacker_input.setStyleSheet(input_style())
        layout.addWidget(self.attacker_input)

        self.output_box = QTextEdit(self)
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("Zone-Log")
        self.output_box.setStyleSheet(Editor_TXTStyle())
        layout.addWidget(self.output_box)

        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save", self)
        self.save_button.setFixedSize(150, 40)
        self.save_button.setStyleSheet(button_style())
        self.save_button.clicked.connect(self.Save_DATA)
        
        self.grab_button = QPushButton("START-H", self)
        self.grab_button.setFixedSize(150, 40)
        self.grab_button.setStyleSheet("""
        QPushButton {
            background-color: #8A2BE2;
            color: white;
            font-size: 16px;
            border: none;
        }
        QPushButton:hover {
            background-color: #1ABC9C;
        }
        QPushButton:pressed {
            background-color: cyan;
        }
                                       """)
        self.grab_button.clicked.connect(self.START_ZH)

        button_layout.addWidget(self.grab_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)


    def Save_DATA(self):
        attacker_name = self.attacker_input.text()
        
        if attacker_name:

            # OpenDialog Start Zeus_Result folder
            self.save_path, _ = QFileDialog.getSaveFileName(self, "Save File", f"{current_dir}/{attacker_name}", "Text Files (*.txt)")
            
            if self.save_path:
                try:
                    with open(self.save_path, 'w') as file:
                        file.write(self.output_box.toPlainText())
                # except Exception as e:
                #     print(f"Error saving file: {e}")
                except:
                    pass 
    def START_ZH(self):
        attacker_name = self.attacker_input.text()
        if not self.save_path:
            QMessageBox.warning(self, "No Save Path", "Please select a valid save path.")
        else:
            #verify again
            if attacker_name or self.save_path:
                self.grab_thread = ZoneH_GrabThread(attacker_name, self.save_path, 51)
                self.grab_thread.update_output.connect(self.update_console)
                self.grab_thread.start()
        
    def update_console(self, text):
        self.output_box.append(text)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec()) 
