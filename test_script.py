import serial, openpyxl, os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pandas as pd
import pyvisa as visa

from popup_dialog import MyDialog
from power_supply_popup import PowerPopUp
from ex import Auto_Configure

class SerialPortThread(QThread):        #    Thread to update com ports in the network
    com_ports_available = pyqtSignal(list)
###########################################################################################
    def run(self):
        com_ports = []
        for i in range(256):
            try:
                s = serial.Serial('COM'+str(i))
                com_ports.append('COM'+str(i))
                s.close()
            except serial.SerialException:
                pass
        self.com_ports_available.emit(com_ports)
###########################################################################################
class App(QMainWindow):
    def __init__(self):
        super().__init__()
    ###########################################################################################
        self.serial_port = None     # Serial port connection variables
        self.rm = visa.ResourceManager()
        #self.direct_ip = MainWindow()
        ###################################################################
        new_action = QAction('New', self)
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        ###################################################################
        undo_action = QAction('Undo', self)
        redo_action = QAction('Redo', self)
        find_action = QAction('Find', self)
        ###################################################################
        Configure_Automatic_action = QAction('Configure Automatic', self)
        NewCommand_action = QAction('New Command', self)
        ###################################################################
        help_action = QAction('About', self)
    ###########################################################################################
        self.setWindowTitle('Test I2C') #   Application Title
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget) ###   Main layout (total widget)
    ###########################################################################################
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')        # Create the 'File' menu and add actions to it
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        edit_menu = menubar.addMenu('Edit')        # Create the 'Edit' menu

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addAction(find_action)

        tools_menu = menubar.addMenu('Tools')        # Create the 'Terminal' menu
        tools_menu.addAction(Configure_Automatic_action)
        tools_menu.addAction(NewCommand_action)

        help_menu = menubar.addMenu('Help')        # Create the 'Help' menu
        help_menu.addAction(help_action)
    ###########################################################################################
        self.title_layout = QHBoxLayout()       ###   Tile Layout
        self.title_label1 = QLabel('    ')
        self.title_label2 = QLabel('    ')
        self.title_label = QLabel('SERIALPORT CONNECT')        # Title label
        self.title_label.setStyleSheet('font-weight: bold')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_layout.addWidget(self.title_label1)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.title_label2)
        self.main_layout.addLayout(self.title_layout)   #   Adding this HBoxlayout to Main layout
    ###########################################################################################
        self.com_baud_layout = QHBoxLayout()        ### ComPort and Baudrate Layout
        self.com_ports_combo = QComboBox()        # combobox for available com ports
        self.com_baud_layout.addWidget(self.com_ports_combo)
        self.baud_rates_combo = QComboBox()        # combobox for baud rates
        self.baud_rates_combo.addItems(['9600','57600','115200'])
        self.com_baud_layout.addWidget(self.baud_rates_combo)
        self.connect_button = QPushButton('Connect')        # Connect button
        self.connect_button.clicked.connect(self.connect_or_disconnect_serial_port)
        self.com_baud_layout.addWidget(self.connect_button)
        self.refresh_button = QPushButton('Refresh')        # Refresh Button
        self.refresh_button.clicked.connect(self.refresh_connect)
        self.com_baud_layout.addWidget(self.refresh_button)
        self.main_layout.addLayout(self.com_baud_layout)        # Add com_baud_layout to our design
    ###########################################################################################
        self.digital_boxes = QHBoxLayout()
        ###########################################################################################
        self.power_supply_box = QGroupBox('PowerSupply')
        self.power_supply_box.setCheckable(True)
        self.power_supply_box.setStyleSheet("font: bold 10pt")
        self.power_supply_box.setAlignment(Qt.AlignCenter)
        self.powerbox_layout = QVBoxLayout()

        self.power_box = QHBoxLayout()
        self.powerbox_layout.addLayout(self.power_box)
        self.power_supply_box.setLayout(self.powerbox_layout)
        self.power_label = QLabel('Power Supply IP')
        self.power_box.addWidget(self.power_label)
        self.line_insert_power = QLineEdit()
        self.power_box.addWidget(self.line_insert_power)

        self.vol_configure_layout = QHBoxLayout()
        self.curr_vol = QPushButton('Curr V')
        self.Load_PowerSupply_details = QPushButton('Load Power')
        self.vol_configure_layout.addWidget(self.Load_PowerSupply_details)
        self.vol_configure_layout.addWidget(self.curr_vol)
        self.curr_curr = QPushButton('Curr A')
        # self.currCurr = QLineEdit()
        self.vol_configure_layout.addWidget(self.curr_curr)
        # self.vol_configure_layout.addWidget(self.currCurr)

        self.powerbox_layout.addLayout(self.vol_configure_layout)

        # self.minVol.returnPressed.connect(self.setminVol)
        # self.maxVol.returnPressed.connect(self.setMaxVol)
        self.curr_vol.clicked.connect(self.calcCurrentVoltage)
        self.curr_curr.clicked.connect(self.calcCurrCurrent)
        
        self.Load_PowerSupply_details.clicked.connect(self.load_power_configuration)

    ###########################################################################################
        self.electric_load_box = QGroupBox('Electronic Load')
        self.electric_load_box.setCheckable(True)
        self.electric_load_box.setStyleSheet("font: bold 10pt")
        self.electric_load_box.setAlignment(Qt.AlignCenter)
        self.loadbox_layout = QVBoxLayout()

        self.Load_box = QHBoxLayout()
        self.loadbox_layout.addLayout(self.Load_box)
        self.electric_load_box.setLayout(self.loadbox_layout)
        self.line_insert_load = QLineEdit()
        self.Load_box.addWidget(self.line_insert_load)
        # self.power_label = QLineEdit()
        # self.Load_box.addWidget(self.power_label)
        
        self.load_layout = QHBoxLayout()
        self.label_load1 = QLabel('label_load1')
        self.edit_load1 = QLineEdit()
        self.load_layout.addWidget(self.label_load1)
        self.load_layout.addWidget(self.edit_load1)
        self.label_load2 = QLabel('label_load2')
        self.edit_load2 = QLineEdit()
        self.load_layout.addWidget(self.label_load2)
        self.load_layout.addWidget(self.edit_load2)
        self.label_load3 = QLabel('label_load3')
        self.edit_load3 = QLineEdit()
        self.load_layout.addWidget(self.label_load3)
        self.load_layout.addWidget(self.edit_load3)
        self.loadbox_layout.addLayout(self.load_layout)

        self.load_configure_layout = QHBoxLayout()
        self.button_load1 = QPushButton('button_load1')
        self.edit_load4 = QLineEdit()
        self.load_configure_layout.addWidget(self.button_load1)
        self.load_configure_layout.addWidget(self.edit_load4)
        self.button_load2 = QPushButton('button_load2')
        self.edit_load5 = QLineEdit()
        self.load_configure_layout.addWidget(self.button_load2)
        self.load_configure_layout.addWidget(self.edit_load5)

        self.loadbox_layout.addLayout(self.load_configure_layout)
        ##################################################################################
        self.multimeter_box = QGroupBox('Multimeter')
        self.multimeter_box.setCheckable(True)
        self.multimeter_box.setStyleSheet("font: bold 10pt")
        self.multimeter_box.setAlignment(Qt.AlignCenter)
        self.meter_box = QVBoxLayout()
        self.multimeter_box.setLayout(self.meter_box)
        self.line_insert_multimeter = QLineEdit()
        self.meter_box.addWidget(self.line_insert_multimeter)
        # self.meter_label = QLabel()
        # self.meter_box.addWidget(self.meter_label)
    ###########################################################################################
        self.digital_boxes.addWidget(self.multimeter_box)
        self.digital_boxes.addWidget(self.power_supply_box)
        #self.digital_boxes.addWidget(self.electric_load_box)
        self.main_layout.addLayout(self.digital_boxes)

        self.line_insert_multimeter.returnPressed.connect(self.connectmultimeter)
        self.line_insert_power.returnPressed.connect(self.connectpowersupply)
    ###########################################################################################
        # self.output_label = QLabel('Output')       # Second label to display the output
        # self.output_label.setAlignment(Qt.AlignCenter)
        # self.main_layout.addWidget(self.output_label)
        self.text_browser = QTextBrowser()        # Text browser to display the output
        self.main_layout.addWidget(self.text_browser)
    ###########################################################################################
        self.command_layout = QHBoxLayout()     ### Layout for Command label and command insert widgets
        self.command_label = QLabel('Command')      # defining command label
        self.serial_commands_edit = QLineEdit()        # widget for custom serial commands
        self.serial_commands_edit.returnPressed.connect(self.write_serial_commands)
        self.command_layout.addWidget(self.command_label)
        self.command_layout.addWidget(self.serial_commands_edit)
        self.main_layout.addLayout(self.command_layout)
    ###########################################################################################
        self.layout_H1 = QHBoxLayout()      ### Layout for NEXT button and LINE-EDIT fields
        self.test_button = QPushButton('Test1')        # Next button
        self.layout_H1.addWidget(self.test_button)
        self.test_button.clicked.connect(self.open_dialog)

        self.next_button = QPushButton('Next')        # Next button
        self.layout_H1.addWidget(self.next_button)
        self.next_button.clicked.connect(self.on_next)
        self.next_button.setEnabled(False)
    ###########################################################################################
        self.result_line_insert = QLineEdit()
        self.layout_H1.addWidget(self.result_line_insert)
        self.main_layout.addLayout(self.layout_H1)
    ###########################################################################################
        self.voltage_widget = QHBoxLayout()
        self.voltage_Button = QPushButton('Voltage')
        self.vol_edit = QLineEdit()       
        self.voltage_widget.addWidget(self.voltage_Button)
        self.voltage_widget.addWidget(self.vol_edit)
        self.current_Button = QPushButton('Current')
        self.curr_edit = QLineEdit()
        self.voltage_widget.addWidget(self.current_Button)#23
        self.voltage_widget.addWidget(self.curr_edit)
        self.main_layout.addLayout(self.voltage_widget)        
    ###########################################################################################
        self.resulted_command = QLineEdit() # line edit command for showing the resulted command from all the information together
        self.main_layout.addWidget(self.resulted_command)
        ###################################################################
        self.serial_thread = SerialPortThread()
        self.serial_thread.com_ports_available.connect(self.update_com_ports)
        self.serial_thread.start()
        ###################################################################
        self.commands = ['i2c:scan', 'i2c:read:53:04:FC', 'i2c:write:53:', 'i2c:read:53:20:00', 'i2c:write:73:04', 'i2c:scan','i2c:write:21:0300','i2c:write:21:0100','i2c:write:21:01FF', 'i2c:write:73:01',
                          'i2c:scan', 'i2c:write:4F:06990918', 'i2c:write:4F:01F8', 'i2c:read:4F:1E:00']
        
        self.I2C_Commands = ['i2c:read:21:08:F0', ]
        self.next_command_index = 0


        open_action.triggered.connect(self.Load_Excel)
        save_action.triggered.connect(self.Save_Excel)
        Configure_Automatic_action.triggered.connect(self.open_configure)
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        shortcut.activated.connect(self.Save_Excel)

        #self.powersupply = None

    def load_power_configuration(self):
        try:
            print('powersupply value', self.powersupply)
            power_dialog = PowerPopUp(self.rm, self.powersupply)
            power_dialog.button_clicked.connect(self.on_widget_button_clicked)
            power_dialog.exec()
        except AttributeError:
            QMessageBox.information(self, "PowerSupply Status", "Please Connect the PowerSupply to do Further")

    def calcCurrentVoltage(self):
        self.multimeter.write("CONF:VOLTage:DC")
        #self.multimeter.write("VOLTage:DC:RANGe 10")
        present_voltage = self.multimeter.query("READ?")
        self.text_browser.append(present_voltage)

    def calcCurrCurrent(self):
        #self.powersupply.write("CONF:CURRent:DC")
        #self.powersupply.query("CURRent?")
        #self.multimeter.write("CURRent:DC:RANGe 10")
        #present_current = self.powersupply.query("READ?")
        self.text_browser.append(self.powersupply.query("MEASure:CURRent?"))

    def setminVol(self):
        self.powersupply.write(f"VOLTage:PROTection:LOW {self.minVol.text()}")
        print(self.minVol.text())

    def setMaxVol(self):
        self.powersupply.write(f"VOLTage:PROTection:HIGH {self.maxVol.text()}")
        print(self.maxVol.text())

    def open_configure(self):
        dialog = Auto_Configure()
        dialog.exec()
    def open_dialog(self):
        dialog = MyDialog(self.rm, self.multimeter, self)
        print('multi',self.multimeter)
        dialog.exec()
        R709_value = dialog.get_lineinser1_value()
        print(R709_value)

    def connectmultimeter(self):
        self.multimeter = self.rm.open_resource('TCPIP0::'+self.line_insert_multimeter.text()+'::INSTR')
        try:
            if self.multimeter:
                self.text_browser.append('Multimeter Connected')
        except RuntimeError:
            self.meter_label.setText('Multimeter has not been presented')

    def connectpowersupply(self):
        self.powersupply = self.rm.open_resource('TCPIP0::'+self.line_insert_power.text()+'::INSTR')
        try:
            if self.powersupply:
                self.text_browser.append('Powersupply Connected')
        except RuntimeError:
            self.power_label.setText('Powersupply has not been presented')
