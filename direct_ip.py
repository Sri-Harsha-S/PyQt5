import subprocess, socket
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton
import pyvisa as visa
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Device Connection")
        self.setGeometry(100, 100, 400, 200)
        hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(hostname)

        self.rm = visa.ResourceManager()

        self.ps_combobox = QComboBox(self)
        self.ps_combobox.setGeometry(50, 50, 200, 30)
        self.mm_combobox = QComboBox(self)
        self.mm_combobox.setGeometry(50, 100, 200, 30)

        self.connect_ps_button = QPushButton("Connect PS", self)
        self.connect_ps_button.setGeometry(270, 50, 100, 30)
        self.connect_ps_button.clicked.connect(self.connect_power_supply)

        self.connect_mm_button = QPushButton("Connect MM", self)
        self.connect_mm_button.setGeometry(270, 100, 100, 30)
        self.connect_mm_button.clicked.connect(self.connect_multimeter)

        self.populate_comboboxes()
        self.mm = None

    def populate_comboboxes(self):
        ip_list = self.get_ip_addresses()

        for ip_address in ip_list:
            print(ip_address)
            self.ps_combobox.addItem(ip_address)
            self.ps_combobox.setCurrentText(ip_list[1])
            self.mm_combobox.addItem(ip_address)

    def get_ip_addresses(self):
        output = subprocess.check_output("arp -a", shell=True).decode()
        ip_list = []
        for line in output.split('\n'):
            if "." in line:  # Filter only dynamic IP addresses
                ip = line.split()[0]
                if ip != self.local_ip:
                    ip_list.append(ip)
                    print('static', ip_list)
        updated_list = [addresses for addresses in ip_list if ':' not in addresses]

        new_list = []
        for i in updated_list:
            try:
                scope = self.rm.open_resource('TCPIP::'+i+'::5024::SOCKET')
                scope.read_termination = '\n'
                scope.write_termination = '\n'
                resp = scope.query("*IDN?")
                self.mm = scope
                print(self.mm)
                if 'Siglent' in resp:
                    new_list.append(i)
                    new_list.append('192.168.212.20')
                else:
                    print(f"No compatible device found at IP: (i)")
            except visa.VisaIOError as e:
                print(f"Error connecting to IP: {i}, {e}")
        return new_list

    def connect_power_supply(self):
        ip_address = self.ps_combobox.currentText()[1]
        # Connect to power supply using IP address

    def connect_multimeter(self):
        ip_address = self.mm_combobox.currentText()[0]
        # Connect to multimeter using IP address


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
