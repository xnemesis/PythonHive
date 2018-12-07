from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class pathSlider(QtWidgets.QAbstractSlider):
    def __init__(self, path=QtGui.QPainterPath(), *args, **kwargs):
        super(pathSlider, self).__init__(*args, **kwargs)
        self._path = path
        self.stroke_path = self._path
        self.scale_path = self._path
        self.setPath()
        self.setAttribute(Qt.WA_NoSystemBackground)

    def setPath(self, path = None):
        if (path is None):
            self._path = QtGui.QPainterPath()
            c1 = QtCore.QPointF(5, -15)
            c2 = QtCore.QPointF(220, -15)
            self._path = QtGui.QPainterPath(QtCore.QPointF(5, 100))
            self._path.cubicTo(c1, c2, QtCore.QPointF(235, 100))
        else:
            self._path = path
            
        self.update()

    def path(self):
        return self._path

    path = QtCore.pyqtProperty(QtGui.QPainterPath, fget=path, fset=setPath)

    def paintEvent(self, event):
        border = 10
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        sx = (self.rect().width() -2*border) / self.path.boundingRect().width()
        sy = (self.rect().height() -2*border) /self.path.boundingRect().height()
        tr = QtGui.QTransform()
        tr.translate(border, border)
        tr.scale(sx, sy)
        self.scale_path = tr.map(self.path)
        stroker = QtGui.QPainterPathStroker()
        stroker.setCapStyle(QtCore.Qt.RoundCap)
        stroker.setWidth(10)
        stroke_path = stroker.createStroke(self.scale_path).simplified()
        painter.setPen(QtGui.QPen(self.palette().color(QtGui.QPalette.Shadow), 1))
        painter.setBrush(QtGui.QBrush(self.palette().color(QtGui.QPalette.Midlight)))
        painter.drawPath(stroke_path)
        stroker.setWidth(20)
        self.stroke_path = stroker.createStroke(self.scale_path).simplified()
        percentage = (self.value() - self.minimum())/(self.maximum() - self.minimum())
        highlight_path = QtGui.QPainterPath()
        highlight_path.moveTo(self.scale_path.pointAtPercent(0))
        n_p = int((self.maximum() + 1 - self.minimum())/self.singleStep())
        for i in range(n_p+1):
            d = i*percentage/n_p
            p = self.scale_path.pointAtPercent(d)
            highlight_path.lineTo(p)
        stroker.setWidth(8)
        new_phighlight_path = stroker.createStroke(highlight_path).simplified()

        activeHighlight = self.palette().color(QtGui.QPalette.Highlight)
        painter.setPen(activeHighlight)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(activeHighlight)))
        painter.drawPath(new_phighlight_path)

        opt  = QtWidgets.QStyleOptionSlider()
        r = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt, 
                                        QtWidgets.QStyle.SC_SliderHandle, self)
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

    def minimumSizeHint(self):
        return QtCore.QSize(5,5)#15§, 15)

    def sizeHint(self):
        return QtCore.QSize(95, 50)

    def mousePressEvent(self, event):
        self.update_pos(event.pos())
        super(pathSlider, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.update_pos(event.pos())
        super(pathSlider, self).mouseMoveEvent(event)

    def update_pos(self, point):
        if self.stroke_path.contains(point):
            n_p = int((self.maximum() + 1 - self.minimum())/self.singleStep())
            ls = []
            for i in range(n_p):
                p = self.scale_path.pointAtPercent(i*1.0/n_p)
                ls.append(QtCore.QLineF(point, p).length())
            j = ls.index(min(ls))
            val = int(j*(self.maximum() + 1 - self.minimum())/n_p)
            self.setValue(val)