#####################################################################################################################################################################################
    def refresh_connect(self):
        self.serial_thread.quit()
        self.serial_thread.wait()
        self.serial_thread.start()
#####################################################################################################################################################################################
    def update_com_ports(self, com_ports):
        self.com_ports_combo.clear()
        self.com_ports_combo.addItems(com_ports)
#####################################################################################################################################################################################
    def on_next(self):
        if self.next_command_index < (len(self.commands)+1):        # Append command to text browser and set radio button on
            if self.serial_port:
                command = self.commands[self.next_command_index]
                self.serial_port.write(command.encode())
                self.text_browser.append('Processed Command: '+command + '\n')
                ms_out1 = self.serial_port.readline()
                cmd_out = ms_out1.decode('Ascii')
                self.text_browser.append('received message from Board:'+ cmd_out + '\n')
                self.next_command_index += 1
                self.result_line_insert.setText('cmddd'+'ti'+ cmd_out)
                if self.next_command_index == len(self.commands):                # Disable Next button after all commands have been displayed
                    self.next_button.setEnabled(False)
#####################################################################################################################################################################################
    def connect_or_disconnect_serial_port(self):
        if self.serial_port is None:
            com_port = self.com_ports_combo.currentText()            # Get the selected com port and baud rate
            baud_rate = int(self.baud_rates_combo.currentText())
            self.serial_port = serial.Serial(com_port, baud_rate, timeout=1)            # Create a new serial port object and open it
            self.com_ports_combo.setEnabled(False)  # Disable the combo boxes and change the button text
            self.baud_rates_combo.setEnabled(False)
            self.connect_button.setText('Disconnect')
            self.text_browser.append('Serial Communication Connected \n')
            self.next_button.setEnabled(True)
        else:
            self.serial_port.close()            # Close the serial port
            self.serial_port = None
            self.com_ports_combo.setEnabled(True)            # Enable the combo boxes and change the button text
            self.baud_rates_combo.setEnabled(True)
            self.next_button.setEnabled(False)
            self.connect_button.setText('Connect')
            self.text_browser.append('Communication Disconnected \n')
