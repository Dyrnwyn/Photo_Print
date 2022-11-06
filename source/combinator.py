import os
import re
from psd_tools import PSDImage
from PIL import ImageFilter, Image, ImageDraw, ImageFont
from PyQt5 import QtCore
import datetime
import platform


def search_file(flExt, fldr=""):
    # Во временно директории ищем все файлы c переданным разрешением
    # И добавляем их в список
    filteredFlList = []
    with os.scandir(fldr) as flList:
        for fl in flList:
            if not fl.name.startswith('.') and fl.is_file() and \
                    re.findall(r"^.*\." + flExt + "*", fl.name):
                filteredFlList.append(fl.name)
    return filteredFlList


class ThreadForConvert(QtCore.QThread):
    ratio_dict = {"п_10х15_": 1.5,
                  "п_15х20_": 1.333,
                  "п_20х30_": 1.5,
                  "п_Настенный календарь_": 1.3778,
                  "п_магнит_": 1.428,
                  "п_магнит 10х15_": 1.5,
                  "о_10х15_": 1.5,
                  "о_15х20_": 1.333,
                  "о_20х30_": 1.5,
                  "о_Настенный календарь_": 1.3778,
                  "о_магнит 10х15_": 1.5,
                  "о_календарик 7х10_": 1.428,
                  "_Брелок 58_": 0.32,
                  "_Зеркало 75_": 0.4,
                  "_Значок 75_": 0.4,
                  "_Значок 100_": 0.518,
                  "_Значок 158_": 0.84,
                  "_Копилка 158_": 0.84,
                  "_Кружка-термос с крышкой_": 0}

    dict_of_sizes = {"п_10х15_": (1772, 1181),
                     "п_15х20_": (2362, 1772),
                     "п_20х30_": (3543, 2362),
                     "п_Настенный календарь_": (3661, 2657),
                     "п_магнит_": (1181, 827),
                     "п_магнит 10х15_": (1772, 1181),
                     "о_10х15_": (1772, 1181),
                     "о_15х20_": (2362, 1772),
                     "о_20х30_": (3543, 2362),
                     "о_Настенный календарь_": (3661, 2657),
                     "о_магнит 10х15_": (1772, 1181),
                     "о_календарик 7х10_": (1181, 827),
                     "_Брелок 58_": 0.32,
                     "_Зеркало 75_": 0.4,
                     "_Значок 75_": 0.4,
                     "_Значок 100_": 0.518,
                     "_Значок 158_": 0.84,
                     "_Копилка 158_": 0.84,
                     "_Кружка-термос с крышкой_": 0}
    dict_of_photo_png = {"п_10х15_": {},
                         "п_15х20_": {},
                         "п_20х30_": {},
                         "п_магнит_": {},
                         "п_магнит 10х15_": {},
                         "о_10х15_": {},
                         "о_15х20_": {},
                         "о_20х30_": {},
                         "о_магнит 10х15_": {},
                         "о_календарик 7х10_": {},
                         "п_Настенный календарь_": {},
                         "о_Настенный календарь_": {},
                         "_Брелок 58_": {},
                         "_Зеркало 75_": {},
                         "_Значок 75_": {},
                         "_Значок 100_": {},
                         "_Значок 158_": {},
                         "_Копилка 158_": {},
                         "_Кружка-термос с крышкой_": {}}
    rotate_dict = {"п_10х15_": (Image.ROTATE_90, 0),
                   "п_15х20_": (0, Image.ROTATE_90),
                   "п_20х30_": (Image.ROTATE_90, 0),
                   "п_Настенный календарь_": (Image.ROTATE_90, 0),
                   "п_магнит_": (0, Image.ROTATE_90),
                   "п_магнит 10х15_": (Image.ROTATE_90, 0),
                   "о_10х15_": (Image.ROTATE_90, 0),
                   "о_15х20_": (0, Image.ROTATE_90),
                   "о_20х30_": (Image.ROTATE_90, 0),
                   "о_Настенный календарь_": (Image.ROTATE_90, 0),
                   "о_магнит 10х15_": (Image.ROTATE_90, 0),
                   "о_календарик 7х10_": (0, Image.ROTATE_90),
                   "_Кружка-термос с крышкой_": (Image.ROTATE_90, 0)}
    format_weight = {"п_10х15_": 2,
                     "п_15х20_": 4,
                     "п_20х30_": 8,
                     "п_магнит_": 1,
                     "п_магнит 10х15_": 2,
                     "о_10х15_": 2,
                     "о_15х20_": 4,
                     "о_20х30_": 8,
                     "о_магнит 10х15_": 2,
                     "о_календарик 7х10_": 1,
                     "п_Настенный календарь_": 8,
                     "о_Настенный календарь_": 8,
                     "_Брелок 58_": 1,
                     "_Зеркало 75_": 1,
                     "_Значок 75_": 1,
                     "_Значок 100_": 1,
                     "_Значок 158_": 1,
                     "_Копилка 158_": 1,
                     "_Кружка-термос с крышкой_": 1}
    count_converted_photo = QtCore.pyqtSignal(int)
    messages_what_work = QtCore.pyqtSignal(str)
    # список имен плосских фотографий
    flat_photo_name_list = ("п_10х15_", "п_15х20_", "п_20х30_", "п_магнит_", "п_магнит 10х15_")
    # список имен плосских фотографий
    stereo_photo_name_list = ("о_10х15_", "о_15х20_", "о_20х30_", "о_магнит 10х15_", "о_календарик 7х10_")
    # список имен плосских фотографий
    wall_calendar_name_list = ("п_Настенный календарь_", "о_Настенный календарь_")
    badge_name_list = ("_Брелок 58_", "_Зеркало 75_", "_Значок 75_", "_Значок 100_", "_Значок 158_", "_Копилка 158_")
    cup_name_list = ("_Кружка-термос с крышкой_")
    dpi = ""
    dict_of_psd_files = {}
    dir_for_png = ''
    dir_to_print = ''
    list_to_print_on_210x297 = []
    list_to_print_on_610x320 = []
    font_file = ""
    sizes_foto = {
        "210x297": {"ColorSpace": 'RGB', "Size": (2480, 3508), "Color": (255, 255, 255)},
        "225x320": {"ColorSpace": 'RGB', "Size": (2657, 3780), "Color": (255, 255, 255)},
        "110x320": {"ColorSpace": 'RGB', "Size": (1299, 3780), "Color": (255, 255, 255)},
        "200x320": {"ColorSpace": 'RGB', "Size": (2362, 3780), "Color": (255, 255, 255)},
        "610x320": {"ColorSpace": 'RGB', "Size": (7205, 3780), "Color": (255, 255, 255)},
    }
    current_object = ""
    dir_for_save_complete_file = ""
    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        self.convert_psd_to_png()
        self.add_photo_to_61x32_main()

    def get_font(self):
        font = ImageFont.truetype(self.font_file, 48)
        return font

    def add_photo_to_61x32_main(self):
        self.add_wallpaper_to_61x32()
        self.add_flat_photo_225x320_to_61x32()
        self.add_cup_to_210x197()
        #  self.add_badge_to_210x197_main()

    def set_var(self, dpi, psd_dict, dir_for_png, dir_to_print,
                list_to_print_on_210x297=[],
                list_to_print_on_610x320=[], font_file="",
                current_object=""):
        """Устанавливаем значения переменных
        разрешение фотографии dpi, словарь psd файлов, путь к папке для еконвертации в png"""
        self.dpi = dpi
        self.dict_of_psd_files = psd_dict
        self.dir_for_png = dir_for_png
        self.dir_to_print = dir_to_print
        self.list_to_print_on_210x297 = list_to_print_on_210x297
        self.list_to_print_on_610x320 = list_to_print_on_610x320
        self.font_file = font_file
        self.current_object = current_object
        self.dir_for_save_complete_file = self.dir_to_print + os.sep + self.current_object + os.sep
        self.check_exists_dir(self.dir_to_print + os.sep + self.current_object)

    def check_exists_dir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
    def draw_title(self, img, text, point):
        font = self.get_font()
        draw_text = ImageDraw.Draw(img)
        draw_text.text(point, text, font=font, fill=(0, 0, 0))
        return img

    def add_cup_to_210x197(self):
        photo_format = "_Кружка-термос с крышкой_"
        point = [[(75, 160), (20, 15)], [(1265, 160), (1000, 65)]]
        count_photo_on_210x297 = 0
        image_210x297 = self.new_image("210x297")
        while self.get_availability_of_photo(photo_format):
            if count_photo_on_210x297 == 2:
                self.save_png_image(image_210x297, self.dir_to_print + "cup_" + str(
                                    self.get_time_for_filename()) + '.png')
                image_210x297 = self.new_image("210x297")
                count_photo_on_210x297 = 0
            image, title = self.get_not_printed_photo_with_title(photo_format)
            image_cup = Image.open(image)
            image_210x297.paste(image_cup, point[count_photo_on_210x297][0])
            image_210x297 = self.draw_title(image_210x297, title, point[count_photo_on_210x297][1])
            count_photo_on_210x297 += 1
        if count_photo_on_210x297 != 0:
            self.save_png_image(image_210x297, self.dir_to_print + "cup_" + str(self.get_time_for_filename()) + '.png')
        return

    def add_badge_to_210x197_main(self):
        photo_format = "_Копилка 158_"
        while self.get_availability_of_photo(photo_format):
            img, title = self.get_not_printed_photo_with_title(photo_format)
            badge_img = Image.open(img)
            print(badge_img.getbbox())

    def add_flat_photo_20x32_to_61x32(self):
        # point = [(59, 0), (2421, 0), (4783, 0)]
        point = [(59, 0), (2521, 0), (4883, 0)]
        count_photo_on_61x32 = 0
        image_61x32 = self.new_image("610x320")
        while self.get_availability_of_flat_photo():
            image_20x32 = self.get_flat_photo_on_20x32()
            image_61x32.paste(image_20x32, point[count_photo_on_61x32])
            if count_photo_on_61x32 == 2:
                self.save_png_image(image_61x32, self.dir_to_print + str(self.get_time_for_filename()) + '.png')
                count_photo_on_61x32 = 0
                image_61x32 = self.new_image_61x32()
            else:
                count_photo_on_61x32 += 1
        if count_photo_on_61x32 != 0:
            self.save_png_image(image_61x32, self.dir_to_print + str(self.get_time_for_filename()) + '.png')
        return

    def add_flat_photo_225x320_to_61x32(self):
        point = [(60, 0), (2890, 0), (5670, 0)]
        count_photo_on_61x32 = 0
        image_61x32 = self.new_image("610x320")
        while self.get_availability_of_flat_photo():
            if count_photo_on_61x32 == 2:
                image_11x32 = self.get_photo_on_11x32()
                image_61x32.paste(image_11x32, point[count_photo_on_61x32])
                self.save_png_image(image_61x32, self.dir_for_save_complete_file + str(self.get_time_for_filename()) + ".png")
                count_photo_on_61x32 = 0
                image_61x32 = self.new_image("610x320")
            elif count_photo_on_61x32 < 2:
                image_225x320 = self.get_flat_photo_on_225x320()
                image_61x32.paste(image_225x320, point[count_photo_on_61x32])
                count_photo_on_61x32 += 1
        if count_photo_on_61x32 != 0:
            self.save_png_image(image_61x32, self.dir_for_save_complete_file + str(self.get_time_for_filename()) + '.png')
        return

    def add_wallpaper_to_61x32(self):
        wallpaper_point = [[(60, 0), (240, 10)], [(2890, 0), (3640, 10)], [(5670, 0), (5700, 10)]]
        count_photo_on_61x32 = 0
        while self.get_availability_of_photo("п_Настенный календарь_"):
            if count_photo_on_61x32 == 0:
                image_61x32 = self.new_image_61x32()
            wlp_img = self.add_calendar_to_225x320()
            image_61x32.paste(wlp_img, wallpaper_point[count_photo_on_61x32][0])
            count_photo_on_61x32 += 1
            if count_photo_on_61x32 == 2:
                image_11x32 = self.get_photo_on_11x32()
                image_61x32.paste(image_11x32, wallpaper_point[count_photo_on_61x32][0])
                self.save_png_image(image_61x32, self.dir_to_print + str(self.get_time_for_filename()) + ".png")
                count_photo_on_61x32 = 0
        if count_photo_on_61x32 == 1:
            if self.get_availability_of_flat_photo():
                img = self.get_flat_photo_on_20x32()
                image_61x32.paste(img, wallpaper_point[count_photo_on_61x32][0])
                count_photo_on_61x32 += 1
            else:
                count_photo_on_61x32 += 1
        if count_photo_on_61x32 == 2:
            image_11x32 = self.get_photo_on_11x32()
            image_61x32.paste(image_11x32, wallpaper_point[count_photo_on_61x32][0])
            self.save_png_image(image_61x32, self.dir_to_print + str(self.get_time_for_filename()) + ".png")
            count_photo_on_61x32 = 0
        if count_photo_on_61x32 == 0:
            return

    def add_calendar_to_225x320(self):
        walpaper_img, title = self.get_not_printed_photo_with_title("п_Настенный календарь_")
        img = Image.open(walpaper_img)
        img_225x320 = self.new_image_225x320()
        top = round((img_225x320.height - img.height) / 2)
        img_225x320.paste(img, (0, top))
        img_225x320 = self.draw_title(img_225x320, title, (0, 10))
        return img_225x320

    def get_flat_photo_on_20x32(self):
        photo_format_list = ("п_20х30_", "п_15х20_", "п_10х15_", "п_магнит 10х15_", "п_магнит_")
        point = [[(0, 117), (0, 70)], [(0, 1024), (0, 974)],
                 [(1181, 117), (1181, 70)], [(1181, 1024), (1181, 974)],
                 [(0, 117), (0, 70)], [(0, 1024), (0, 974)],
                 [(1181, 117), (1181, 70)], [(1181, 1024), (1181, 974)]]
        places = [0, 0, 0, 0,
                  0, 0, 0, 0]
        places_when_rotate = [1, 1, 1, 1,
                              0, 0, 0, 0]
        img20x32 = self.new_image_20x32()
        for photo_format in photo_format_list:
            while self.get_availability_of_photo(photo_format):
                if self.get_availability_of_free_space(places, photo_format):
                    if places == places_when_rotate:
                        img20x32 = img20x32.transpose(Image.ROTATE_180)
                    number_of_place, new_free_places = self.get_free_place(places, photo_format)
                    places = new_free_places
                    img_file, title = self.get_not_printed_photo_with_title(photo_format)
                    img = Image.open(img_file)
                    img20x32.paste(img, point[number_of_place][0])
                    img20x32 = self.draw_title(img20x32, title, point[number_of_place][1])
                else:
                    break
            continue
        return img20x32

    def get_flat_photo_on_225x320(self):
        # point = [[(30, 60), (30, 10)],
        #          [(30, 950), (30, 900)],
        #          [(30, 1910), (30, 1860)],
        #          [(30, 2840), (30, 2790)]]
        photo_format_list = ("п_20х30_", "п_15х20_", "п_10х15_", "п_магнит 10х15_", "п_магнит_")
        point = [[(50, 67), (50, 20)], [(50, 1000), (50, 950)],
                 [(1331, 67), (1331, 20)], [(1331, 1000), (1331, 950)],
                 [(50, 1947), (50, 1900)], [(50, 2890), (50, 2840)],
                 [(1331, 1947), (1331, 1907)], [(1331, 2890), (1331, 2840)]]
        places = [0, 0,
                  0, 0,
                  0, 0,
                  0, 0]
        img225x320 = self.new_image("225x320")
        for photo_format in photo_format_list:
            while self.get_availability_of_photo(photo_format):
                if self.get_availability_of_free_space(places, photo_format):
                    number_of_place, new_free_places = self.get_free_place(places, photo_format)
                    places = new_free_places
                    img_file, title = self.get_not_printed_photo_with_title(photo_format)
                    img = Image.open(img_file)
                    img225x320.paste(img, point[number_of_place][0])
                    img225x320 = self.draw_title(img225x320, title, point[number_of_place][1])
                else:
                    break
            continue
        return img225x320

    def get_photo_on_11x32(self):
        point = [[(30, 60), (30, 10)],
                 [(30, 950), (30, 900)],
                 [(30, 1910), (30, 1860)],
                 [(30, 2840), (30, 2790)]]
        places = [0, 0, 0, 0]
        image_11x32 = self.new_image("110x320")
        while self.get_availability_of_free_space(places, "п_магнит 10х15_"):
            if self.get_availability_of_photo("п_магнит 10х15_"):
                number_of_place, new_free_places = self.get_free_place(places, "п_магнит 10х15_")
                img_file, title = self.get_not_printed_photo_with_title("п_магнит 10х15_")
                places = new_free_places
                img = Image.open(img_file)
                image_11x32.paste(img, point[number_of_place][0])
                image_11x32 = self.draw_title(image_11x32, title, point[number_of_place][1])
            else:
                break
        while self.get_availability_of_free_space(places, "п_магнит_"):
            if self.get_availability_of_photo("п_магнит_"):
                number_of_place, new_free_places = self.get_free_place(places, "п_магнит_")
                img_file, title = self.get_not_printed_photo_with_title("п_магнит_")
                places = new_free_places
                img = Image.open(img_file)
                image_11x32.paste(img, point[number_of_place][0])
                image_11x32 = self.draw_title(image_11x32, title, point[number_of_place][1])
            else:
                break
        while self.get_availability_of_free_space(places, "п_10х15_"):
            if self.get_availability_of_photo("п_10х15_"):
                number_of_place, new_free_places = self.get_free_place(places, "п_10х15_")
                img_file, title = self.get_not_printed_photo_with_title("п_10х15_")
                places = new_free_places
                img = Image.open(img_file)
                image_11x32.paste(img, point[number_of_place][0])
                image_11x32 = self.draw_title(image_11x32, title, point[number_of_place][1])
            else:
                break
        return image_11x32

    def get_free_place(self, places, photo_format):
        """Получаем на входе массив с местами на листе и формат фотографии, который хотим
        разместить на листе, проверяем, если в массиве, есть 0(означает, свободное место под магнит), 
        тогда проверяем, влезет ли формат фотографии на лист, проряя сосдние места
        К примеру, если формат фотографии, занимает 2 места, нам необходимо 2 сосдних места в массиве.
        В качестве возращаемого результата, номер места, куда вставлять фотографию, и обновленный список мест
        где использованные места, заняты единицей(1)"""
        count_places = 0
        for i in places:
            if i == 0:
                free_place = len(places[count_places: len(places)])  # свободное место на листе
                if free_place >= self.format_weight[photo_format]:
                    count = count_places
                    take_places = count + self.format_weight[photo_format]
                    while count < take_places:
                        places[count] = 1
                        count += 1
                    return count_places, places
            count_places += 1
        return False

    def get_availability_of_free_space(self, places, photo_format):
        """Проверяем наличие места на листе для конкретного формата фотографии"""
        count_places = 0
        for i in places:
            if i == 0:
                free_place = len(places[count_places: len(places)])
                if free_place >= self.format_weight[photo_format]:
                    return True
            count_places += 1
        return False

    def get_time_for_filename(self):
        x = datetime.datetime.now()
        return x.strftime("%d-%b %H_%M_%S_%f")

    def get_availability_of_flat_photo(self):
        flat_photo = ["п_10х15_", "п_15х20_", "п_20х30_", "п_магнит_", "п_магнит 10х15_"]
        for f in flat_photo:
            if self.get_availability_of_photo(f):
                return True
        return False

    def get_availability_of_photo(self, photo_format):
        dict_current_photo_format = self.dict_of_photo_png[photo_format]
        for k, v in dict_current_photo_format.items():
            if v["Напечатанно"] == "not printed":
                return True
        return False

    def get_not_printed_photo_with_title(self, photo_format):
        dict_current_photo_format = self.dict_of_photo_png[photo_format]
        for k, v in dict_current_photo_format.items():
            photo_sum = int(v["Количество"])
            printed_sum = v["Количество напечатанных"]
            if v["Напечатанно"] == "not printed":
                img_absolute_path = k
                title = str(v["Формат фото"]) + str(v["Количество"]) + " " + str(v["Фото ребенка"]) + " " + str(v["Класс"])
                printed_sum += 1
                v["Количество напечатанных"] = printed_sum
                if printed_sum == photo_sum:
                    v["Напечатанно"] = "printed"
                dict_current_photo_format[k] = v
                return img_absolute_path, title
        return None

    def new_image(self, size):
        size_settings = self.sizes_foto[size]
        return Image.new(size_settings["ColorSpace"], size_settings["Size"], size_settings["Color"])

