import sys
# Поделючение GUI интерфейса
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Winform(QWidget):
    def __init__(self, parent=None):
        super(Winform, self).__init__(parent)

        # Настройки окна главной формы
        self.ui = uic.loadUi('GUI_draw.ui')  # GUI, должен быть в папке с main.py
        self.ui.setWindowTitle('Автоматически балансирующий '
                               'стол 181-311')  # Название главного окна
        self.ui.setWindowIcon(QIcon('surflay.ico'))  # Иконка на гланое окно

        self.pix = QPixmap()        # создать экземпляр объекта QPixmap
        self.lastPoint = QPoint()   # начальная точка
        self.endPoint = QPoint()    # конечная точка

        self.ui.show()              # Открываем окно формы

        # Создание изображение с фоном цвета Gainsboro
        grey = QPixmap(self.ui.Bitmap.size())  # Создание фонового изображения для битмапа
        grey.fill(QColor('Gainsboro'))  # Заливаем это изображение цветом Gainsboro
        self.ui.Bitmap.setPixmap(grey)  # Вывести изображение на BitMap на форме

        self._image = QtGui.QPixmap("image_table.jpg")
        frameScaled = self._image.scaled(self.ui.Bitmap.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.Bitmap.setPixmap(frameScaled)  # Вывести изображение на BitMap на форме
        self.ui.Bitmap.setAlignment(Qt.AlignCenter)

        self.pix = grey

    # Перекрашенная функция репликации в основном нарисована здесь
    def paintEvent(self, event):
        pp = QPainter(self.pix)
        # Нарисуйте прямую линию в соответствии с двумя положениями до и после указателя мыши
        pp.drawLine(self.lastPoint, self.endPoint)
        # Сделать предыдущее значение координаты равным следующему значению координаты,
        # Таким образом можно нарисовать непрерывную линию
        self.lastPoint = self.endPoint
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pix)  # Рисуем на холсте

        point_x = QPoint(self.endPoint).x()
        point_y = QPoint(self.endPoint).y()
        self.ui.labelSystemMassage.setText('Статус: Координаты(' + str(point_x) + ';' + str(point_y) + ')')

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Winform()
    sys.exit(app.exec_())