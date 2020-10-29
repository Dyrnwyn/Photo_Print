import os
import re
from psd_tools import PSDImage
from PIL import ImageFilter
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
    count_converted_photo = QtCore.pyqtSignal(int)
    # список имен плосских фотографий
    flat_photo_name_list = ("п_10х15_", "п_15х20_", "п_20х30_", "п_магнит_", "п_магнит 10х15_")
    # список имен плосских фотографий
    stereo_photo_name_list = ("о_10х15_", "о_15х20_", "о_20х30_", "о_магнит 10х15_", "о_календарик 7х10_")
    # список имен плосских фотографий
    wall_calendar_name_list = ("п_Настенный календарь_", "о_Настенный календарь_")
    badge_name_list = ("_Брелок 58_", "_Зеркало 75_", "_Значок 75_", "_Значок 100_", "_Значок 158_", "_Копилка 158_")
    cup_name_list = ("Кружка-термос с крышкой")
    dpi = (300, 300)
    dict_of_psd_files = {}
    dir_for_png = 'C:\\Объекты\\print_photo_png'

    def __init__(self):
        QtCore.QThread.__init__(self)

    def set_var(self, dpi, psd_dict, dir_for_png):
        """Устанавливаем значения переменных
        разрешение фотографии dpi, словарь psd файлов, путь к папке для еконвертации в png"""
        self.photo_dpi = dpi
        self.dict_of_psd_files = psd_dict
        self.dir_for_png = dir_for_png

    def crop_image(self, img, ratio):
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
        print((left, upper, right, lower))
        return img.crop((left, upper, right, lower))

    def resize_image(self, img, photo_format):
        if img.width > img.height:   # опеределяем горизонтальную фотографию
            new_width = self.dict_of_sizes[photo_format][0]
            new_height = self.dict_of_sizes[photo_format][1]
        elif img.width < img.height:  # опеределяем вертикальную фотографию
            new_width = self.dict_of_sizes[photo_format][1]
            new_height = self.dict_of_sizes[photo_format][0]
        return img.resize((new_width, new_height))

    def run(self):
        count = 0
        for k, v in self.dict_of_psd_files.items():
            path_for_png = self.dir_for_png + '\\' + os.path.split(k)[1]
            for file in v:
                psd_file = PSDImage.open(k + '\\' + file)
                img = psd_file.composite()
                photo_format = file.split("_")[0] + "_" + file.split("_")[1] + "_"
                ratio = self.get_ratio(file)
                if photo_format in self.flat_photo_name_list:
                    cropped_img = self.crop_image(img, ratio)
                    img_for_save = self.resize_image(cropped_img, photo_format)
                elif photo_format in self.stereo_photo_name_list:
                    pass
                elif photo_format in self.wall_calendar_name_list:
                    cropped_img = self.crop_image(img, ratio)
                    resized_img = self.resize_image(cropped_img, photo_format)
                    img_for_save = self.wall_calendar_image(resized_img)
                elif photo_format in self.cup_name_list:
                    img_for_save = self.convert_cup_image(img, ratio)
                elif photo_format in self.badge_name_list:
                    img_for_save = self.convert_badge_image(img, ratio)
                else:
                    pass
                try:
                    img_for_save.save(path_for_png + '\\' + file[0: -4] + '.png', compress_level=0, dpi=self.photo_dpi)
                except Exception:
                    pass
                count += 1
                self.count_converted_photo.emit(count)

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
