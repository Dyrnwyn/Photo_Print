import sys
from PyQt5 import QtWidgets
import window
import combinator


class MainApp(QtWidgets.QMainWindow, window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addFileButton.clicked.connect(self.add_file)
        self.addDirectoryButton.clicked.connect(self.add_file_from_folder)
        self.progressBar.setVisible(False)

    def add_file_from_folder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        list_of_psd_files = combinator.search_file("psd", directory)
        row_count = len(list_of_psd_files)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(row_count)
        current_object = "Иркутск"
        count = 0
        for file in list_of_psd_files:
            print(file + " " + str(count))
            self.tableWidget.setItem(count, 0, QtWidgets.QTableWidgetItem(file))
            self.tableWidget.setItem(count, 1, QtWidgets.QTableWidgetItem(current_object))
            count += 1




    def add_file(self):
        files = QtWidgets.QFileDialog.getOpenFileName(self, "Добавить файл","","Файлы изображений (*.psd)")


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()