# Функции конвертирования из psd в png и вращения фотографии
    def convert_psd_to_png(self):
        self.messages_what_work.emit("Конвертирую файлы в png")
        count = 0
        for object_path, files in self.dict_of_psd_files.items():
            current_object = os.path.split(object_path)[1]
            path_for_png = self.dir_for_png + os.sep + current_object
            self.check_exists_dir(path_for_png)
            for file_name, attribute in files.items():
                # получаем имя png файла, включая путь
                png_file_name = self.change_format_file_name(file_name, path_for_png)
                psd_file = PSDImage.open(object_path + os.sep + file_name)  # открываем psd файл
                img = psd_file.composite()  # сливаем слои, и получаем изображение типа PIL
                # из имени файла, получаем формат фотографии
                photo_format = attribute["Вид фото"] + "_" + attribute["Формат фото"] + "_"  # формат фотографии
                children_photo = attribute["Фото ребенка"]  # номер фотографии ребенка
                photo_summ = attribute["Количество"]  # получаем колиство изделий с кадра
                group = attribute["Класс"]
                ratio = self.get_ratio(file_name)  # получаем соотношения сторон
                self.add_to_dict_of_photo_png(photo_format, photo_summ, png_file_name,
                                              current_object, children_photo, group)
                if photo_format in self.flat_photo_name_list:
                    cropped_img = self.crop_image(img, ratio)
                    resized_img = self.resize_image(cropped_img, photo_format)
                    img_for_save = self.rotate_image(resized_img, photo_format)
                elif photo_format in self.stereo_photo_name_list:
                    cropped_img = self.crop_image(img, ratio)
                    resized_img = self.resize_image(cropped_img, photo_format)
                    img_for_save = self.rotate_image(resized_img, photo_format)
                elif photo_format in self.wall_calendar_name_list:
                    cropped_img = self.crop_image(img, ratio)
                    resized_img = self.resize_image(cropped_img, photo_format)
                    png_wall_image = self.wall_calendar_image(resized_img)
                    img_for_save = self.rotate_image(png_wall_image, photo_format)
                elif photo_format in self.cup_name_list:
                    png_img = self.convert_cup_image(img, ratio)
                    img_for_save = self.rotate_image(png_img, photo_format)
                elif photo_format in self.badge_name_list:
                    img_for_save = self.convert_badge_image(img, ratio)
                else:
                    pass
                self.save_png_image(img_for_save, png_file_name)
                count += 1
                self.count_converted_photo.emit(count)
                del psd_file
                del img

    def add_to_dict_of_photo_png(self, photo_format, photo_summ, png_file_name, current_object, children_photo, group):
        """ изменяем словарь выбранного формата, добавляем в него фотографию,
        вида {абсолютный путь к png фото : [photo_summ, 0, 'not printed', photo_format, children_photo,
        current_object]}
        где:
        photo_summ - количество изделий, которое необходимо сделать
        0 - количество изделий, которое уже было добавлено на лист, для печати
        'not printed' - указывает на то, что фотография еще не была добавлена, на лист для печати
        photo_format - формат фотографии, вида о_10х15_
        children_photo - имя фотографии ребенка
        current_object - Объект к которому принадлежит изделие
        """
        dict_png_of_current_photo_format = self.dict_of_photo_png[photo_format]
        dict_png_of_current_photo_format[png_file_name] = {"Количество": photo_summ,
                                                           "Количество напечатанных": 0,
                                                           "Напечатанно": 'not printed',
                                                           "Формат фото": photo_format,
                                                           "Фото ребенка": children_photo,
                                                           "Класс": group,
                                                           "Объект": current_object}
        self.dict_of_photo_png[photo_format] = dict_png_of_current_photo_format

    def crop_image(self, img, ratio):
        """Образаем фотографию с необходимым соотношение ширины к длинне"""
        calc_height = img.width * ratio
        calc_width = img.height * ratio
        img_height = img.height
        img_width = img.width
        if img_width > img_height:   # опеределяем горизонтальную фотографию
            if calc_width > img_width:
                new_height = round(img_width / ratio)
                upper = round((img_height - new_height) / 2)
                left = 0
                lower = img_height - upper
                right = img_width
            else:
                new_width = round(img_height * ratio)
                left = round((img_width - new_width) / 2)
                upper = 0
                right = img_width - left
                lower = img_height
        elif img_width < img_height:  # опеределяем вертикальную фотографию
            if calc_height > img_height:
                new_width = round(img_height / ratio)
                left = round((img_width - new_width) / 2)
                upper = 0
                right = img_width - left
                lower = img_height
            else:
                new_height = round(img_width * ratio)
                upper = round((img_height - new_height) / 2)
                left = 0
                lower = img_height - upper
                right = img_width
        return img.crop((left, upper, right, lower))

    def rotate_image(self, img, photo_format):
        """Разворачиваем фотографию на 90 градусов
        только в том случае, если ширина больше высоты"""
        if img.width > img.height:
            if self.rotate_dict[photo_format][0] != 0:
                return img.transpose(self.rotate_dict[photo_format][0])
        elif img.width < img.height:
            if self.rotate_dict[photo_format][1] != 0:
                return img.transpose(self.rotate_dict[photo_format][1])
        return img

    def resize_image(self, img, photo_format):
        """Меняем размер изображений, размеры хранятся в словаре
        dict_of_size, в качестве параметров передается PIL изображение и формат фотографии"""
        if img.width > img.height:   # опеределяем горизонтальную фотографию
            new_width = self.dict_of_sizes[photo_format][0]
            new_height = self.dict_of_sizes[photo_format][1]
        elif img.width < img.height:  # опеределяем вертикальную фотографию
            new_width = self.dict_of_sizes[photo_format][1]
            new_height = self.dict_of_sizes[photo_format][0]
        return img.resize((new_width, new_height))

    def change_format_file_name(self, file_name, path_for_png):
        new_file_name = path_for_png + os.sep + file_name[0: -4] + '.png'
        return new_file_name

    def save_png_image(self, img, png_file_name):
        try:
            img.save(png_file_name, compress_level=0, dpi=self.dpi)
        except Exception as e:
            print(e)

    def get_ratio(self, file_name):
        photo_size = file_name.split("_")[0] + "_" + file_name.split("_")[1] + "_"
        return self.ratio_dict[photo_size]

    def convert_photo_image(self, img, ratio):
        pass

    def wall_calendar_image(self, img):
        """Конвертируем настенный календарь в пнг, размываем фото для нижнего слоя,
        и вставляем сверху фото, меньшего размера, приблизительно 5-7мм рамки, нижнего слоя"""
        front_img = img.resize((round(img.width / 1.0505), round(img.height / 1.0505))).convert('RGBA')
        blured_img = img.filter(ImageFilter.GaussianBlur(radius=35)).convert('RGBA')
        left = round((blured_img.width - front_img.width) / 2)
        top = round((blured_img.height - front_img.height) / 2)
        blured_img.alpha_composite(front_img, (left, top))
        return blured_img

    def convert_cup_image(self, img, ratio):
        return img

    def convert_badge_image(self, img, ratio):
        new_width = round(img.width * ratio)
        new_height = round(img.height * ratio)
        return img.resize((new_width, new_height))