#####################################################################################################################################################################################
    def write_serial_commands(self):
        if self.serial_port:
            serial_commands = self.serial_commands_edit.text()            # Get the serial commands from the line edit field
            self.serial_port.write(serial_commands.encode())            # Write the serial commands to the serial port
            self.output_label.setText('Output: ' + serial_commands)            # Update the output label and text browser
#####################################################################################################################################################################################
    def start_serial_port_thread(self):
        self.serial_port_thread = SerialPortThread()
        self.serial_port_thread.com_ports_available.connect(self.com_ports_combo.addItems)
        self.serial_port_thread.start()
#####################################################################################################################################################################################
    def closeEvent(self, event):
        if self.serial_port:
            self.serial_port.close()
        super().closeEvent(event)
#####################################################################################################################################################################################
    def Load_Excel(self):
        file_dialog = QFileDialog(self)        # Open file dialog to select an Excel sheet
        file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            file_path = selected_files[0]
        else:
            return
        try:
            excel_data = pd.read_excel(file_path)        # Load the selected Excel sheet
        except pd.errors.EmptyDataError:
            QMessageBox.warning(self, "Empty Sheet", "The selected Excel sheet is empty.")
            return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while loading the Excel sheet:\n{str(e)}")
            return
        self.text_browser.clear()        # Display the data in the text browser
        self.text_browser.append("Loaded Excel Data:" + '\n')
        self.text_browser.append(excel_data.to_string())
