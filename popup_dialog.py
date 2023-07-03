from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#from test_script import App

class MyDialog(QDialog):
    button_clicked = pyqtSignal(str)
    def __init__(self, rm, multimeter, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dialog")
        main_layout = QVBoxLayout()
        
        layout1 = QHBoxLayout()
        self.label1 = QPushButton('R709')
        self.label2 = QPushButton('R700')
        self.label3 = QPushButton('C443')
        self.label4 = QPushButton('C442')


        self.lineinser1 = QLineEdit()
        self.lineinser2 = QLineEdit()
        self.lineinser3 = QLineEdit()
        self.lineinser4 = QLineEdit()
        
        layout1.addWidget(self.label1)
        layout1.addWidget(self.lineinser1)

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

        self.setLayout(main_layout)

        self.rm = rm
        self.multimeter = multimeter
        self.label1.clicked.connect(self.calcR709)


    def on_button_clicked(self):
        self.button_clicked.emit("Button clicked")

    def calcR709(self):
        voltage = float(self.multimeter.query('MEAS:VOLT:DC?'))
        self.lineinser1.setText(str(voltage))
    def get_lineinser1_value(self):
        return self.lineinser1.text()