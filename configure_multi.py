import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QGroupBox, QLabel, QPushButton, QLineEdit, QHBoxLayout

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My GUI")
        self.setGeometry(200, 200, 400, 300)

        # Create the main layout
        layout = QVBoxLayout()

        # Create the combobox
        self.combo_box = QComboBox()
        self.combo_box.addItem("<select>")
        self.combo_box.addItem("Multimeter")
        self.combo_box.addItem("Power Supply")
        self.combo_box.addItem("Elec Load")
        self.combo_box.addItem("Func Generator")
        self.combo_box.currentIndexChanged.connect(self.update_group_box)
        layout.addWidget(self.combo_box)

        # Create the group box
        self.group_box = QGroupBox("Device Settings")
        group_box_layout = QVBoxLayout()
        self.group_box.setLayout(group_box_layout)
        layout.addWidget(self.group_box)

        # Set the main layout
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Keep track of the currently selected option
        self.current_option = None

        # Store the horizontal layouts
        self.ip_layout = None
        self.buttons_layout = None

    def update_group_box(self, index):
        # Clear the group box
        self.clear_group_box()

        # Add widgets based on the selected item
        selected_item = self.combo_box.currentText()
        if selected_item == "Multimeter":
            comport_combo_box = QComboBox()
            comport_combo_box.addItem("COM1")
            comport_combo_box.addItem("COM2")
            comport_combo_box.addItem("COM3")
            self.group_box.layout().addWidget(QLabel("Select COM Port:"))
            self.group_box.layout().addWidget(comport_combo_box)

            baudrate_combo_box = QComboBox()
            baudrate_combo_box.addItem("57600")
            baudrate_combo_box.addItem("115200")
            self.group_box.layout().addWidget(QLabel("Select Baudrate:"))
            self.group_box.layout().addWidget(baudrate_combo_box)

        elif selected_item == "Power Supply":
            self.ip_layout = QHBoxLayout()
            self.buttons_layout = QHBoxLayout()

            self.group_box.layout().addWidget(QLabel("Enter IP Address:"))
            ip_line_edit = QLineEdit()
            self.ip_layout.addWidget(ip_line_edit)

            self.group_box.layout().addWidget(QLabel("Select Port:"))
            port_combo_box = QComboBox()
            self.ip_layout.addWidget(port_combo_box)

            connect_button = QPushButton("Connect")
            self.buttons_layout.addWidget(connect_button)

            refresh_button = QPushButton("Refresh")
            self.buttons_layout.addWidget(refresh_button)

            self.group_box.layout().addLayout(self.ip_layout)
            self.group_box.layout().addLayout(self.buttons_layout)

        # Update the current option
        self.current_option = selected_item

    def clear_group_box(self):
        # Clear the group box
        while self.group_box.layout().count():
            child = self.group_box.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Clear the horizontal layouts if present
        if self.ip_layout:
            while self.ip_layout.count():
                child = self.ip_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.ip_layout = None

        if self.buttons_layout:
            while self.buttons_layout.count():
                child = self.buttons_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.buttons_layout = None

    def show(self):
        super().show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
