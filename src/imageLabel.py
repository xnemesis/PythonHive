from PyQt5 import QtWidgets, QtCore
from hiveDeviceController import hive

class imageLabel(QtWidgets.QLabel):
    def __init__(self, light, hiveLight, ellipse, direction, *args, **kwargs):
        super(imageLabel, self).__init__(*args, **kwargs)
        self._light = light
        self._hiveLight = hiveLight
        self._ellipse = ellipse
        self._direction = direction

    def mousePressEvent(self, event):
        if (self._hiveLight.isLightOn(self._light)):
            if (self._direction):
                ret = self._hiveLight.increaseBrightness(self._light, 10)
                self._ellipse.setPercentage(ret)
            else:
                ret = self._hiveLight.decreaseBrightness(self._light, 10)
                self._ellipse.setPercentage(ret)
        
        super(QtWidgets.QLabel, self).mouseReleaseEvent(event)