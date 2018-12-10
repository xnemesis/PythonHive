import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from pprint import pprint

class pathSlider(QtWidgets.QAbstractSlider):
    def __init__(self, light, hiveLight, inverse=False, \
                 path=QtGui.QPainterPath(), *args, **kwargs):
        try:
            super(pathSlider, self).__init__(*args, **kwargs)
            self._light = light
            self._hiveLight = hiveLight
            self._path = path
            self.stroke_path = self._path
            self.scale_path = self._path
            self._inverse = inverse
            self.setPath(self._path)
            self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
            if (self._inverse):
                val = (self._hiveLight.getColourTemperature(self._light) / 10) \
                       - 270
            else:
                val = self._hiveLight.getBrightness(self._light)
            self.setValue(val)
        except:
            print("Unexpected exception in pathSlider.__init__():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    def setPath(self, path = None):
        try:
            if (path is None):
                self._path = QtGui.QPainterPath()                                
                self._path.translate(-self._path.boundingRect().topLeft())
                if (self._inverse):
                    c1 = QtCore.QPointF(5, 15) 
                    c2 = QtCore.QPointF(220, 15) 
                    self._path = QtGui.QPainterPath(QtCore.QPointF(5, -100)) 
                    self._path.cubicTo(c1, c2, QtCore.QPointF(235, -100))
                else:
                    c1 = QtCore.QPointF(5, -15)
                    c2 = QtCore.QPointF(220, -15)
                    self._path = QtGui.QPainterPath(QtCore.QPointF(5, 100))
                    self._path.cubicTo(c1, c2, QtCore.QPointF(235, 100))
            else:
                path.translate(-path.boundingRect().topLeft())
                self._path = path
            self.update()
        except:
            print("Unexpected exception in pathSlider.setPath():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    def path(self):
        return self._path

    path = QtCore.pyqtProperty(QtGui.QPainterPath, fget=path, fset=setPath)

    def paintEvent(self, event):
        try:
            border = 10
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            sx=(self.rect().width()-2*border)/self.path.boundingRect().width()
            sy=(self.rect().height()-2*border)/self.path.boundingRect().height()
            
            tr = QtGui.QTransform()
            tr.translate(border, border)
            tr.scale(sx, sy)
            self.scale_path = tr.map(self.path)
            
            stroker = QtGui.QPainterPathStroker()
            stroker.setCapStyle(QtCore.Qt.RoundCap)
            stroker.setWidth(8)
            stroke_path = stroker.createStroke(self.scale_path).simplified()
            
            pen = QtGui.QPen(self.palette().color(QtGui.QPalette.Shadow), 1)
            painter.setPen(pen)
            
            brush = QtGui.QBrush(self.palette().color(QtGui.QPalette.Midlight))
            painter.setBrush(brush)
            
            painter.drawPath(stroke_path)
            stroker.setWidth(10)
            self.stroke_path = \
                stroker.createStroke(self.scale_path).simplified()
                
            percentage = (self.value() - self.minimum()) / \
                         (self.maximum() - self.minimum())
            highlight_path = QtGui.QPainterPath()
            highlight_path.moveTo(self.scale_path.pointAtPercent(0))
            n_p = int((self.maximum() + 1 - self.minimum())/self.singleStep())
            for i in range(n_p+1):
                d = i*percentage/n_p
                p = self.scale_path.pointAtPercent(d)
                highlight_path.lineTo(p)
            stroker.setWidth(8)
            new_phighlight_path = \
                stroker.createStroke(highlight_path).simplified()

            activeHighlight = self.palette().color(QtGui.QPalette.Highlight)
            painter.setPen(activeHighlight)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(activeHighlight)))
            painter.drawPath(new_phighlight_path)

            opt = QtWidgets.QStyleOptionSlider()
            r = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt, \
                                            QtWidgets.QStyle.SC_SliderHandle, \
                                            self)
            pixmap = QtGui.QPixmap(r.width() + 2*2, r.height() + 2*2)
            pixmap.fill(QtCore.Qt.transparent)
            r = pixmap.rect().adjusted(2, 2, -2, -2)
            pixmap_painter = QtGui.QPainter(pixmap)
            pixmap_painter.setRenderHint(QtGui.QPainter.Antialiasing)
            pixmap_painter.setPen(QtGui.QPen(self.palette().color(QtGui.QPalette.Shadow), 2))
            pixmap_painter.setBrush(self.palette().color(QtGui.QPalette.Base))
            pixmap_painter.drawRoundedRect(r, 4, 4)
            pixmap_painter.end()
            r.moveCenter(p.toPoint())
            painter.drawPixmap(r, pixmap)
        except:
            print("Unexpected exception in pathSlider.paintEvent():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    def minimumSizeHint(self):
        return QtCore.QSize(5,5)

    def sizeHint(self):
        return QtCore.QSize(95, 50)

    def mouseReleaseEvent(self, event):
        if (self._hiveLight.isLightOn(self._light)):
            self.update_pos(event.pos())
            if (self._inverse):
                cTemp = (self.value() + 270) * 10
                self._hiveLight.setColourTemperature(self._light, cTemp)
            else:
                self._hiveLight._setBrightness(self._light, self.value())

    def mousePressEvent(self, event):
        if (self._hiveLight.isLightOn(self._light)):
            self.update_pos(event.pos())

    def mouseMoveEvent(self, event):
        if (self._hiveLight.isLightOn(self._light)):
            self.update_pos(event.pos())
            super(pathSlider, self).mouseMoveEvent(event)

    def update_pos(self, point):
        try:
            if self.stroke_path.contains(point):
                n_p = int(
                            (self.maximum() + 1 - self.minimum()) / \
                            self.singleStep()
                          )
                ls = []
                for i in range(n_p):
                    p = self.scale_path.pointAtPercent(i*1.0/n_p)
                    ls.append(QtCore.QLineF(point, p).length())
                j = ls.index(min(ls))
                val = int(j*(self.maximum() + 1 - self.minimum())/n_p)
                self.setValue(val)
        except:
            print("Unexpected exception in pathSlider.update_pos():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))