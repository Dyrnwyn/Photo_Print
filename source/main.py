import sys
import os
import window
from PyQt5 import QtWidgets, QtCore
from combinator import search_file, ThreadForConvert


class MainApp(QtWidgets.QMainWindow, window.Ui_MainWindow):
    dir_for_png = 'C:\\Объекты\\print_photo_png'
    name_dir_to_print = 'В печать'
    progress_bar_maximum = 0
    dict_of_psd_files = {}
    photo_dpi = (300, 300)
    row_count = 0  # счетчик строк, заполненных в таблице
    count_photo = {"п_10х15_": 0,  # Словарь подсчета количества печатаемых фото
                   "п_15х20_": 0,
                   "п_20х30_": 0,
                   "п_Настенный календарь_": 0,
                   "п_магнит_": 0,
                   "п_магнит 10х15_": 0,
                   "_Брелок 58_": 0,
                   "_Зеркало 75_": 0,
                   "_Значок 75_": 0,
                   "_Значок 100_": 0,
                   "_Значок 158_": 0,
                   "_Копилка 158_": 0,
                   "_Кружка-термос с крышкой_": 0, }

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.progressBar.setValue(0)
        self.addFileButton.clicked.connect(self.add_file)
        self.addDirectoryButton.clicked.connect(self.add_file_from_folder)
        self.composeButton.clicked.connect(self.compose_files)
        self.clearButton.clicked.connect(self.clear_selected_photo)
        self.tableWidget.setRowCount(500)  # устанавливаем количество строк в 500
        self.convert_psd_to_png_thread = ThreadForConvert()
        self.convert_psd_to_png_thread.started.connect(self.on_start_convert)
        self.convert_psd_to_png_thread.finished.connect(self.on_finished_convert)
        self.convert_psd_to_png_thread.count_converted_photo.connect(self.on_change_convert, QtCore.Qt.QueuedConnection)

    def compose_files(self):
        self.dict_of_psd_files = self.get_list_of_psd_from_table()
        self.create_object_dir(self.dict_of_psd_files)
        self.convert_psd_to_png()

    def on_change_convert(self, v):
        """Функция вызываемая во время процесса конвертации"""
        self.progressBar.setValue(v)

    def on_start_convert(self):
        """Функция вызываемая при начале процесса конвертации"""
        self.composeButton.setDisabled(True)
        self.progressBar.setMaximum(progress_bar_maximum)

    def on_finished_convert(self):
        """Функция вызываемая по завершении процесса конвертации"""
        self.composeButton.setDisabled(False)

    def convert_psd_to_png(self):
        self.convert_psd_to_png_thread.set_var(self.photo_dpi, self.dict_of_psd_files, self.dir_for_png,
                                               self.dir_for_png + '\\' + self.name_dir_to_print)
        self.convert_psd_to_png_thread.start()

    def zeroing_count_photo(self):
        """Функция обнуления количества изделий в словаре"""
        for k, v in self.count_photo.items():
            self.count_photo[k] = 0

    def clear_selected_photo(self):
        """Очистка таблицы, обнуление счетчика поля
        обнуление количества фотографий, запись количества обнуленных фото в label"""
        self.tableWidget.clearContents()
        self.row_count = 0
        self.zeroing_count_photo()
        self.add_amount_of_photo_to_label()

    def count_amount_of_photo(self, file_name):
        """Подсчет количества фотографий каждого формата"""
        for k, v in self.count_photo.items():   # находим в файле количество в печать
            if k in file_name:              # и прибавляем к общему количеству данного формата фотографии
                amount = int(file_name.split("_")[4])
                v += amount
                self.count_photo[k] = v

    def add_amount_of_photo_to_label(self):
        """Запись количества фотографий в label"""
        _translate = QtCore.QCoreApplication.translate
        self.label_10x15.setText(_translate("MainWindow", "10x15: " + str(self.count_photo["п_10х15_"])))
        self.label_15x20.setText(_translate("MainWindow", "15x20: " + str(self.count_photo["п_15х20_"])))
        self.label_20x30.setText(_translate("MainWindow", "20x30: " + str(self.count_photo["п_20х30_"])))
        self.label_WallCalendar.setText(_translate("MainWindow", "Настенный календарь: " + str(
                                                   self.count_photo["п_Настенный календарь_"])))
        self.label_magnit.setText(_translate("MainWindow", "магнит: " + str(self.count_photo["п_магнит_"])))
        self.label_magnit_10x15.setText(_translate("MainWindow", "магнит 10х15: " + str(self.count_photo[
                                                   "п_магнит 10х15_"])))
        self.label_brelok58.setText(_translate("MainWindow", "Брелок 58: " + str(self.count_photo["_Брелок 58_"])))
        self.label_zerkalo75.setText(_translate("MainWindow", "Зеркало 75: " + str(self.count_photo["_Зеркало 75_"])))
        self.label_znaciok75.setText(_translate("MainWindow", "Значок 75: " + str(self.count_photo["_Значок 75_"])))
        self.label_znaciok100.setText(_translate("MainWindow", "Значок 100: " + str(self.count_photo["_Значок 100_"])))
        self.label_znaciok158.setText(_translate("MainWindow", "Значок 158: " + str(self.count_photo["_Значок 158_"])))
        self.label_kopilka158.setText(_translate("MainWindow", "Копилка 158: " + str(self.count_photo[
                                                 "_Копилка 158_"])))
        self.label_Cup.setText(_translate("MainWindow", "Кружка-термос с крышкой: " + str(self.count_photo[
                                          "_Кружка-термос с крышкой_"])))

    def add_psd_files_to_table(self, file, file_object, directory):
        """Функция добавления файла, имени обьекта и директории в таблицу.
        В функцию передается имя файла, имя обьекта, директория файла"""
        self.tableWidget.setItem(self.row_count, 0, QtWidgets.QTableWidgetItem(file))
        self.tableWidget.setItem(self.row_count, 1, QtWidgets.QTableWidgetItem(file_object))
        self.tableWidget.setItem(self.row_count, 2, QtWidgets.QTableWidgetItem(directory))
        self.count_amount_of_photo(file)
        self.row_count += 1

    def add_file_from_folder(self):
        """Добавляем список psd файлов в таблицу"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        if directory != '':
            list_of_psd_files = search_file("psd", directory)
            file_object = os.path.split(directory)[1]  # имя объекта к которому принадлежит файл
            for file in list_of_psd_files:
                self.add_psd_files_to_table(file, file_object, directory)
            self.tableWidget.resizeColumnsToContents()
            self.add_amount_of_photo_to_label()
        else:
            pass

    def add_file(self):
        dialogObject = QtWidgets.QFileDialog(self, "Добавить файл", "", "Файлы изображений (*.psd)")
        dialogObject.setFileMode(3)
        dialogObject.setViewMode(1)
        dialogObject.exec()
        files = dialogObject.selectedFiles()
        if files != []:
            for file in files:
                directory = os.path.split(file)[0]
                file_name = os.path.split(file)[1]
                file_object = os.path.split(directory)[1]
                self.add_psd_files_to_table(file_name, file_object, directory)
            self.tableWidget.resizeColumnsToContents()
            self.add_amount_of_photo_to_label()
        else:
            pass

    def create_object_dir(self, dict_of_psd_files):
        """Создаем отдельные папки для каждого обьекта
        чтобы сконвертировать туда png. Основная папка
        описана в переменной dir_for_png"""
        try:
            os.mkdir(self.dir_for_png)
            os.mkdir(self.dir_for_png + '\\' + self.name_dir_to_print)
        except Exception as e:
            pass
        for k, v in dict_of_psd_files.items():
            directory_object = self.dir_for_png + '\\' + os.path.split(k)[1]
            try:
                os.mkdir(directory_object)
            except Exception as e:
                print(e)

    def get_list_of_psd_from_table(self):   # создаем словарь на основании заполненной таблицы
        count_row = 0                       # вида {путь к файлу: [список файлов]}
        dict_of_psd_file = {}
        global progress_bar_maximum
        while self.tableWidget.item(count_row, 0) is not None:
            path_to_file = self.tableWidget.item(count_row, 2).text()
            if path_to_file not in dict_of_psd_file:
                dict_of_psd_file[path_to_file] = []
                list_of_files = dict_of_psd_file[path_to_file]
                list_of_files.append(self.tableWidget.item(count_row, 0).text())
            else:
                list_of_files = dict_of_psd_file[path_to_file]
                list_of_files.append(self.tableWidget.item(count_row, 0).text())
            count_row += 1
        progress_bar_maximum = count_row  # получаем количество фотографий для индикатора хода процесса
        return dict_of_psd_file


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
