import sys
# Поделючение GUI интерфейса
from threading import Thread

import cv2
import numpy as np
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# OpenCV setup
HSV_TABLE_MASK_LOWER = (50, 40, 0)
HSV_TABLE_MASK_UPPER = (80, 255, 255)
HSV_BALL_MASK_1_LOWER = (160, 70, 60)
HSV_BALL_MASK_1_UPPER = (180, 255, 255)
HSV_BALL_MASK_2_LOWER = (0, 70, 60)
HSV_BALL_MASK_2_UPPER = (10, 255, 255)
FONT = cv2.FONT_HERSHEY_PLAIN

MORPH_ON = 1
HOUGH_ON = 1
SERVO_ON = 1
BLUR_ON = 1
SHOW_MAIN = 1
SHOW_THRESH = 1
FLIP = 0

COLOR_RANGE={
 'ball_light': (np.array((20, 70, 170), np.uint8), np.array((40, 170, 255), np.uint8)),
 'ball_dark': (np.array((0, 170, 120), np.uint8), np.array((20, 240, 255), np.uint8)),
}

class FormWidget(QWidget):
    def __init__(self, parent=None):
        super(FormWidget, self).__init__(parent)
        self.pix = QPixmap()  # создать экземпляр объекта QPixmap
        self.lastPoint = QPoint()  # начальная точка
        self.endPoint = QPoint()  # конечная точка

        self.flagDraw = False
        self._image_def = QtGui.QPixmap("image_table.jpg")
        self.lastPoint_list = []
        self.endPoint_list = []
        self.initUi()

    def initUi(self):
        # Размер окна установлен 900 * 520
        self.resize(900, 520)
        # Размер холста 640 * 480, фон белый
        self.pix = QPixmap(480, 480)
        self.pix.fill(Qt.white)
        self._image = QtGui.QPixmap("image_table.jpg")
        frameScaled = self._image.scaled(self.pix.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pix = frameScaled


    def setImageFromCamera(self, inImg):
        self.pix = inImg
        self.update()

    def saveCurrentImage(self, numberImage):
        if self.pix is not None:
            cv2.imwrite('SavedImages/Image' + str(numberImage) + '.png', self.pix)
            self.StatusLabel.setText('Статус: сохранено Image' + str(self.numberImage))

    def setFlagDraw(self, inBool):
        self.flagDraw = inBool

    # Перекрашенная функция репликации в основном нарисована здесь
    def paintEvent(self, event):
        if self.flagDraw is False:
            # Выводим видео с камеры
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.pix)  # Рисуем на холсте
            return

        pp = QPainter(self.pix)
        # Нарисуйте прямую линию в соответствии с двумя положениями до и после указателя мыши
        if self.lastPoint.x() != 0 and self.lastPoint.y() != 0 and self.endPoint.x() != 0 and self.endPoint.y() != 0:
            pen = QPen(Qt.red)
            pen.setWidth(10)
            pp.setPen(pen)
            pp.drawEllipse(42, 42, 400, 400)
            pp.drawPoint(242, 242)

            r_circle = 195
            x_center = 242
            y_center = 242
            x = self.endPoint.x()
            y = self.endPoint.y()

            if len(self.lastPoint_list) >= 2000:
                self.lastPoint_list = []
                self.endPoint_list = []

            if self.func_point_in_circle(x, y, x_center, y_center, r_circle):
                self.lastPoint = self.endPoint
                self.lastPoint_list.append(self.lastPoint)
                self.endPoint_list.append(self.endPoint)
            else:
                import math
                full_len = math.sqrt(math.pow(x - x_center, 2) + math.pow(y - y_center, 2))
                point = QPoint(x_center, y_center)
                newPoint = point + (self.endPoint - point) * (r_circle / full_len)
                self.lastPoint_list.append(newPoint)
                self.endPoint_list.append(newPoint)

            for index_points in range(len(self.lastPoint_list)):
                pen = QPen(Qt.black)
                pen.setWidth(10)
                pp.setPen(pen)
                pp.drawLine(self.lastPoint_list[index_points], self.endPoint_list[index_points])

        # Сделать предыдущее значение координаты равным следующему значению координаты,
        # Таким образом можно нарисовать непрерывную линию
        # self.lastPoint = self.endPoint
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pix)  # Рисуем на холсте

    def func_point_in_circle(self, x, y, x_center, y_center, r_circle):
        return (x - x_center) * (x - x_center) + (y - y_center) * (y - y_center) <= r_circle * r_circle

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
        self._image = self._image_def
        frameScaled = self._image.scaled(self.pix.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pix = frameScaled
        self.lastPoint_list = []
        self.endPoint_list = []
        self.update()


class Dialog_01(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Автоматически балансирующий стол 181-311'                      # Название главного окна
        self.setWindowIcon(QIcon('surflay.ico'))     # Иконка на гланое окно
        self.top, self.left, self.width, self.height = 0, 0, 800, 535
        self.initUI()

        # Флаги работы программы
        self.flagCameraWork = False  # Флаг работы камеры

        # Переменные для работы с камерой
        self.capture = None  # Захват изображение с камеры
        self.frameIn = None  # Входное (сырое) изображение с камеры
        self.frameOut = None  # Выходное (Обработанное) изображение с камеры

    def initUI(self):

        self.frameToSave = None  # Обработанное изображение для сохранения
        self.flagRecord = False
        self.numberImage = 0  # Переменная номера изображения

        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.lastx = 0
        self.lasty = 0
        self.time = 0

        self.color = 'ball_light'
        self.color2 = 'ball_dark'
        self.h_min = COLOR_RANGE[self.color][0]
        self.h_max = COLOR_RANGE[self.color][1]
        if self.color2:
            self.h_min_2 = COLOR_RANGE[self.color2][0]
            self.h_max_2 = COLOR_RANGE[self.color2][1]

        self.GroupBox_Cam = QGroupBox(self)
        self.GroupBox_Cam.setGeometry(5, 5, 480, 480)
        self.vbox = QVBoxLayout()
        self.GroupBox_Cam.setLayout(self.vbox)
        self.GroupBox_Cam.setAlignment(Qt.AlignCenter)
        self.form_widget = FormWidget(self)
        self.vbox.addWidget(self.form_widget)

        MIN_Button_Height = 30
        self.GroupBox_Button = QGroupBox(self)
        self.GroupBox_Button.setGeometry(490, 5, 300, 150)
        self.vbox = QVBoxLayout()
        self.GroupBox_Button.setLayout(self.vbox)
        self.cbModeSelect = QComboBox(self)
        self.cbModeSelect.addItem("Режим автоматического балансирования")
        self.cbModeSelect.addItem("Режим движения по траектории")
        self.cbModeSelect.setMinimumHeight(MIN_Button_Height)
        self.cbModeSelect.setStyleSheet(open('styles/styleQComboBox.css').read())
        self.bCameraWork = QPushButton('Включить видео с камеры', self)
        self.bCameraWork.setMinimumHeight(MIN_Button_Height)
        self.bCameraWork.setStyleSheet(open('styles/styleButtonStartStopVideo.css').read())
        self.bStartMission = QPushButton('Начать движение шарика', self)
        self.bStartMission.setMinimumHeight(MIN_Button_Height)
        self.bStartMission.setStyleSheet(open('styles/styleButtonStartStopVideo.css').read())
        self.bClearPointer = QPushButton('Очистить поле', self)
        self.bClearPointer.setMinimumHeight(MIN_Button_Height)
        self.bClearPointer.setStyleSheet(open('styles/styleButtonStartStopVideo.css').read())
        self.vbox.addWidget(self.cbModeSelect)
        self.vbox.addWidget(self.bCameraWork)
        self.vbox.addWidget(self.bStartMission)
        self.vbox.addWidget(self.bClearPointer)

        self.GroupBox_Video_Button = QGroupBox(self)
        self.GroupBox_Video_Button.setGeometry(490, 160, 300, 250)
        self.vbox_Video = QVBoxLayout()
        self.GroupBox_Video_Button.setLayout(self.vbox_Video)
        self.label_NamePanel = QLabel("Режим съёмки")
        self.label_NamePanel.setAlignment(Qt.AlignCenter)
        self.bVideo = QPushButton('Включить видеосъемку', self)
        self.bVideo.setStyleSheet(open('styles/styleButtonStartStopVideo.css').read())
        self.cbCount = QRadioButton("Задать количество кадров")
        self.cbStop = QRadioButton("До остановки сохранения")
        self.cbStop.click()
        self.label_NamespinBoxCount = QLabel("Количество кадров до остановки")
        self.label_NamespinBoxCount.setAlignment(Qt.AlignCenter)
        self.spinBoxCount = QSpinBox()
        self.spinBoxCount.setAlignment(Qt.AlignCenter)
        self.spinBoxCount.setMinimum(1)
        self.spinBoxCount.setMaximum(100000)
        self.label_NamespinBoxInterval = QLabel("Интервал съемки, мс")
        self.label_NamespinBoxInterval.setAlignment(Qt.AlignCenter)
        self.spinBoxInterval = QSpinBox()
        self.spinBoxInterval.setAlignment(Qt.AlignCenter)
        self.spinBoxInterval.setMinimum(100)
        self.spinBoxInterval.setMaximum(10000)
        self.bVideo.setMinimumHeight(MIN_Button_Height)
        self.vbox_Video.addWidget(self.label_NamePanel)
        self.vbox_Video.addWidget(self.bVideo)
        self.vbox_Video.addWidget(self.cbCount)
        self.vbox_Video.addWidget(self.cbStop)
        self.vbox_Video.addWidget(self.label_NamespinBoxCount)
        self.vbox_Video.addWidget(self.spinBoxCount)
        self.vbox_Video.addWidget(self.label_NamespinBoxInterval)
        self.vbox_Video.addWidget(self.spinBoxInterval)

        self.GroupBox_Status = QGroupBox(self)
        self.GroupBox_Status.setGeometry(5, 490, 480, 40)
        self.vbox_Status = QVBoxLayout()
        self.GroupBox_Status.setLayout(self.vbox_Status)
        self.StatusLabel = QLabel("Статус: ")
        self.StatusLabel.setAlignment(Qt.AlignTop)
        self.vbox_Status.addWidget(self.StatusLabel)

        self.StatusLabel.setText("Статус: активирован автоматический режим")

        select_item = self.cbModeSelect.currentIndex()
        if select_item == 0:
            self.bStartMission.setEnabled(False)
            self.form_widget.setFlagDraw(False)

        # Подписки на события
        # Включение камеры
        self.bCameraWork.clicked.connect(self.cameraWorkClicked)
        self.bVideo.clicked.connect(self.cameraRecord)
        # Очистить поле
        self.bClearPointer.clicked.connect(self.clearPainter)
        self.cbModeSelect.currentIndexChanged.connect(self.index_change)

    def cameraRecord(self):
        interval = self.spinBoxInterval.value() / 1000  # Интервал сохранения

        # Режим нажатия кнопки остановки
        if self.cbCount.isChecked():
            thread = Thread(target=self.recordThread1, args=(1, interval))

        # Режим заданного количества кадров
        elif self.cbStop.isChecked():
            if self.flagRecord:
                self.bVideo.setText('Включить видеосъёмку')
                self.flagRecord = False
            else:
                self.bVideo.setText('Отключить видеосъёмку ')
                self.flagRecord = True
            thread = Thread(target=self.recordThread2, args=(1, interval))

        thread.start()

    # Поток для съёмки в режиме заданного количества кадров
    def recordThread1(self, first_interval, interval):
        count = self.spinBoxCount.value()
        from time import sleep
        sleep(first_interval)

        for i in range(0, count):
            self.saveImageClicked()
            sleep(interval)

        self.StatusLabel.setText('Статус: запись завершена')

    # Поток для съёмки в режиме нажатия кнопки остановки
    def recordThread2(self, first_interval, interval):
        from time import sleep
        sleep(first_interval)

        while self.flagRecord:
            self.saveImageClicked()
            sleep(interval)

        self.StatusLabel.setText('Статус: запись завершена')

    # Клик по кнопке "Сохранить изображение"
    def saveImageClicked(self):
        if self.flagCameraWork:
            self.numberImage += 1
            self.form_widget.saveCurrentImage(self.numberImage)

    def index_change(self):
        select_item = self.cbModeSelect.currentIndex()
        if select_item == 1:
            self.StatusLabel.setText("Статус: активирован режим траектории")
            self.bStartMission.setEnabled(True)
            self.form_widget.setFlagDraw(True)
        else:
            self.StatusLabel.setText("Статус: активирован автоматический режим")
            self.bStartMission.setEnabled(False)
            self.form_widget.setFlagDraw(False)

        if select_item == 0:
            self.form_widget.clear_painter()

    def clearPainter(self):
        self.StatusLabel.setText("Статус: поле для рисования очищено")
        self.form_widget.clear_painter()

    # Нажатие на кнопку включения камеры
    def cameraWorkClicked(self):
        if self.flagCameraWork:
            self.flagCameraWork = False
            self.bCameraWork.setText('Включить видео с камеры')
            self.StatusLabel.setText("Статус: камера выключена")
            self.capture.release()
            self._image = QtGui.QPixmap("image_table.jpg")
            self.form_widget.setImageFromCamera(self._image)  # Вывод обработанного изображения на форму
            self.frameToSave = self._image  # Для сохранения изображения
            cv2.destroyAllWindows()
        else:
            self.flagCameraWork = True
            self.bCameraWork.setText('Выключить видео с камеры')
            self.StatusLabel.setText("Статус: камера включена")
            thread = Thread(target=self.ThreadCamera)
            thread.start()

    # Поток для камеры
    def ThreadCamera(self):
        if self.flagCameraWork:
            self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            while self.capture.isOpened():
                ret, self.frameIn = self.capture.read()
                if ret:
                    self.frameProcessing()  # Обработка изображения
                    self.form_widget.setImageFromCamera(self.frameOut)    # Вывод обработанного изображения на форму
                    # cv2.imshow('Camera', self.frameOut2)                # Вывод изображения с камеры
                    cv2.waitKey(10)

    def valmap(self, value, istart, istop, ostart, ostop):
        """
        Re-maps a number from one range to another (the same as in arduino)
        :return:
        """

        return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

    # Обработка сырого изображения с камеры
    def frameProcessing(self):
        frameProcess = self.frameIn  # Копируем входное изображение для его обработки

        par1 = 80  # 40
        par2 = 50  # 67
        h, w = frameProcess.shape[:2]
        import time
        dt = time.process_time() - self.time
        self.time = time.process_time()

        # Функция inRange преобразует цветную картинку в черно-белую маску. В этой маске, все пиксели, попадающие в заданный диапазон — становятся белыми. Прочие — черными.
        # В HSV проще создать правильную маску для выделения нужного цвета
        hsv = cv2.cvtColor(frameProcess, cv2.COLOR_BGR2HSV)
        thresh = cv2.inRange(hsv, self.h_min, self.h_max)
        thresh_2 = cv2.inRange(hsv, self.h_min_2, self.h_max_2)
        thresh = cv2.bitwise_or(thresh, thresh_2)

        if MORPH_ON:
            # Данная процедура нужна для того, чтобы убрать из кадра мелкий мусор и замазать возможные дефекты в выделяемом объекте.
            # Например, морфологическое преобразование позволяет убрать из теннисного шарика прожилку, которая имеет отличный цвет.
            st1 = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21), (10, 10))
            st2 = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11), (5, 5))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, st1)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, st2)

        if BLUR_ON:
            # Банальное размывание методом Гаусса. Как и предыдущая процедура, размывание необходимо для сглаживания шероховатостей
            thresh = cv2.GaussianBlur(thresh, (5, 5), 2)

        circles = None
        if HOUGH_ON:
            # Процедура HoughCircles находит на изображении все окружности, используя при этом преобразование Хофа
            import numpy as np
            circles = cv2.HoughCircles(thresh,
                                       cv2.HOUGH_GRADIENT, 2, h / 4,
                                       np.array([]),
                                       par1, par2, 5, 0)

        if circles is not None and circles.size > 0:
            maxRadius = 0
            x = 0
            y = 0
            found = False

            for c in circles[0]:
                found = True
                if c[2] > maxRadius:
                    maxRadius = int(c[2])
                    x = int(c[0])
                    y = int(c[1])
            if found:
                # Для наглядности, поверх изображения накладывается окружность синего цвета, а центр этой окружности обозначается зеленой точкой
                cv2.circle(frameProcess, (x, y), 3, (0, 255, 0), -1)
                cv2.circle(frameProcess, (x, y), maxRadius, (255, 0, 0), 3)

                if dt != 0:
                    xspeed = abs(x - self.lastx) / dt;
                    yspeed = abs(y - self.lasty) / dt;

                self.lastx = x
                self.lasty = y

                # На основе координат обнаруженной окружности, рассчитываются углы поворота сервоприводов
                # if SERVO_ON:
                # yaw = (x*1./w)*50.0 - 25.0
                # pitch = (y*1./h)*39.0 - 19.5
                # sctrl.shift(0, (x*1./w)*20-10)
                # sctrl.shift(1, -((y*1./h)*20-10))

        if FLIP:
            img = cv2.flip(frameProcess, 0)
            thresh = cv2.flip(thresh, 0)

        # cv2.imshow(self.color, thresh)

        #  В углу кадра отображаем время между двумя кадрами
        if dt != 0:
            text = '%0.1f' % (1. / dt)
            cv2.putText(frameProcess, text, (20, 20),
                        cv2.FONT_HERSHEY_PLAIN,
                        1.0, (0, 110, 0), thickness=2)

        """Перевод изображения из opencv в QPixmap для вывода на главную форму"""
        rgb_image = cv2.cvtColor(frameProcess, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        bytesPerLine = channels * width
        convertToQtFormat = QImage(rgb_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        frameScaled = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        self.frameOut = QPixmap.fromImage(frameScaled)  # Для вывода на битмап на форме

if __name__ == '__main__':
    App = QApplication.instance()
    if App is None:
        App = QApplication(sys.argv)
    ui = Dialog_01()
    ui.show()
    sys.exit(App.exec_())