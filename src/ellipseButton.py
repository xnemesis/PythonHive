import weakref
from PyQt5 import QtCore, QtGui, QtWidgets
from hiveDeviceController import hive

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

class ellipseButton(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, light, hiveLight, parent = None, *args, **kwargs):
        super(ellipseButton, self).__init__(*args, **kwargs)
        self._fill_brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        self._percentage = 0
        self._light = light
        self._hiveLight = hiveLight
        
        if (parent is None):
            self._parent = None
        else:
            self._parent = parent
    
    def setFillBrush(self, brush):
        self._fill_brush = brush
        self.update()

    def fillBrush(self):
        return self._fill_brush

    def setPercentage(self, percentage):
        self._percentage /= 100
        self.update()

    def percentage(self):
        return self._percentage
    
    def update(self):
        color = QtGui.QColor(QtCore.Qt.lightGray).darker(150)
        brush = QtGui.QBrush(color)
        self.setBrush(brush)
        self._percentage = 0
        
        ret = self._hiveLight.isLightOn(self._light)
        if (ret == True):
            self._percentage = \
                             (self._hiveLight.getBrightness(self._light) / 100)
            self._fill_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.lightGray))
            super(ellipseButton, self).update()
        else:
            super(ellipseButton, self).update()

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        r_in = QtCore.QRectF(QtCore.QPointF(), self.rect().size())
        r_out = QtCore.QRectF(r_in)
        r_out.setTop((1 - self.percentage()) * r_in.height())

        p1 = QtGui.QPixmap(r_in.size().toSize())
        p1.fill(QtCore.Qt.transparent)
        p_1 = QtGui.QPainter(p1)
        p_1.setRenderHints(painter.renderHints())
        p_1.fillRect(r_out, self.fillBrush())
        p_1.end()

        p2 = QtGui.QPixmap(r_in.size().toSize())
        p2.fill(QtCore.Qt.transparent)
        p_2 = QtGui.QPainter(p2)
        p_2.setRenderHints(painter.renderHints())
        p_2.setPen(painter.pen())
        p_2.setBrush(self.brush())
        p_2.drawEllipse(r_in)
        p_2.end()

        pixmap = QtGui.QPixmap(r_in.size().toSize())
        pixmap.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(pixmap)
        p.setRenderHints(painter.renderHints())
        p.drawPixmap(QtCore.QPointF(), p1)
        p.setCompositionMode(QtGui.QPainter.CompositionMode_DestinationAtop)
        p.drawPixmap(QtCore.QPointF(), p2)
        p.end()

        painter.drawPixmap(option.rect.topLeft(), pixmap)
        painter.setPen(self.pen())
        painter.drawEllipse(option.rect)

    def mouseReleaseEvent(self, event):
        color = QtGui.QColor(QtCore.Qt.lightGray)
        
        if self._light is None:
            print("toggling all")
            self._hiveLight.toggleAllLights(0)
            color = QtGui.QColor(QtCore.Qt.lightGray)
        elif self._light == "-1":
            print("calling update")
            self._parent.refreshButtons()
        else:
            ret = self._hiveLight.toggleDevice(self._light)

            color = QtGui.QColor(QtCore.Qt.lightGray).darker(150)
            brush = QtGui.QBrush(color)
            self.setBrush(brush)

            if (ret):
                self.setPercentage(self._hiveLight.getBrightness(self._light))
                self.setFillBrush(brush)
            else:
                self.setPercentage(0)
        
        if (self._parent is not None):
            self._parent.refreshButtons()
    
        super(ellipseButton, self).mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        # Do your stuff here.
        pass

    def hoverEnterEvent(self, event):
        #color = QtGui.QColor(0, 174, 185)
        #color = QtGui.QColor(QtCore.Qt.lightGray).lighter(125)
        #brush = QtGui.QBrush(color)
        #QtWidgets.QGraphicsEllipseItem.setBrush(self, brush)
        pass

    def hoverLeaveEvent(self, event):
        #color = QtGui.QColor(QtCore.Qt.lightGray)
        #brush = QtGui.QBrush(color)
        #QtWidgets.QGraphicsEllipseItem.setBrush(self, brush)
        pass
        
