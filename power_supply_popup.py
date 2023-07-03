from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PowerPopUp(QDialog):
    button_clicked = pyqtSignal(str)
    def __init__(self, rm, powersupply, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dialog")
        main_layout = QVBoxLayout()
        
        layout1 = QHBoxLayout()
        self.label1 = QLabel('Channel')
        self.label2 = QLabel('Voltage')
        self.label3 = QLabel('Current')
        self.label4 = QLabel('Tolerenz')


        self.lineinser1 = QComboBox()
        self.lineinser2 = QLineEdit()
        self.lineinser3 = QLineEdit()
        self.lineinser4 = QLineEdit()
        
        layout1.addWidget(self.label1)
        layout1.addWidget(self.lineinser1)

        self.lineinser1.addItems(['Channel 1','Channel 2','Channel 3'])
        self.lineinser1.activated.connect(self.channelselct)

        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()

        layout2.addWidget(self.label2)
        layout2.addWidget(self.lineinser2)

        layout3.addWidget(self.label3)
        layout3.addWidget(self.lineinser3)

        layout4.addWidget(self.label4)
        layout4.addWidget(self.lineinser4)

        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        main_layout.addLayout(layout4)

        # self.textBrowser = QTextBrowser()
        # main_layout.addWidget(self.textBrowser)
        self.rm = rm
        self.powersupply = powersupply

        self.setLayout(main_layout)

    def channelselct(self):
        if self.lineinser1.currentText() == 'Channel 1':
            self.button_clicked.emit("Channel 1 has been selected")
            self.powersupply.write('INSTrument CH1')
        elif self.lineinser1.currentText() == 'Channel 2':
            self.button_clicked.emit("Channel 2 has been selected")
            self.powersupply.write('INSTrument CH3')
        elif self.lineinser1.currentText() == 'Channel 3':
            self.button_clicked.emit("Channel 3 has been selected")
            self.powersupply.write('INSTrument CH3')
        else:
            self.button_clicked.emit("Please select a channel to proceed")

    def on_button_clicked(self):
        self.button_clicked.emit("Button clicked")

    def calcR709(self):
        voltage = float(self.multimeter.query('MEAS:VOLT:DC?'))
        self.lineinser1.setText(str(voltage))
    def get_lineinser1_value(self):
        return self.lineinser1.text()
    
    
# if __name__ == '__main__':
#     app = QApplication([])
#     window = PowerPopUp()
#     window.show()
#     app.exec()






    # channel select ..... 'INSTrument CH1' or 'INSTrument CH2'
    # command to get which info that which channel we selected 'INSTrument?'
    # command to measure the current 'MEASure:CURRent? [{CH1|CH2}]'
    # command to measure the voltage 't MEASure:VOLTage? [{CH1|CH2}]'
    # example command to set the current value 'CH1:CURRent 0.5' --> example ### [{CH1|CH2}:]CURRent <current>

    # command to conform the current value '[{CH1|CH2}:]CURRent?'  example 'CH1:CURRent?'

    # OUTPut {CH1|CH2|CH3},{ON|OFF} example::: OUTPut CH1,ON
    