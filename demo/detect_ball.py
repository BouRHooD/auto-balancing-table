import sys, time
from threading import Thread
import cv2
import numpy as np


COM = 'COM4'

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

def nothing( *arg ):
    pass

def createPath( img ):
    h, w = img.shape[:2] 
    return np.zeros((h, w, 3), np.uint8)

class Tracker(Thread):
    def __init__(self, color, color_2=None, flag=0):
        Thread.__init__(self)
        self.color = color

        self.lastx = 0
        self.lasty = 0
        self.time = 0
 
        self.h_min = COLOR_RANGE[color][0] 
        self.h_max = COLOR_RANGE[color][1]
        if color_2:
            self.h_min_2 = COLOR_RANGE[color_2][0]
            self.h_max_2 = COLOR_RANGE[color_2][1]

        self.flag = flag
 
        if self.flag:
            cv2.namedWindow(self.color)
 
    def poll(self,img):
        par1 = 80 #40
        par2 = 50 #67
        h, w = img.shape[:2]
        dt = time.process_time() - self.time
        self.time = time.process_time()
        
        # Функция inRange преобразует цветную картинку в черно-белую маску. В этой маске, все пиксели, попадающие в заданный диапазон — становятся белыми. Прочие — черными.
        # В HSV проще создать правильную маску для выделения нужного цвета
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV )
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
            circles = cv2.HoughCircles( thresh, 
                                        cv2.HOUGH_GRADIENT, 2, h/4,
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
                cv2.circle(img, (x, y), 3, (0,255,0), -1)
                cv2.circle(img, (x, y), maxRadius, (255,0,0), 3)

                if dt != 0:
                    xspeed = abs(x - self.lastx)/dt;
                    yspeed = abs(y - self.lasty)/dt;
 
                self.lastx = x
                self.lasty = y
                
                # На основе координат обнаруженной окружности, рассчитываются углы поворота сервоприводов
                # if SERVO_ON:
                    # yaw = (x*1./w)*50.0 - 25.0
                    # pitch = (y*1./h)*39.0 - 19.5
                    # sctrl.shift(0, (x*1./w)*20-10)
                    # sctrl.shift(1, -((y*1./h)*20-10))

        if FLIP:
            img = cv2.flip(img,0)
            thresh = cv2.flip(thresh,0)

        if self.flag:
            cv2.imshow(self.color, thresh)
        
        #  В углу кадра отображаем время между двумя кадрами
        if dt != 0:
            text = '%0.1f' % (1./dt)
            cv2.putText( img, text, (20, 20),
                         cv2.FONT_HERSHEY_PLAIN,
                         1.0, (0, 110, 0), thickness = 2)

        if SHOW_MAIN:
            cv2.imshow('result', img)

if __name__ == '__main__':
    if SHOW_MAIN:
        cv2.namedWindow( "result", cv2.WINDOW_AUTOSIZE)

    green = Tracker('ball_light', 'ball_dark', SHOW_THRESH)
    green.start()

    # if SERVO_ON:
        # sctrl = Servo( com=COM )
        # sctrl.setpos(0,45)
        # sctrl.setpos(1,45)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    flag, img = cap.read()
    green.path = createPath(img)

    while True:
        flag, img = cap.read()
        try:
            green.poll(img)
        except:
            cap = None
            green = None
            # if SERVO_ON:
                #sctrl.stop()
            raise
 
        green.join()
        ch = cv2.waitKey(5)
        if ch == 27:
            break

    # if SERVO_ON:
        # sctrl.setpos(0,45)
        # sctrl.setpos(1,45)
        # sctrl.stop()

    green = None
    cap = None
    cv2.destroyAllWindows()

