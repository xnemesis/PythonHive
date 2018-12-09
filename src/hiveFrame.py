import sys, math, itertools
from PyQt5 import QtGui, QtCore, QtWidgets
from imageLabel import imageLabel
from ellipseButton import ellipseButton
from hiveDeviceController import hive
from error import hiveError
from pprint import pprint
from slider import pathSlider

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

class windowFrame(QtWidgets.QGraphicsView):
    def __init__(self, parent = None, *args, **kwargs):
        try:
            super(windowFrame, self).__init__(parent)

            self.setScene(QtWidgets.QGraphicsScene(self))
            self.setBackgroundBrush(QtGui.QColor(QtCore.Qt.darkGray))
            self.setRenderHints(self.renderHints() | \
                                QtGui.QPainter.Antialiasing  | \
                                QtGui.QPainter.SmoothPixmapTransform)
            hiveLight = hive()
            arrDevices = hiveLight.getDevices()
        
            theta = math.radians(360)
            lColumns = (len([dev for id, dev in arrDevices.items() if dev['type'] == 'light']))
            gColumns = (len([dev for id, dev in arrDevices.items() if dev['type'] == 'group']))
            lDelta, gDelta = theta/lColumns, theta/gColumns
            w, h, lx, ly, li, gx, gy, gi = 100, 100, 100, 100, 0, 0, 0, 0
            circX, circY = 0, 0

            pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.lightGray).darker(50))
            for id, device in arrDevices.items():
                lAngle = li * lDelta
                gAngle = gi * gDelta
            
                if (device['type'] == 'light'):
                    circX = (w + lx) * math.cos(lAngle)
                    circY = (h + ly) * math.sin(lAngle)
                    li += 1
                elif (device['type'] == 'group'):
                    circX = (w + gx) * math.cos(gAngle)
                    circY = (h + gy) * math.sin(gAngle)
                    gi += 1
            
                item = ellipseButton(id, hiveLight, None, circX, circY, w, h)
                item.setAcceptHoverEvents(True)
                item.setPen(pen)
            
                brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.lightGray).darker(150))
                
                item.setBrush(brush)
                if ("status" in device and device['status']):
                    item.setPercentage(hiveLight.getBrightness(id))
                    item.setFillBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.lightGray)))
                
                item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
                self.scene().addItem(item)
                self.createBrightnessBtns(id, hiveLight, item, circX + (w / 2), circY + (h / 2))
                self.writeText(device['name'], circX , circY, w, h)
            
                if ("colourTemp" in device):
                    c1 = QtCore.QPointF(5, 15) 
                    c2 = QtCore.QPointF(220, 15) 
                    path = QtGui.QPainterPath(QtCore.QPointF(5, -100)) 
                    path.cubicTo(c1, c2, QtCore.QPointF(235, -100))
                    sslider = pathSlider(id, hiveLight, True, path, \
                                         minimum=0, maximum=383)
                    sslider.move(circX + 5, circY + (h // 2))
                    self.scene().addWidget(sslider)
                
            circX, circY = 0, 0
            item = ellipseButton(None, hiveLight, None, circX, circY, w, h)
            item.setPen(pen)
            item.setBrush(brush)
            item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
            self.scene().addItem(item)
            self.writeText("Turn Off All", circX, circY, w, h)
    
            circX, circY = 0 + (self.width() / 2), 0 - (self.width() / 4)
            w /= 2
            h /= 2
            item = ellipseButton("-1", hiveLight, self, circX, circY, w, h)
            item.setAcceptHoverEvents(True)
            item.setPen(pen)
            item.setBrush(brush)
            item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
            self.scene().addItem(item)
            self.writeText("Refresh", circX, circY, w, h)

        except ZeroDivisionError:
            sys.exit("Unable to connect to the server")
        except:
            print("Unexpected exception in windowFrame.__init__():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    def writeText(self, text, x, y, maxX, maxY):
        font = QtGui.QFont('White Rabbit')
        font.setPointSize(12)
        self.dot1=QtWidgets.QGraphicsTextItem(text)
        self.dot1.setFont(font)
        x += (maxX / 2) - (self.dot1.boundingRect().width() / 2)
        y += (maxY / 2) - (self.dot1.boundingRect().height() / 2)
        self.dot1.setPos(x, y)
        self.scene().addItem(self.dot1)
    
    def createBrightnessBtns(self, id, hiveLight, item, lx, ly):
        label = imageLabel(id, hiveLight, item, True, self)
        pixmap = QtGui.QPixmap('icons/plus.png')
        label.setPixmap(pixmap)
        lx = lx - (label.width() / 2) + 250
        ly = ly - (label.height() / 2) + 170
        label.move(lx, ly)
        
        label = imageLabel(id, hiveLight, item, False, self)
        pixmap = QtGui.QPixmap('icons/minus.png')
        label.setPixmap(pixmap)
        ly += 60
        label.move(lx, ly)
        
    def refreshButtons(self):
        [item.update() for item in self.items() if isinstance(item, ellipseButton)]