<h1 align="center">auto-balancing-table</h1>
<h1 align="center">Автоматически балансирующий стол</h1>

<p align="center">

<img src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" >
  
<img src="https://img.shields.io/github/repo-size/BouRHooD/auto-balancing-table" >
  
<img src="https://img.shields.io/github/last-commit/bourhood/auto-balancing-table" >
  
</p>

---

RU: Поверхность наклоняется сервоприводами для перемещения шара на основе видео с камеры, которая будет детектировать центр объекта в пространстве.

EN: The surface is tilted by servos to move the ball based on the video from the camera, which will detect the center of the object in space.

# [View a demo](https://coub.com/view/2j0dqt)

---
<h1 align="left"> Программа для детектирования окружности </h1>
Писать программу было решено на языке python. Алгоритм работы python-скрипта для распознавания состоит из шести основных шагов:
преобразование кадра в формат HSV;
фильтрация в заданном диапазоне HSV;
морфологическое преобразование;
размывание;
детектирование окружностей;
передача управляющих сигналов на сервоприводы.
