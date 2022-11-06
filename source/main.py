import sys
import os
import window
import choiceDialog
from PyQt5 import QtWidgets, QtCore
from combinator import search_file, ThreadForConvert
import json


class dialogChoiseFoto(QtWidgets.QDialog, choiceDialog.Ui_Dialog):
    """docstring for dialog_choise_foto"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class MainApp(QtWidgets.QMainWindow, window.Ui_MainWindow):
    settings = {"п_10х15_": '',
                "п_15х20_": '',
                "п_20х30_": '',
                "п_магнит_": '',
                "п_магнит 10х15_": '',
                "п_Настенный календарь_": '',
                "Директория объектов": '',
                "Директория временных файлов": '',
                "Шрифт": ''}
    dir_for_png = settings["Директория временных файлов"]
    dir_to_print = settings["Директория объектов"]
    progress_bar_maximum = 0
    dict_of_psd_files = {}
    photo_dpi = (300, 300)
    row_count = 0  # счетчик строк, заполненных в таблице
    list_to_print_on_210x297 = []
    list_to_print_on_610x320 = []
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
        self.change_list_to_default()
        self.addFileButton.clicked.connect(self.add_file)
        self.addDirectoryButton.clicked.connect(self.add_file_from_folder)
        self.composeButton.clicked.connect(self.compose_files)
        self.clearButton.clicked.connect(self.clear_selected_photo)
        self.toolButton_folderForFinishFoto.clicked.connect(self.choise_folder_for_finished_foto)
        self.toolButton_tmpFolder.clicked.connect(self.choise_tmp_folder)
        self.toolButton_Font.clicked.connect(self.choise_font)
        self.tableWidget.setRowCount(500)  # устанавливаем количество строк в 500
        self.tableWidget.doubleClicked.connect(self.choise_foto_size)
        self.convert_psd_to_png_thread = ThreadForConvert()
        self.convert_psd_to_png_thread.started.connect(self.on_start_convert)
        self.convert_psd_to_png_thread.finished.connect(self.on_finished_convert)
        self.convert_psd_to_png_thread.count_converted_photo.connect(self.on_change_convert, QtCore.Qt.QueuedConnection)
        self.convert_psd_to_png_thread.messages_what_work.connect(self.on_change_convert_set_label,
                                                                  QtCore.Qt.QueuedConnection)
        self.setPushButtonSave.clicked.connect(self.save_settings)
        self.name_settings_directory = 'Настройки'
        self.settings_directory = os.path.dirname(__file__) + os.sep + self.name_settings_directory + os.sep
        if not os.path.exists(self.settings_directory):
            os.mkdir(self.settings_directory)
            self.save_settings()
        self.load_settings()

    def save_settings(self):
        for k, v in self.settings.items():
            self.settings[k] = '610x320'
        if self.set_radioButton_10x15_210x297.isChecked():
            self.settings["п_10х15_"] = '210x297'
        if self.set_radioButton_15x20_210x297.isChecked():
            self.settings["п_15х20_"] = '210x297'
        if self.set_radioButton_20x30_210x297.isChecked():
            self.settings["п_20х30_"] = '210x297'
        if self.set_radioButton_wallCalendar_210x297.isChecked():
            self.settings["п_Настенный календарь_"] = '210x297'
        if self.set_radioButton_magnit_210x297.isChecked():
            self.settings["п_магнит_"] = '210x297'
        if self.set_radioButton_magnit10x15_210x297.isChecked():
            self.settings["п_магнит 10х15_"] = '210x297'
        if self.lineeditFolderFinishedFoto.text() == '':
            self.settings["Директория объектов"] = self.lineeditFolderFinishedFoto.placeholderText()
        else:
            self.settings["Директория объектов"] = self.lineeditFolderFinishedFoto.text()
        if self.lineeditTmpFolder.text() == '':
            self.settings["Директория временных файлов"] = self.lineeditTmpFolder.placeholderText()
        else:
            self.settings["Директория временных файлов"] = self.lineeditTmpFolder.text()
        if self.lineeditFont.text() == '':
            self.settings["Шрифт"] = self.lineeditFont.placeholderText()
        else:
            self.settings["Шрифт"] = self.lineeditFont.text()
        json_txt = json.dumps(self.settings)
        settings_file = open(self.settings_directory + 'settings.conf', 'w')
        settings_file.write(json_txt)
        settings_file.close()
        self.change_list_to_print_from_settings()

    def load_settings(self):
        json_text = ''
        if not os.path.isfile(self.settings_directory + 'settings.conf'):
            self.save_settings()
        settings_file = open(self.settings_directory + 'settings.conf', 'r')
        json_text = settings_file.read()
        settings_file.close()
        error_in_settings = False
        if json_text != '':
            settings = json.loads(json_text)
            for k, v in self.settings.items():
                 self.settings[k] = settings[k]
            if self.settings["п_10х15_"] == '210x297':
                self.set_radioButton_10x15_210x297.setChecked(True)
            else:
                self.set_radioButton_10x15_610x320.setChecked(True)
            if self.settings["п_15х20_"] == '210x297':
                self.set_radioButton_15x20_210x297.setChecked(True)
            else:
                self.set_radioButton_15x20_610x320.setChecked(True)
            if self.settings["п_20х30_"] == '210x297':
                self.set_radioButton_20x30_210x297.setChecked(True)
            else:
                self.set_radioButton_20x30_610x320.setChecked(True)
            if self.settings["п_Настенный календарь_"] == '210x297':
                self.set_radioButton_wallCalendar_210x297.setChecked(True)
            else:
                self.set_radioButton_wallCalendar_610x320.setChecked(True)
            if self.settings["п_магнит_"] == '210x297':
                self.set_radioButton_magnit_210x297.setChecked(True)
            else:
                self.set_radioButton_magnit_610x320.setChecked(True)
            if self.settings["п_магнит 10х15_"] == '210x297':
                self.set_radioButton_magnit10x15_210x297.setChecked(True)
            else:
                self.set_radioButton_magnit10x15_610x320.setChecked(True)
            self.lineeditFolderFinishedFoto.setText(self.settings["Директория объектов"])
            self.lineeditTmpFolder.setText(self.settings["Директория временных файлов"])
            self.lineeditFont.setText(self.settings["Шрифт"])
            if error_in_settings:
                self.show_message_box("Ошибка файла настроек",
                                      "В файле настроек обнаружена ошибка, необходимо проверить настройки")
        self.change_list_to_print_from_settings()

    @staticmethod
    def show_message_box(title_text, message_text):
        msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                        title_text, message_text,
                                        buttons=QtWidgets.QMessageBox.Ok)
        msg_box.exec()

    def change_list_to_print_from_settings(self):
        self.change_list_to_default()
        for k, v in self.settings.items():
            if v == "210x297":
                self.list_to_print_on_210x297.append(k)
            elif v == "610x320":
                self.list_to_print_on_610x320.append(k)

    def change_list_to_default(self):
        self.list_to_print_on_210x297 = ["_Брелок 58_", "_Зеркало 75_", "_Значок 75_", "_Значок 100_",
                                         "_Значок 158_", "_Копилка 158_", "_Кружка-термос с крышкой_"]
        self.list_to_print_on_610x320 = []

    def keyReleaseEvent(self, e):
        if self.focusWidget() == self.tableWidget:
            if e.key() == QtCore.Qt.Key_Delete:
                self.pressedButtonOnTable()

    def compose_files(self):
        self.dict_of_psd_files = self.get_list_of_psd_from_table()
        self.create_object_dir(self.dict_of_psd_files)
        self.convert_psd_to_png()

    def on_change_convert(self, v):
        """Функция вызываемая во время процесса конвертации"""
        self.progressBar.setValue(v)

    def on_change_convert_set_label(self, txt):
        self.progressBarLabel.setText(txt)

    def on_start_convert(self):
        """Функция вызываемая при начале процесса конвертации"""
        self.composeButton.setDisabled(True)
        self.progressBar.setMaximum(progress_bar_maximum)

    def on_finished_convert(self):
        """Функция вызываемая по завершении процесса конвертации"""
        self.composeButton.setDisabled(False)

    def convert_psd_to_png(self):
        """Запускаем поток конвертирования и формирования файлов для печати
        Сначала устанавливаем переменные, далее запускаем поток"""
        self.convert_psd_to_png_thread.set_var(self.photo_dpi, self.dict_of_psd_files,
                                               self.settings['Директория временных файлов'],
                                               self.settings['Директория объектов'], self.list_to_print_on_210x297,
                                               self.list_to_print_on_610x320,
                                               self.settings['Шрифт'],
                                               self.get_object())
        self.convert_psd_to_png_thread.start()

    def get_object(self):
        return self.tableWidget.item(0, 3).text()
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
        try:
            vid_foto = file.split("_")[0]
            foto_type = file.split("_")[1]
            sum_foto = file.split("_")[4]
        except Exception:
            vid_foto = '"п'
            foto_type = "10x15"
            sum_foto = "1"
        if vid_foto != "о":
            self.tableWidget.setItem(self.row_count, 0, QtWidgets.QTableWidgetItem(file))
            self.tableWidget.setItem(self.row_count, 1, QtWidgets.QTableWidgetItem(foto_type))
            self.tableWidget.setItem(self.row_count, 2, QtWidgets.QTableWidgetItem(sum_foto))
            self.tableWidget.setItem(self.row_count, 3, QtWidgets.QTableWidgetItem(file_object))
            self.tableWidget.setItem(self.row_count, 4, QtWidgets.QTableWidgetItem(directory))
            self.count_amount_of_photo(file)
            self.row_count += 1

    def get_list_of_psd_from_table(self):   # создаем словарь на основании заполненной таблицы
        count_row = 0                       # вида {путь к файлу: [список файлов]}
        dict_of_psd_file = {}
        global progress_bar_maximum
        while self.tableWidget.item(count_row, 0) is not None:
            path_to_file = self.tableWidget.item(count_row, 4).text()
            file_name = self.tableWidget.item(count_row, 0).text()
            foto_format = self.tableWidget.item(count_row, 1).text()
            sum_foto = self.tableWidget.item(count_row, 2).text()
            object_of_foto = self.tableWidget.item(count_row, 3).text()
            try:
                group = file_name.split("_")[5]
                vid_foto = file_name.split("_")[0]
                children_foto = file_name.split("_")[3]
            except Exception:
                group = "1"
                vid_foto = "п"
                children_foto = "0000"
            if path_to_file not in dict_of_psd_file:
                dict_of_psd_file[path_to_file] = {}
            file_dict = dict_of_psd_file[path_to_file]
            file_dict[file_name] = {"Формат фото": foto_format, "Количество": sum_foto,
                                    "Объект": object_of_foto, "Класс": group, "Вид фото": vid_foto,
                                    "Фото ребенка": children_foto}
            count_row += 1
        progress_bar_maximum = count_row  # получаем количество фотографий для индикатора хода процесса
        return dict_of_psd_file

    def choise_foto_size(self):
        col = self.tableWidget.currentColumn()
        row = self.tableWidget.currentRow()
        if col == 1:
            dialog = dialogChoiseFoto()
            dialog.exec()
            cur_item = dialog.listWidget.currentItem()
            if cur_item is not None:
                foto_format = dialog.listWidget.currentItem().text()
                self.tableWidget.setItem(row, col, QtWidgets.QTableWidgetItem(foto_format))

    def create_object_dir(self, dict_of_psd_files):
        """Создаем отдельные папки для каждого обьекта
        чтобы сконвертировать туда png. Основная папка
        описана в переменной dir_for_png"""
        try:
            os.mkdir(self.dir_for_png)
            os.mkdir(self.dir_for_png + os.sep + self.name_dir_to_print)
        except Exception:
            pass
        for k, v in dict_of_psd_files.items():
            directory_object = self.dir_for_png + os.sep + os.path.split(k)[1]
            try:
                os.mkdir(directory_object)
            except Exception:
                pass

    def add_file_from_folder(self):
        """Добавляем список psd файлов в таблицу"""
        directory = self.choise_folder()
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
        """Добавление отдельных psd файлов в таблицу"""
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

    def pressedButtonOnTable(self):
        self.removeRowFromTable()

    def removeRowFromTable(self):
        current_row = self.tableWidget.currentRow()
        self.tableWidget.removeRow(current_row)
        self.tableWidget.setRowCount(500)

    def choise_folder_for_finished_foto(self):
        self.lineeditFolderFinishedFoto.setText(self.choise_folder())

    def choise_tmp_folder(self):
        self.lineeditTmpFolder.setText(self.choise_folder())

    def choise_folder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        return str(directory)

    def choise_font(self):
        font_file = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите шрифт")
        self.lineeditFont.setText(str(font_file[0]))

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
