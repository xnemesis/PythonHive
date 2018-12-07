from PyQt5 import QtCore, QtWidgets
from hiveFrame import windowFrame
from pprint import pprint

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    f = windowFrame()
    f.setFixedSize(600, 500)
    f.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    f.show()
    
    #gauge = dial(1.0)
    #gauge.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
    #gauge.show()
	
    app.exec_()