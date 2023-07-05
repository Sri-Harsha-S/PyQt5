import sys, subprocess, socket, threading
import pyvisa as visa
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class MyWindow(QDialog):
    button_clicked = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My GUI")
        self.setGeometry(200, 200, 400, 300)


        hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(hostname)
        self.rm = visa.ResourceManager()


        layout = QVBoxLayout()

        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.combo_box = QComboBox()
        self.combo_box.addItem("<select>")
        self.combo_box.addItem("Multimeter")
        self.combo_box.addItem("Power Supply")
        self.combo_box.addItem("Elec Load")
        self.combo_box.addItem("Func Generator")
        self.combo_box.currentIndexChanged.connect(self.update_group_box)
        self.group_box = QGroupBox("Device Settings")
        group_box_layout = QVBoxLayout()
        self.group_box.setLayout(group_box_layout)

        self.ps_combobox = QComboBox()
        self.mm_combobox = QComboBox()

        self.configure_button = QPushButton("Configure")
        layout.addWidget(self.configure_button)
        self.configure_button.setEnabled(True)
        self.configure_button.clicked.connect(self.Configure_ips)

        self.connect_mm_button = QPushButton("Connect MM")
        self.connect_mm_button.setEnabled(False)
        self.connect_mm_button.clicked.connect(self.connect_multimeter)
        self.connect_ps_button = QPushButton('Connect PS')
        self.connect_ps_button.setEnabled(False)
        self.connect_ps_button.clicked.connect(self.connect_powersupply)
        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.ps_combobox)
        layout_1.addWidget(self.connect_ps_button)
        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.mm_combobox)
        layout_2.addWidget(self.connect_mm_button)

        layout.addLayout(layout_1)
        layout.addLayout(layout_2)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.group_box)




        
        
        
        self.power = 0
        self.Voltage = 0
        self.setLayout(layout)

        self.mail_l = None
        self.current_option = None


    def on_button_clicked(self):
        self.button_clicked.emit("Button clicked")


    def populate_comboboxes(self):
        ip_list = self.get_ip_addresses()

        for ip_address in ip_list:
            self.ps_combobox.addItem(ip_address)
            self.mm_combobox.addItem(ip_address)

    def get_ip_addresses(self):
        output = subprocess.check_output("arp -a", shell=True).decode()
        ip_list = []

        for line in output.split('\n'):
            if "." in line:  # Filter only dynamic IP addresses
                ip = line.split()[0]
                if ip != self.local_ip:
                    ip_list.append(ip)

        updated_list = [address for address in ip_list if ':' not in address]

        new_list = []
        lock = threading.Lock()  # Create a lock for thread-safe appending to new_list

        def connect_to_device(ip_address):
            nonlocal new_list
            try:
                self.scope = self.rm.open_resource(f'TCPIP::{ip_address}::5024::SOCKET', timeout=500)
                self.scope.read_termination = '\n'
                self.scope.write_termination = '\n'
                resp = self.scope.query("*IDN?")
                if 'Siglent' in resp:
                    with lock:
                            new_list.append(ip_address)
                    print(f"Device found at IP: {ip_address}")
                else:
                    print(f"No compatible device found at IP: {ip_address}")
            except visa.VisaIOError as e:
                print(f"Error connecting to IP: {ip_address}, {e}")

        threads = []    # Create and start threads for parallel execution
        for ip_address in updated_list:
            thread = threading.Thread(target=connect_to_device, args=(ip_address,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return new_list
    def Configure_ips(self):
        #self.populate_comboboxes()
        self.configure_button.setEnabled(False)
        self.connect_ps_button.setEnabled(True)
        self.connect_mm_button.setEnabled(True)

        # ip_address = self.ps_combobox.currentText()
        # Connect to power supply using IP address

    def connect_multimeter(self):
        #ip_address = self.mm_combobox.currentText()
        print(self.scope.query('*IDN'))
        # Connect to multimeter using IP address
    def connect_powersupply(self):
        pass

    def update_group_box(self, index):
        self.clear_group_box()
        # Clear the group box
        # while self.group_box.layout().count():
        #     child = self.group_box.layout().takeAt(0)
        #     if child.widget():
        #         child.widget().deleteLater()

        # Add widgets based on the selected item
        selected_item = self.combo_box.currentText()
        if selected_item == "Multimeter":
            # Code for Multimeter configuration...
            comport_combo_box = QComboBox()
            comport_combo_box.addItem("COM1")
            comport_combo_box.addItem("COM2")
            comport_combo_box.addItem("COM3")
            self.group_box.layout().addWidget(QLabel("Select COM Port:"))
            self.group_box.layout().addWidget(comport_combo_box)

            baudrate_combo_box = QComboBox()
            baudrate_combo_box.addItem("57600")
            baudrate_combo_box.addItem("115200")
            conn_button = QPushButton("Connect")
            self.group_box.layout().addWidget(conn_button)
            conn_button.clicked.connect(self.runprocess)
            self.group_box.layout().addWidget(QLabel("Select Baudrate:"))
            self.group_box.layout().addWidget(baudrate_combo_box)

        elif selected_item == "Power Supply":
            self.button_clicked.emit("PowerSupply has been selected")
            self.mail_l = QVBoxLayout()  # Create the QVBoxLayout
            # self.group_box.layout().addWidget(QLabel("Enter IP Address:"))
            # ip_line_edit = QLineEdit()
            # self.group_box.layout().addWidget(ip_line_edit)

            self.mail_l.addWidget(QLabel("Additional Settings:"))  # Add widgets to self.mail_l
            self.mail_l.addWidget(QPushButton("Button 1"))
            self.mail_l.addWidget(QPushButton("Button 2"))

            
            self.main_layout = QVBoxLayout()
            
            layout1 = QHBoxLayout()
            label1 = QLabel('Channel')
            label2 = QLabel('Voltage')
            label3 = QLabel('Current')
            label4 = QLabel('Tolerenz')


            lineinser1 = QComboBox()
            lineinser2 = QLineEdit()
            lineinser3 = QLineEdit()
            lineinser4 = QLineEdit()
            
            layout1.addWidget(label1)
            layout1.addWidget(lineinser1)

            lineinser1.addItems(['<select>','Channel 1','Channel 2','Channel 3'])
            # lineinser1.activated.connect(self.channelselct)

            layout2 = QHBoxLayout()
            layout3 = QHBoxLayout()
            layout4 = QHBoxLayout()

            layout2.addWidget(label2)
            layout2.addWidget(lineinser2)

            layout3.addWidget(label3)
            layout3.addWidget(lineinser3)

            layout4.addWidget(label4)
            layout4.addWidget(lineinser4)

            self.mail_l.addLayout(layout1)
            self.mail_l.addLayout(layout2)
            self.mail_l.addLayout(layout3)
            self.mail_l.addLayout(layout4)
            # self.mail_l.addLayout(self.main_layout)
            #self.group_box.layout().addLayout(self.main_layout)
            self.group_box.layout().addLayout(self.mail_l)  # Add self.mail_l layout to the group_box
        self.current_option = selected_item

            # connect_button = QPushButton("Connect")
            # self.group_box.layout().addWidget(connect_button)
            # refresh_button = QPushButton("Refresh")
            # self.group_box.layout().addWidget(refresh_button)

    def clear_group_box(self):
        # Clear the group box
        while self.group_box.layout().count():
            child = self.group_box.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Clear the horizontal layout if present
        if self.mail_l:
            while self.mail_l.count():
                child = self.mail_l.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()


    def runprocess(self):
        print(self.power)
    def enterpower(self):
        self.power = 43
        self.button_clicked.emit("Channel 1 has been selected")
        print(self.power)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
