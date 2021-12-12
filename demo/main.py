# Это Python программа Leonov Vladislav 181-311
# Подключение библиотек
import sys                                                            # Предоставляет системе особые параметры и функции
import cv2                                                            # OpenCV - техническое зрение (opencv-python)
from threading import Thread                                          # Для создания нового потока
from time import sleep                                                # Для управления временем работы потока
# Поделючение GUI интерфейса
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

''' -------- Главная форма ------- '''
class Window(QMainWindow):
    def __init__(self):
        super().__init__()                                            # Python 3.x унаследуем от QMainWindow
        # super(Window, self).__init__()                              # Python 2.x унаследуем от QMainWindow в class Win

        self.formOpening()                                            # Настройки и запуск формы

        # Подписки на события
        self.ui.bCameraWork.clicked.connect(self.cameraWorkClicked)   # Включение камеры
        self.ui.bSaveImage.clicked.connect(self.saveImageClicked)     # Сохранить изображение
        self.ui.bSaveVideo.clicked.connect(self.recordClicked)        # Записать видео

    def formOpening(self):
        # Настройки окна главной формы
        self.ui = uic.loadUi('GUI.ui')                                # GUI, должен быть в папке с main.py
        self.ui.setWindowTitle('Автоматически балансирующий '
                               'стол 181-311')                        # Название главного окна
        self.ui.setWindowIcon(QIcon('surflay.ico'))                   # Иконка на гланое окно
        self.ui.show()                                                # Открываем окно формы

        # Флаги работы программы
        self.flagCameraWork = False                                   # Флаг работы камеры
        self.record = False                                           # Флаг записи ведо до остановки

        # Переменные для работы с камерой
        self.capture = None                                           # Захват изображение с камеры
        self.frameIn = None                                           # Входное (сырое) изображение с камеры
        self.frameOut = None                                          # Выходное (Обработанное) изображение с камеры
        self.frameToSave = None                                       # Обработанное изображение для сохранения

        # Переменные
        self.displayWidth = 640                                       # Ширина BitMap на форме
        self.displayHeight = 480                                      # Высота BitMap на форме
        self.numberImage = 0                                          # Переменная номера изображения

        # Создание изображение с фоном цвета Gainsboro
        grey = QPixmap(self.displayWidth, self.displayHeight)         # Создание фонового изображения для битмапа
        grey.fill(QColor('Gainsboro'))                                # Заливаем это изображение цветом Gainsboro
        self.ui.Bitmap.setPixmap(grey)                                # Вывести изображение на BitMap на форме

    # Нажатие на кнопку включения камеры
    def cameraWorkClicked(self):
        if self.flagCameraWork:
            self.flagCameraWork = False
            self.ui.bCameraWork.setText('Включить видео с камеры')
            self.cap.release()
            cv2.destroyAllWindows()
        else:
            self.flagCameraWork = True
            self.ui.bCameraWork.setText('Выключить видео с камеры')
            thread = Thread(target=self.ThreadCamera)
            thread.start()

    # Поток для камеры
    def ThreadCamera(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while self.capture.isOpened():
            ret, self.frameIn = self.capture.read()
            if ret:
                self.frameProcessing()                                # Обработка изображения
                self.ui.Bitmap.setPixmap(self.frameOut)               # Вывод обработанного изображения на форму
                # cv2.imshow('Camera', self.frameOut2)                # Вывод изображения с камеры
                cv2.waitKey(10)

    # Обработка сырого изображения с камеры
    def frameProcessing(self):
        # Цветовое пространство
        if self.ui.BgrButton.isChecked():
            # Оставляем в RGB
            frameProcess = self.frameIn                               # Копируем входное изображение для его обработки
            self.ui.labelS1.setText('R')
            self.ui.labelS2.setText('G')
            self.ui.labelS3.setText('B')
        elif self.ui.HsvButton.isChecked():
            # Перевод из RGB в HSV
            frameProcess = cv2.cvtColor(self.frameIn, cv2.COLOR_BGR2HSV)
            self.ui.labelS1.setText('H')
            self.ui.labelS2.setText('S')
            self.ui.labelS3.setText('V')
        elif self.ui.GrayButton.isChecked():
            # Перевод из RGB в GRAY
            frameProcess = cv2.cvtColor(self.frameIn, cv2.COLOR_BGR2GRAY)
            self.ui.labelS1.setText('G')
            self.ui.labelS2.setText('0')
            self.ui.labelS3.setText('0')

        # Яркость и контраст
        if self.ui.BrightnessContrastCheckBox.isChecked():
            maxGray = int(self.ui.BrightnessSliderMax.value())        # Минимальное значение для подсчёта alpha и beta
            minGray = int(self.ui.BrightnessSlider.value())           # Максимальное значение для подсчёта alpha и beta
            if maxGray != minGray:
                alpha = 255 / (maxGray - minGray)                     # Яркость
                beta = -minGray * alpha                               # Контраст
                frameProcess = cv2.convertScaleAbs(frameProcess, alpha=alpha, beta=beta)
            self.ui.labelSystemMassage.setText('Статус: Яркость и контраст')


        # Обрезка
        if self.ui.CropCheckBox.isChecked():
            x = self.ui.XSlider.value()
            y = self.ui.YSlider.value()
            w = self.ui.WSlider.value()
            h = self.ui.HSlider.value()
            frameProcess = frameProcess[y:y+h, x:x+w]
            self.ui.labelSystemMassage.setText('Статус: Обрезка')

        # Масштабирование
        if self.ui.ScaleCheckBox.isChecked():
            # Нам надо сохранить соотношение сторон
            # Чтобы изображение не исказилось при уменьшении
            # Для этого считаем коэф. уменьшения стороны
            ScaleValue = int(self.ui.ScaleSlider.value())               # Процент от изначального размера

            newWidth = int(frameProcess.shape[1] * ScaleValue / 100)
            newHeight = int(frameProcess.shape[0] * ScaleValue / 100)
            dim = (newWidth, newHeight)                                 # newWidth, newHeight
            frameProcess = cv2.resize(frameProcess, dim, interpolation=cv2.INTER_AREA)
            self.ui.labelSystemMassage.setText('Статус: Масштабирование ' + str(ScaleValue) + "%")

        # Бинаризация
        if self.ui.BinarizeCheckBox.isChecked():
            if self.ui.GrayButton.isChecked():
                lower = self.ui.Lower1stBox.value()
                upper = self.ui.Upper1stBox.value()
            else:
                lower = (self.ui.Lower1stBox.value(), self.ui.Lower2ndBox.value(), self.ui.Lower3rdBox.value())
                upper = (self.ui.Upper1stBox.value(), self.ui.Upper2ndBox.value(), self.ui.Upper3rdBox.value())
            self.ui.labelSystemMassage.setText('Статус: Бинаризация')
            frameProcess = cv2.inRange(frameProcess, lower, upper)

        """Перевод изображения из opencv в QPixmap для вывода на главную форму"""
        rgb_image = cv2.cvtColor(frameProcess, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_image.shape
        bytesPerLine = channels * width
        convertToQtFormat = QImage(rgb_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        frameScaled = convertToQtFormat.scaled(self.displayWidth, self.displayHeight, Qt.KeepAspectRatio)
        self.frameOut = QPixmap.fromImage(frameScaled)          # Для вывода на битмап на форме
        self.frameToSave = frameProcess                         # Для сохранения изображения
        self.frameOut2 = frameProcess                           # Для вывода в отдельное окно для сравнения с frameOut

    # Клик по кнопке "Сохранить изображение"
    def saveImageClicked(self):
        if self.flagCameraWork:
            self.numberImage += 1
            cv2.imwrite('SavedImages/Image' + str(self.numberImage) + '.png', self.frameToSave)
            self.ui.labelSystemMassage.setText('Статус: Сохранено Image' + str(self.numberImage))

    # Клик по кнопке "Начать съёмку"
    def recordClicked(self):
        interval = self.ui.IntervalSpinBox.value() / 1000       # Интервал сохранения

        # Режим нажатия кнопки остановки
        if self.ui.FrameModeButton.isChecked():
            thread = Thread(target=self.recordThread1, args=(1, interval))

        # Режим заданного количества кадров
        elif self.ui.StopModeButton.isChecked():
            if self.record:
                self.ui.bSaveVideo.setText('Включить видеосъёмку ')
                self.record = False
            else:
                self.ui.bSaveVideo.setText('Отключить видеосъёмку ')
                self.record = True
            thread = Thread(target=self.recordThread2, args=(1, interval))

        thread.start()

    # Поток для съёмки в режиме заданного количества кадров
    def recordThread1(self, first_interval, interval):
        count = self.ui.FrameCountSpinBox.value()
        sleep(first_interval)

        for i in range(0, count):
            self.saveImageClicked()
            sleep(interval)

        self.ui.labelSystemMassage.setText('Статус: Запись завершена')

    # Поток для съёмки в режиме нажатия кнопки остановки
    def recordThread2(self, first_interval, interval):
        sleep(first_interval)

        while self.record:
            self.saveImageClicked()
            sleep(interval)

        self.ui.labelSystemMassage.setText('Статус: Запись завершена')


''' --------Запуск формы------- '''
if __name__ == '__main__':
    app = QApplication(sys.argv)                                      # Объект приложения (экземпляр QApplication)
    win = Window()                                                    # Создание формы
    # Вход в главный цикл приложения
    sys.exit(app.exec_())                                             # Выход после закрытия приложения




