# Импорт библиотек tkinter для создания GUI, messagebox для вывода окон сообщений, deque для очереди и random для генерации случайных чисел.
from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
import time
from datetime import time, date, datetime

# Размеры поля
SIZE_X = 10
SIZE_Y = 10

# Константы состояний клетки
STATE_DEFAULT = 0  # Не нажата
STATE_CLICKED = 1  # Нажата
STATE_FLAGGED = 2  # Помечена флажком

# Обработка нажатий кнопок мыши (левая и правая)
BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

window = None

# Основной класс игры Minesweeper
class Minesweeper:

    # Инициализация игры
    def __init__(self, tk):

        # Загрузка изображений для клеток поля
        self.images = {
            "plain": PhotoImage(file = "images/tile_plain.gif"),  # пустая клетка
            "clicked": PhotoImage(file = "images/tile_clicked.gif"),  # нажата
            "mine": PhotoImage(file = "images/tile_mine.gif"),  # мина
            "flag": PhotoImage(file = "images/tile_flag.gif"),  # флаг
            "wrong": PhotoImage(file = "images/tile_wrong.gif"),  # неверный флаг
            "numbers": []  # изображения с цифрами
        }
        # Загрузка изображений цифр от 1 до 8 для отображения количества мин рядом
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file = "images/tile_"+str(i)+".gif"))

        # Настройка интерфейса
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # Создание меток для отображения времени, количества мин и флажков
        self.labels = {
            "time": Label(self.frame, text = "00:00:00"),
            "mines": Label(self.frame, text = "Мины: 0"),
            "flags": Label(self.frame, text = "Флаги: 0")
        }
        # Расположение меток в интерфейсе
        self.labels["time"].grid(row = 0, column = 0, columnspan = SIZE_Y)  # метка времени
        self.labels["mines"].grid(row = SIZE_X+1, column = 0, columnspan = int(SIZE_Y/2))  # метка мин
        self.labels["flags"].grid(row = SIZE_X+1, column = int(SIZE_Y/2)-1, columnspan = int(SIZE_Y/2))  # метка флагов

        self.restart()  # Запуск новой игры
        self.updateTimer()  # Инициализация таймера

    # Настройка игрового поля
    def setup(self):
        # Переменные для счёта флагов, правильных флагов, нажатых клеток и времени старта
        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0
        self.startTime = None

        # Создание кнопок (клеток) игрового поля
        self.tiles = dict({})
        self.mines = 0  # количество мин
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + "_" + str(y)
                isMine = False  # является ли клетка миной

                gfx = self.images["plain"]  # начальная картинка клетки

                # Генерация мин случайным образом
                if random.uniform(0.0, 1.0) < 0.1:  # 10% вероятность мины
                    isMine = True
                    self.mines += 1

                # Создание объекта клетки
                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,  # начальное состояние клетки
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(self.frame, image = gfx),  # кнопка для клетки
                    "mines": 0  # количество мин рядом с клеткой (будет вычислено позже)
                }

                # Привязка событий кликов мыши к кнопке
                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid(row = x+1, column = y)  # размещение кнопки на поле

                self.tiles[x][y] = tile

        # Определение количества мин вокруг каждой клетки
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                mc = 0
                for n in self.getNeighbors(x, y):  # получение соседей клетки
                    mc += 1 if n["isMine"] else 0  # увеличение счётчика мин
                self.tiles[x][y]["mines"] = mc

    # Перезапуск игры
    def restart(self):
        self.setup()  # настройка поля заново
        self.refreshLabels()  # обновление меток

    # Обновление меток
    def refreshLabels(self):
        self.labels["flags"].config(text = "Флаги: "+str(self.flagCount))
        self.labels["mines"].config(text = "Мины: "+str(self.mines))

    # Окончание игры
    def gameOver(self, won):
        # Обновление состояния кнопок после завершения игры
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image = self.images["wrong"])
                if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image = self.images["mine"])

        self.tk.update()

        # Показ сообщения о победе или поражении
        msg = "Вы выиграли! Играть снова?" if won else "Вы проиграли! Играть снова?"
        res = tkMessageBox.askyesno("Конец игры", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()

    # Обновление таймера
    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0]  # убираем миллисекунды
            if delta.total_seconds() < 36000:
                ts = "0" + ts  # добавляем ноль в начале при необходимости
        self.labels["time"].config(text = ts)
        self.frame.after(100, self.updateTimer)  # обновляем каждую 1/10 секунды

    # Получение соседних клеток
    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x-1,  "y": y-1},  # верхний левый
            {"x": x-1,  "y": y},    # верхний
            {"x": x-1,  "y": y+1},  # верхний правый
            {"x": x,    "y": y-1},  # левый
            {"x": x,    "y": y+1},  # правый
            {"x": x+1,  "y": y-1},  # нижний левый
            {"x": x+1,  "y": y},    # нижний
            {"x": x+1,  "y": y+1},  # нижний правый
        ]
        # Проверка на границы поля
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    # Обработчик нажатия левой кнопки мыши
    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    # Обработчик нажатия правой кнопки мыши
    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    # Логика обработки нажатия на клетку
    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile["isMine"] == True:
            # Игра окончена (проигрыш)
            self.gameOver(False)
            return

        # Изменение изображения клетки
        if tile["mines"] == 0:
            tile["button"].config(image = self.images["clicked"])
           
            self.clearSurroundingTiles(tile["id"])  # очистка соседних клеток, если рядом нет мин
        else:
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])  # отображение цифры, если рядом есть мины
        
        # Если клетка еще не была нажата, изменить её состояние и обновить счётчик нажатий
        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        
        # Если все клетки, кроме мин, нажаты — игра выиграна
        if self.clickedCount == (SIZE_X * SIZE_Y) - self.mines:
            self.gameOver(True)  # вызов завершения игры с победой

    # Логика обработки нажатия правой кнопки мыши (установка/снятие флага)
    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        # Если клетка не была нажата, можно установить флаг
        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image = self.images["flag"])  # установка изображения флага
            tile["state"] = STATE_FLAGGED  # изменение состояния клетки на "помечена флагом"
            tile["button"].unbind(BTN_CLICK)  # запрет на нажатие левой кнопкой
            # Если на месте клетки находится мина, увеличиваем счётчик правильных флагов
            if tile["isMine"] == True:
                self.correctFlagCount += 1
            self.flagCount += 1  # увеличение общего количества флагов
            self.refreshLabels()  # обновление информации в метках (количество флагов)
        
        # Если клетка помечена флагом, можно снять флаг
        elif tile["state"] == STATE_FLAGGED:
            tile["button"].config(image = self.images["plain"])  # возврат к исходному изображению клетки
            tile["state"] = STATE_DEFAULT  # возврат состояния клетки к начальному
            tile["button"].bind(BTN_CLICK, self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))  # разрешение клика левой кнопкой
            # Если клетка с флагом была миной, уменьшаем счётчик правильных флагов
            if tile["isMine"] == True:
                self.correctFlagCount -= 1
            self.flagCount -= 1  # уменьшение общего количества флагов
            self.refreshLabels()  # обновление информации в метках

    # Функция для очистки всех соседних клеток
    def clearSurroundingTiles(self, id):
        queue = deque([id])  # создаём очередь для проверки соседних клеток

        while len(queue) != 0:
            key = queue.popleft()  # берём первую клетку из очереди
            parts = key.split("_")  # разделяем идентификатор на координаты
            x = int(parts[0])
            y = int(parts[1])

            # Проходим по соседним клеткам
            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)  # очищаем соседние клетки

    # Функция для очистки отдельной клетки
    def clearTile(self, tile, queue):
        # Если клетка уже была обработана, пропускаем её
        if tile["state"] != STATE_DEFAULT:
            return

        # Если вокруг клетки нет мин, меняем её изображение на "нажато" и добавляем её в очередь для дальнейшей проверки
        if tile["mines"] == 0:
            tile["button"].config(image = self.images["clicked"])
            queue.append(tile["id"])
        else:
            # Если рядом есть мины, отображаем соответствующую цифру
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])

        tile["state"] = STATE_CLICKED  # устанавливаем состояние "нажато"
        self.clickedCount += 1  # увеличиваем счётчик нажатых клеток

### Конец определения класса ###

# Главная функция
def main():
    # Создание экземпляра Tk (окно приложения)
    window = Tk()
    # Установка заголовка программы
    window.title("Minesweeper")
    # Создание экземпляра игры Minesweeper
    minesweeper = Minesweeper(window)
    # Запуск основного цикла событий (игры)
    window.mainloop()

# Запуск программы
if __name__ == "__main__":
    main()
