import sys
# Поделючение GUI интерфейса
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

global main_img
class Winform(QMainWindow):
    def __init__(self, parent=None):
        global main_img
        super(Winform, self).__init__(parent)
        # Настройки окна главной формы
        self.ui = uic.loadUi('GUI_draw.ui')             # GUI, должен быть в папке с main.py
        self.ui.setWindowTitle('Автоматически балансирующий '
                               'стол 181-311')          # Название главного окна
        self.ui.setWindowIcon(QIcon('surflay.ico'))     # Иконка на гланое окно

        self.displayWidth = 640                         # Ширина BitMap на форме
        self.displayHeight = 480                        # Высота BitMap на форме

        self.ui.show()                                  # Открываем окно формы

        # Создание изображение с фоном цвета Gainsboro
        grey = QPixmap(self.displayWidth,
                       self.displayHeight)              # Создание фонового изображения для битмапа
        grey.fill(QColor('Gainsboro'))                  # Заливаем это изображение цветом Gainsboro
        self.ui.Bitmap.setPixmap(grey)                  # Вывести изображение на BitMap на форме

        self._image = QtGui.QPixmap("image_table.jpg")
        frameScaled = self._image.scaled(self.ui.Bitmap.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.Bitmap.setPixmap(frameScaled)           # Вывести изображение на BitMap на форме
        self.ui.Bitmap.setAlignment(Qt.AlignCenter)

        main_img = frameScaled
        hover_tracker = HoverTracker(self.ui.Bitmap)

        # Подписки на события ui
        hover_tracker.positionChanged.connect(self.on_position_changed)

    @pyqtSlot(QPoint)
    def on_position_changed(self, p):
        point_x = QPoint(p).x()
        point_y = QPoint(p).y()
        self.ui.labelSystemMassage.setText('Статус: Координаты(' + str(point_x) + ';' + str(point_y) + ')')


class HoverTracker(QObject):
    positionChanged = pyqtSignal(QPoint)

    def __init__(self, widget):
        super().__init__(widget)

        global main_img

        self.lastPoint = QPoint()                       # начальная точка
        self.endPoint = QPoint()                        # конечная точка

        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QEvent.MouseMove:
            self.positionChanged.emit(event.pos())

            self.pix = main_img  # создать экземпляр объекта QPixmap
            pp = QPainter(self.pix)
            # Нарисуйте прямую линию в соответствии с двумя положениями до и после указателя мыши
            pp.drawLine(self.lastPoint, self.endPoint)
            # Сделать предыдущее значение координаты равным следующему значению координаты,
            # Таким образом можно нарисовать непрерывную линию
            self.lastPoint = self.endPoint
            self._widget.setPixmap(self.pix)  # Вывод обработанного изображения на форму

        if obj is self.widget and event.type() == QEvent.MouseButtonPress:
            # Нажмите левую кнопку мыши
            if event.button() == Qt.LeftButton:
                self.lastPoint = event.pos()
                self.endPoint = self.lastPoint

        if obj is self.widget and event.type() == QEvent.MouseButtonRelease:
            # Отпустить левую кнопку мыши
            if event.button() == Qt.LeftButton:
                self.endPoint = event.pos()

        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Winform()
    sys.exit(app.exec_())