#####################################################################################################################################################################################
    def Save_Excel(self):
        port = self.com_ports_combo.currentText()        # Get data from form fields
        baud = self.baud_rates_combo.currentText()
        name, ok = QInputDialog.getText(self, "Save Data", "Enter a name:")        # Ask the user for the name using a popup dialog
        if not ok:
            return
        workbook_name = "mydata.xlsx"        # Open or create Excel workbook and worksheet
        if os.path.exists(workbook_name):
            workbook = openpyxl.load_workbook(workbook_name)
        else:
            workbook = openpyxl.Workbook()
        worksheet = workbook.active
        name_exists = False        # Check if name already exists in the sheet
        for row in worksheet.iter_rows(values_only=True):
            if name == row[0]:
                name_exists = True
                break
        if name_exists:
            reply = QMessageBox.question(
                self, "Name already exists",
                f"{name} already exists. Do you want to save with a different name?",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                new_name, ok = QInputDialog.getText(self, "Save Data", "Enter a different name:")                # Ask the user for a different name using a popup dialog
                if not ok:
                    return
                name = new_name
        data = [name, port, baud]        # Add data to sheet  # Add more data here
        worksheet.append(data)
        workbook.save(workbook_name)        # Save the workbook
        # Optionally, you can open the saved workbook in an external application
        # subprocess.run(["open", workbook_name])
#####################################################################################################################################################################################
    def on_widget_button_clicked(self, message):
        self.text_browser.append(message)
#####################################################################################################################################################################################
if __name__ == '__main__':
    app = QApplication([])
    window = App()
    window.show()
    app.exec()
