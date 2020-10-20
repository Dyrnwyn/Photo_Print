import sys
from PyQt5 import QtWidgets
import window


class MainApp(QtWidgets.QMainWindow, window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addFileButton.clicked.connect(self.add_file)
        self.addDirectoryButton.clicked.connect(self.browse_folder)
        self.progressBar.setVisible(False)

    def browse_folder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")

    def add_file(self):
        files = QtWidgets.QFileDialog.getOpenFileName(self, "Добавить файл","","Файлы изображений (*.psd)")


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()