from PyQt5 import QtCore, QtWidgets
from hiveFrame import windowFrame

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    f = windowFrame()
    f.setFixedSize(600, 500)
    f.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    f.show()
	
    app.exec_()