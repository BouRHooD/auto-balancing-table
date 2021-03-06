<h1 align="center">auto-balancing-table</h1>
<h1 align="center">Автоматически балансирующий стол</h1>

<p align="center">

<img src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" >
  
<img src="https://img.shields.io/github/repo-size/BouRHooD/auto-balancing-table" >
  
<img src="https://img.shields.io/github/last-commit/bourhood/auto-balancing-table" >
  
</p>

---

# Как работать с репозиторием: [ссылка](docs/howWorkWithRepository/howWorkWithRepository.md)

---

RU: Поверхность наклоняется сервоприводами для перемещения шара на основе видео с камеры, которая будет детектировать центр объекта в пространстве.

EN: The surface is tilted by servos to move the ball based on the video from the camera, which will detect the center of the object in space.

# [View a demo](https://coub.com/view/2j0dqt)

---
<h1 align="left"> Программа для детектирования окружности </h1>
Алгоритм работы программы для распознавания состоит из 6 основных шагов:

1. преобразование кадра в формат HSV;
2. фильтрация в заданном диапазоне HSV;
3. морфологическое преобразование;
4. размывание;
5. детектирование окружностей;
6. передача управляющих сигналов на сервоприводы.

![Иллюстрация к проекту](https://github.com/BouRHooD/auto-balancing-table/raw/main/docs/images/exemple_img_detected_ball_.jpg)

---
<h1 align="left"> Программа пользователя для задания траектории </h1>
Алгоритм работы программы для распознавания состоит из 6 основных шагов:

1. переключение в режим задания траектории;
2. получение координаты указателя мыши по щелчку левой кнопкой;
3. проверка попадания координат в границы стола;
4. перерасчёт координат, если не попали в границы стола;
5. запоминаем значения координат;
6. рисуем на рабочей области.

![Иллюстрация к проекту](https://github.com/BouRHooD/auto-balancing-table/raw/main/docs/images/ABT_MainUser.png)

# Обновленный интерфейс
![Иллюстрация к проекту](https://github.com/BouRHooD/auto-balancing-table/raw/main/docs/images/updatedUI.png)


