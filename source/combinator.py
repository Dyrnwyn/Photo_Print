import os
import re
from psd_tools import PSDImage
from PIL import ImageFilter, Image, ImageDraw, ImageFont
from PyQt5 import QtCore


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
    count_converted_photo = QtCore.pyqtSignal(int)
    # список имен плосских фотографий
    flat_photo_name_list = ("п_10х15_", "п_15х20_", "п_20х30_", "п_магнит_", "п_магнит 10х15_")
    # список имен плосских фотографий
    stereo_photo_name_list = ("о_10х15_", "о_15х20_", "о_20х30_", "о_магнит 10х15_", "о_календарик 7х10_")
    # список имен плосских фотографий
    wall_calendar_name_list = ("п_Настенный календарь_", "о_Настенный календарь_")
    badge_name_list = ("_Брелок 58_", "_Зеркало 75_", "_Значок 75_", "_Значок 100_", "_Значок 158_", "_Копилка 158_")
    cup_name_list = ("_Кружка-термос с крышкой_")
    dpi = (300, 300)
    dict_of_psd_files = {}
    dir_for_png = 'C:\\Объекты\\print_photo_png'
    dir_to_print = 'C:\\Объекты\\print_photo_png\\В печать\\'

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        self.convert_psd_to_png()
        self.add_photo_to_61x32_main()

    def set_var(self, dpi, psd_dict, dir_for_png, dir_to_print):
        """Устанавливаем значения переменных
        разрешение фотографии dpi, словарь psd файлов, путь к папке для еконвертации в png"""
        self.photo_dpi = dpi
        self.dict_of_psd_files = psd_dict
        self.dir_for_png = dir_for_png
        self.dir_to_print = dir_to_print

    def get_font(self):
        try:
            font = ImageFont.truetype("Font\\CalibriBold.ttf", 50)
            return font
        except Exception as e:
            print(e)

    def draw_title(self, img, text, point):
        font = self.get_font()
        draw_text = ImageDraw.Draw(img)
        draw_text.text(point, text, font=font, fill=(0, 0, 0))
        return img

    def add_photo_to_61x32_main(self):
        self.add_wallpaper_to_61x32()

    def add_flat_photo_to_a4(self):
        pass

    def add_stereo_photo_to_a4(self):
        pass

    def add_wallpaper_to_61x32(self):
        wallpaper_point = [[(60, 60), (240, 10)], [(2890, 60), (3640, 10)], [(5670, 60), (5700, 10)]]
        count_photo_on_61x32 = 0
        while self.get_availability_of_photo("п_Настенный календарь_"):
            if count_photo_on_61x32 == 0:
                image_61x32 = self.new_image_61x32()
            walpaper_img, title = self.get_not_printed_photo_with_title("п_Настенный календарь_")
            img = Image.open(walpaper_img)
            image_61x32.paste(img, wallpaper_point[count_photo_on_61x32][0])
            image_61x32 = self.draw_title(image_61x32, title, wallpaper_point[count_photo_on_61x32][1])
            count_photo_on_61x32 += 1
            if count_photo_on_61x32 == 2:
                self.save_png_image(image_61x32, self.dir_to_print + "1.png")

    def add_photo_to_11x32(self):
        pass

    def get_availability_of_photo(self, photo_format):
        dict_current_photo_format = self.dict_of_photo_png[photo_format]
        for k, v in dict_current_photo_format.items():
            if v[2] == "not printed":
                return True
        return False

    def get_not_printed_photo_with_title(self, photo_format):
        dict_current_photo_format = self.dict_of_photo_png[photo_format]
        for k, v in dict_current_photo_format.items():
            photo_summ = int(v[0])
            printed_summ = v[1]
            if v[2] == "not printed":
                img_absolute_path = k
                title = str(v[5]) + " " + str(v[3]) + " " + str(v[0]) + " " + str(v[4])
                printed_summ += 1
                v[1] = printed_summ
                if printed_summ == photo_summ:
                    v[2] = "printed"
                dict_current_photo_format[k] = v
                return img_absolute_path, title
        return None

    def new_image_20x30(self):
        """Создание изображения размерами 20х30 см"""
        return Image.new('RGB', (2657, 3780), color=(255, 255, 255))

    def new_image_61x32(self):
        """Создание изображения размерами 61х32 см"""
        return Image.new('RGB', (7205, 3780), color=(255, 255, 255))

    def new_image_11x32(self):
        """Создаем изображение размерами 11х32 см"""
        return Image.new('RGB', (1299, 3780), color=(255, 255, 255))

# Функции конвертирования из psd в png и вращения фотографии
    def convert_psd_to_png(self):
        count = 0
        for k, v in self.dict_of_psd_files.items():
            current_object = os.path.split(k)[1]
            path_for_png = self.dir_for_png + '\\' + current_object
            for file in v:
                psd_file = PSDImage.open(k + '\\' + file)  # открываем psd файл
                img = psd_file.composite()  # сливаем слои, и получаем изображение типа PIL
                # из имени файла, получаем формат фотографии
                photo_format = file.split("_")[0] + "_" + file.split("_")[1] + "_"  # формат фотографии
                children_photo = file.split("_")[3]  # номер фотографии ребенка
                photo_summ = file.split("_")[4]  # получаем колиство изделий с кадра
                ratio = self.get_ratio(file)  # получаем соотношения сторон
                png_file_name = self.change_format_file_name(file, path_for_png)  # получаем имя png файла, включая путь
                self.add_to_dict_of_photo_png(photo_format, photo_summ, png_file_name, current_object, children_photo)
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

    def add_to_dict_of_photo_png(self, photo_format, photo_summ, png_file_name, current_object, children_photo):
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
        dict_png_of_current_photo_format[png_file_name] = [photo_summ, 0, 'not printed',
                                                           photo_format, children_photo, current_object]
        self.dict_of_photo_png[photo_format] = dict_png_of_current_photo_format

    def crop_image(self, img, ratio):
        """Образаем фотографию с необходимым соотношение ширины к длинне"""
        if img.width > img.height:   # опеределяем горизонтальную фотографию
            new_width = round(img.height * ratio)
            left = round((img.width - new_width) / 2)
            upper = 0
            right = img.width - left
            lower = img.height
        elif img.width < img.height:  # опеределяем вертикальную фотографию
            new_width = round(img.height / ratio)
            left = round((img.width - new_width) / 2)
            upper = 0
            right = img.width - left
            lower = img.height
        return img.crop((left, upper, right, lower))

    def rotate_image(self, img, photo_format):
        """Разворачиваем фотографию на 90 градусов
        только в том случае, если ширина больше высоты"""
        if img.width > img.height:
            return img.transpose(self.rotate_dict[photo_format][0])
        elif img.width < img.height:
            return img.transpose(self.rotate_dict[photo_format][1])

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
        new_file_name = path_for_png + '\\' + file_name[0: -4] + '.png'
        return new_file_name

    def save_png_image(self, img, png_file_name):
        try:
            img.save(png_file_name, compress_level=0, dpi=self.photo_dpi)
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
