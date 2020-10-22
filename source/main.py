import sys
from PyQt5 import QtWidgets, QtCore
import window
import combinator
import os
import psd-tools


class MainApp(QtWidgets.QMainWindow, window.Ui_MainWindow):
    dir_for_png = 'C:\\Объекты\\print_photo_png'
    row_count = 0 # счетчик строк, заполненных в таблице
    count_photo = { "п_10х15_": 0, #Словарь подсчета количества печатаемых фото
                    "п_15х20_": 0,
                    "п_20х30_": 0, 
                    "п_Настенный календарь_": 0, 
                    "п_магнит_": 0, 
                    "п_магнит 10х15_": 0, 
                    "Брелок 58": 0, 
                    "Зеркало 75": 0, 
                    "Значок 158": 0, 
                    "Копилка 158": 0, 
                    "Кружка-термос с крышкой": 0, }
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addFileButton.clicked.connect(self.add_file)
        self.addDirectoryButton.clicked.connect(self.add_file_from_folder)
        self.composeButton.clicked.connect(self.compose_files)
        self.progressBar.setVisible(False)
        self.tableWidget.setRowCount(500) # устанавливаем количество строк в 500

    def zeroing_count_photo(self):
        for k,v in self.count_photo.items():
            self.count_photo[k] = 0

    def add_amount_of_photo_to_label(self, file_name):
        _translate = QtCore.QCoreApplication.translate
        for k, v in self.count_photo.items():   # находим в файле количество в печать
                if k in file_name:              # и прибавляем к общему количеству данного формата фотографии
                    amount = int(file_name.split("_")[4])
                    v += amount 
                    self.count_photo[k] = v        
        self.label_10x15.setText(_translate("MainWindow", "10x15: " + str(self.count_photo["п_10х15_"])))
        self.label_15x20.setText(_translate("MainWindow", "15x20: " + str(self.count_photo["п_15х20_"])))
        self.label_20x30.setText(_translate("MainWindow", "20x30: " + str(self.count_photo["п_20х30_"])))
        self.label_WallCalendar.setText(_translate("MainWindow", "Настенный календарь: " + str(self.count_photo["п_Настенный календарь_"])))
        self.label_magnit.setText(_translate("MainWindow", "магнит: " + str(self.count_photo["п_магнит_"])))
        self.label_magnit_10x15.setText(_translate("MainWindow", "магнит 10х15: " + str(self.count_photo["п_магнит 10х15_"])))
        self.label_brelok58.setText(_translate("MainWindow", "Брелок 58: " + str(self.count_photo["Брелок 58"])))
        self.label_zerkalo75.setText(_translate("MainWindow", "Зеркало 75: " + str(self.count_photo["Зеркало 75"])))
        self.label_znaciok158.setText(_translate("MainWindow", "Значок 158: " + str(self.count_photo["Значок 158"])))
        self.label_kopilka158.setText(_translate("MainWindow", "Копилка 158: " + str(self.count_photo["Копилка 158"])))
        self.label_Cup.setText(_translate("MainWindow", "Кружка-термос с крышкой " + str(self.count_photo["Кружка-термос с крышкой"])))


    def add_psd_files_to_table(self, file, file_object, directory):
        """Функция добавления файла, имени обьекта и директории в таблицу.
        В функцию передается имя файла, имя обьекта, директория файла"""
        self.tableWidget.setItem(self.row_count, 0, QtWidgets.QTableWidgetItem(file))
        self.tableWidget.setItem(self.row_count, 1, QtWidgets.QTableWidgetItem(file_object))
        self.tableWidget.setItem(self.row_count, 2, QtWidgets.QTableWidgetItem(directory))
        self.add_amount_of_photo_to_label(file)
        self.row_count += 1

    def add_file_from_folder(self):
        """Добавляем список psd файлов в таблицу"""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        list_of_psd_files = combinator.search_file("psd", directory)
        self.tableWidget.clearContents()
        self.row_count = 0
        file_object = os.path.split(directory)[1] # имя объекта к которому принадлежит файл
        for file in list_of_psd_files:
            self.add_psd_files_to_table(file, file_object, directory)
        self.tableWidget.resizeColumnsToContents()
        self.zeroing_count_photo()
         

    def add_file(self):
        dialogObject = QtWidgets.QFileDialog(self, "Добавить файл","","Файлы изображений (*.psd)")
        dialogObject.setFileMode(3)
        dialogObject.setViewMode(1)
        dialogObject.exec()
        files = dialogObject.selectedFiles()
        for file in files:
            directory = os.path.split(file)[0]
            file_name = os.path.split(file)[1]
            file_object = os.path.split(directory)[1]
            self.add_psd_files_to_table(file_name, file_object, directory)
        self.tableWidget.resizeColumnsToContents()

    def create_object_dir(self, dict_of_psd_files):
        """Создаем отдельные папки для каждого обьекта
        чтобы сконвертировать туда png. Основная папка
        описана в переменной dir_for_png"""
        try:
            os.mkdir(self.dir_for_png)
        except Exception as e:
            print(e)
        for k,v in dict_of_psd_files.items():
            directory_object = self.dir_for_png + '\\' + os.path.split(k)[1]
            try:
                os.mkdir(directory_object)
            except Exception as e:
                print(e)

    def convert_psd_to_png(self, dict_of_psd_files):
        for k,v in dict_of_psd_files.items():
            path_for_png_object = 

    def get_list_of_psd_from_table(self): #создаем словарь на основании заполненной таблицы
        count_row = 0                     # вида {путь к файлу: [список файлов]}
        dict_of_psd_file = {}
        while self.tableWidget.item(count_row, 0) != None:
            path_to_file = self.tableWidget.item(count_row, 2).text()
            if path_to_file not in dict_of_psd_file:
                dict_of_psd_file[path_to_file] = []
                list_of_files = dict_of_psd_file[path_to_file]
                list_of_files.append(self.tableWidget.item(count_row, 0).text())
            else:
                list_of_files = dict_of_psd_file[path_to_file]
                list_of_files.append(self.tableWidget.item(count_row, 0).text())
            count_row += 1
        return dict_of_psd_file

    def compose_files(self):
        dict_of_psd_files = self.get_list_of_psd_from_table()
        self.create_object_dir(dict_of_psd_files)
        self.convert_psd_to_png(dict_of_psd_files)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()