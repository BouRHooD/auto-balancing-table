import sys
# Поделючение GUI интерфейса
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class FormWidget(QWidget):
    def __init__(self, parent=None):
        super(FormWidget, self).__init__(parent)
        self.pix = QPixmap()  # создать экземпляр объекта QPixmap
        self.lastPoint = QPoint()  # начальная точка
        self.endPoint = QPoint()  # конечная точка

        self.initUi()


    def initUi(self):
        # Размер окна установлен 900 * 520
        self.resize(900, 520)
        # Размер холста 640 * 480, фон белый
        self.pix = QPixmap(640, 480)
        self.pix.fill(Qt.white)
        self._image = QtGui.QPixmap("image_table.jpg")
        frameScaled = self._image.scaled(self.pix.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pix = frameScaled


    # Перекрашенная функция репликации в основном нарисована здесь
    def paintEvent(self, event):
        pp = QPainter(self.pix)
        # Нарисуйте прямую линию в соответствии с двумя положениями до и после указателя мыши
        if self.lastPoint.x() != 0 and self.lastPoint.y() != 0 and self.endPoint.x() != 0 and self.endPoint.y() != 0:
            pen = QPen(Qt.red)
            pen.setWidth(10)
            pp.setPen(pen)
            pp.drawEllipse(42,42,400,400)
            pp.drawPoint(242,242)
            import math
            n = 1
            r = 158
            x_center = 242
            y_center = 242
            for i in range(1, n + 1):
                x = self.endPoint.x()
                y = self.endPoint.y()
                if x >= x_center and y >= y_center:
                    if math.sqrt(x - x_center) + math.sqrt(y - y_center) <= math.sqrt(r):
                        pen = QPen(Qt.black)
                        pen.setWidth(10)
                        pp.setPen(pen)
                        pp.drawLine(self.lastPoint, self.endPoint)
                        print('Эта точка внутри окружности')
                    else:
                        pen = QPen(Qt.black)
                        pen.setWidth(10)
                        pp.setPen(pen)
                        pp.drawLine(self.lastPoint, self.endPoint)
                        print('Эта точка не внутри окружности')
                else:
                    pen = QPen(Qt.black)
                    pen.setWidth(10)
                    pp.setPen(pen)
                    pp.drawLine(self.lastPoint, self.endPoint)
        # Сделать предыдущее значение координаты равным следующему значению координаты,
        # Таким образом можно нарисовать непрерывную линию
        self.lastPoint = self.endPoint
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pix)  # Рисуем на холсте


    # Мышь пресс-мероприятие
    def mousePressEvent(self, event):
        # Нажмите левую кнопку мыши
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.endPoint = self.lastPoint


    # Событие движения мыши
    def mouseMoveEvent(self, event):
        # Перемещайте мышь, удерживая нажатой левую кнопку мыши
        if event.buttons() and Qt.LeftButton:
            self.endPoint = event.pos()
            # Сделать перекраску
            self.update()


    # Событие отпускания мыши
    def mouseReleaseEvent(self, event):
        # Отпустить левую кнопку мыши
        if event.button() == Qt.LeftButton:
            self.endPoint = event.pos()
            # Сделать перекраску
            self.update()

    def clear_painter(self):
        self.pix = QPixmap()  # создать экземпляр объекта QPixmap
        self.pix = QPixmap(640, 480)
        self._image = QtGui.QPixmap("image_table.jpg")
        frameScaled = self._image.scaled(self.pix.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pix = frameScaled
        self.update()

class Dialog_01(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Рисовальщик пути 181-311"
        self.setWindowIcon(QIcon('surflay.ico'))     # Иконка на гланое окно
        self.top, self.left, self.width, self.height = 0, 0, 900, 520
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.flayout = QFormLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.form_widget = FormWidget(self)
        self.form_widget.setGeometry(10, 10, 640, 480)

        self.form_button_clear = QPushButton('Очистить поле', self)
        self.form_button_clear.setGeometry(640 + 5, 10, 100, 50)

        # Выполнить функцию browse_folder при нажатии кнопки
        self.form_button_clear.clicked.connect(self.form_widget.clear_painter)


if __name__ == '__main__':
    App = QApplication.instance()
    if App is None:
        App = QApplication(sys.argv)
    ui = Dialog_01()
    ui.show()
    sys.exit(App.exec_())