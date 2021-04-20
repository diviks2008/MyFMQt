#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# sudo apt install python3-pyqt5

import sys
import os
import subprocess
import time
import shutil
import hashlib
import random
import locale
import re

from PyQt5.QtWidgets import QApplication, QTreeView, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QAbstractItemView, QStyle, QTextEdit, QMenu, QAction, QMessageBox, QInputDialog, QLabel, QProgressDialog
from PyQt5.QtCore import Qt, QItemSelectionModel, QFileInfo
from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem, QTextCursor, QImage


date_time = '%Y.%m.%d %H:%M:%S'
myemail = '646976696b733230303840676d61696c2e636f6d'
exts_image = ['.bmp', '.jpeg', '.jpg', '.png', '.gif']
exts_video = ['.avi', '.mkv', '.mp4']
exts_audio = ['.mp3']
list_columns = ['Name', 'size', 'rights', 'owner', 'group', 'ext', 'DateModified']
preview_max_lines = 300
My_title = 'MyFMQt'
version = '8'


class MyFMQt(QWidget):

    def __init__(self):
        super().__init__()
        self.list_columns = list_columns
        self.number_columns = len(self.list_columns)

        self.title = '{}_v{}'.format(My_title, version)
        self.folder_rab = os.getcwd()
        self.folder_prog = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.left = 100
        self.top = 100
        self.width = 1024
        self.height = 480
        self.width_default = 90
        self.width_date = 143
        self.width_text_edit = 350

        self.progress = QProgressDialog('Copying files...', 'Abort Copy', 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setAutoClose(True)
        self.progress.setMinimumDuration(100)
        self.progress.close()

        self.initUI()

        # move to center
        desktop = QApplication.desktop()
        x = (desktop.width() - self.frameSize().width()) // 2
        y = (desktop.height() - self.frameSize().height()) // 2
        self.move(x, y)

    def initUI(self):
        self.ico = self.style().standardIcon(QStyle.SP_DirIcon)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.ico))
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.treeView = QTreeView(self)
        self.e_folder = QLineEdit(self)
        self.b_up = QPushButton('&UP', self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.l_path = QLabel(self)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.list_columns)
        self.treeView.setModel(self.model)

        vboxLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        hboxLayout.addWidget(self.e_folder)
        hboxLayout.addWidget(self.b_up)
        vboxLayout.addLayout(hboxLayout)

        hboxLayout = QHBoxLayout()
        hboxLayout.addWidget(self.treeView)
        hboxLayout.addWidget(self.text_edit)
        vboxLayout.addLayout(hboxLayout)

        vboxLayout.addWidget(self.l_path)

        self.setLayout(vboxLayout)

        self.treeView.setRootIsDecorated(False)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.header().setDefaultAlignment(Qt.AlignCenter) # header to center
        self.treeView.header().setSectionsMovable(True) # to drag and drop columns

        self.e_folder.setText(self.folder_rab)
        self.get_files_in_folder(self.folder_rab)
        self.insert_data_in_model()

        self.e_folder_add_context_menu()
        self.text_edit_add_context_menu()
        self.text_edit.setMinimumWidth(self.width_text_edit)

        self.treeView.doubleClicked.connect(self.double_clicked)
        self.b_up.clicked.connect(self.press_button_up)
        self.treeView.clicked.connect(self.preview)

        header = self.treeView.header()
        header.setSectionsMovable(True)
        header.sectionClicked[int].connect(self.on_header_clicked)

        self.treeView.setSortingEnabled(True)
        # self.treeView.sortByColumn(1, Qt.DescendingOrder)
        # self.treeView.sortByColumn(1, Qt.AscendingOrder)

        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)  # <- enable selection of rows in tree
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)  # <- disable editing items in tree
        self.create_size_columns()
        self.print_list_files_in_folder(self.folder_rab)

        self.set_row(0)
        self.show()

    def addData(self, n, *t):
        for i in range(len(self.list_columns)):
            self.model.setData(self.model.index(n, i), t[i])

    def insert_data_in_model(self):
        folder = self.e_folder.text()
        all_lines = 0
        if os.path.exists(folder):
            self.folder_rab = folder
        else:
            self.folder_rab = os.getcwd()
        for dir_path in self.dirs:
            dir_name = os.path.basename(dir_path)
            tab_mtime, tab_atime = self.get_mtime_file(dir_path)
            self.model.insertRow(all_lines, QStandardItem(QStandardItem(QIcon(self.ico), '')))
            try:
                items = os.listdir(dir_path)
            except:
                self.addData(all_lines, dir_name, '', '', '', '', 'denied', tab_mtime)
                all_lines += 1
                continue
            dirs = [os.path.join(dir_path, d) for d in items if os.path.isdir(os.path.join(dir_path, d))]
            files = [os.path.join(dir_path, f) for f in items if os.path.isfile(os.path.join(dir_path, f))]
            file_size = '{}/{}/{}'.format(len(items), len(dirs), len(files))
            self.addData(all_lines, dir_name, file_size, oct(os.stat(dir_path).st_mode)[-3:], QFileInfo(dir_path).owner(), QFileInfo(dir_path).group(), '', tab_mtime)#, tab_atime)
            all_lines += 1

        for file_path in self.files:
            file_name = os.path.basename(file_path)
            tab_mtime, tab_atime = self.get_mtime_file(file_path)
            file_size = self.converter_number_to_gb(os.path.getsize(file_path))
            if file_path[-7:] == '.tar.gz':
                ext = file_path[-7:]
            else:
                ext = os.path.splitext(file_path)[1]
            self.model.insertRow(all_lines)
            self.addData(all_lines, file_name, file_size, oct(os.stat(file_path).st_mode)[-3:], QFileInfo(file_path).owner(), QFileInfo(file_path).group(), ext, tab_mtime)#, tab_atime)
            all_lines += 1

    def create_size_columns(self):
        size_columns = 0
        for i in range(self.number_columns - 1):
            self.treeView.resizeColumnToContents(i)
            size_columns += self.treeView.columnWidth(i)
        if self.treeView.columnWidth(0) > 276:
            self.treeView.setColumnWidth(0, 276)
        self.treeView.setColumnWidth(self.number_columns - 1, self.width_date)
        size_columns += self.width_date
        self.treeView.setMaximumWidth(size_columns + 2)
        size_columns_min = self.treeView.columnWidth(0) + self.treeView.columnWidth(1) + self.treeView.columnWidth(2)
        self.treeView.setMinimumWidth(size_columns_min + 3)

    def resizeEvent(self, event):
        self.create_size_columns()
        self.preview()

    def get_files_in_folder(self, folder):
        self.dirs = []
        self.files = []
        items = os.listdir(folder)
        self.dirs = [os.path.join(folder, d) for d in items if os.path.isdir(os.path.join(folder, d))]
        self.files = [os.path.join(folder, f) for f in items if os.path.isfile(os.path.join(folder, f))]
        header = self.treeView.header()
        self.sort_list_files_by_ind(header.sortIndicatorSection())

    def get_mtime_file(self, file_path):
        f_mtime = os.path.getmtime(file_path)
        f_atime = os.path.getatime(file_path)
        tab_mtime = time.strftime(date_time, time.localtime(f_mtime))
        tab_atime = time.strftime(date_time, time.localtime(f_atime))
        return tab_mtime, tab_atime

    def converter_number_to_gb(self, size):
        KB = 1024.0
        MB = KB * KB
        GB = MB * KB
        if size >= GB:
            return '{:,.1f} Gb'.format(size / GB)
        if size >= MB:
            return '{:,.1f} Mb'.format(size / MB)
        if size >= KB:
            return '{:,.1f} Kb'.format(size / KB)
        return '{} b'.format(size)

    def double_clicked(self, index):
        row = self.get_row()
        # data = self.model.itemData(index)
        self.start_file(row)

    def keyPressEvent(self, event):
        # print(event.key())
        if event.key() == Qt.Key_Return:  # Enter
            self.open_folder()
            return
        elif event.key() == Qt.Key_F1:  # F1
            self.print_help()
        elif event.key() == Qt.Key_R and Qt.Key_Control:  # Ctrl+R
            item_new = self.treeView.currentIndex().data()
            self.update_lineEdit_folder_rab(item_new)
            return
        # elif event.key() == Qt.Key_Escape:
        #     self.press_button_up(event='')
        #     return
        elif event.key() == Qt.Key_Delete:
            item_new = self.delete_dirs_files()
            self.update_lineEdit_folder_rab(item_new)
            return

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down:
            self.preview(self.treeView.currentIndex())

    def open_folder(self):
        self.text_edit.clear()
        row = self.get_row()
        try:
            self.start_file(row)
        except:
            self.update_lineEdit_folder_rab()
        self.set_row(row)

    def preview(self, index=0):
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)  # selected row
        self.text_edit.clear()
        try:
            file_path = self.get_filepath_by_index()
            self.l_path.setText(os.path.basename(file_path))
        except:
            self.l_path.setText('')
            return
        if os.access(file_path, os.R_OK) and os.path.isfile(file_path):
            if os.path.splitext(file_path)[1] in exts_image:
                try:
                    icon = QImage(file_path)
                    if icon.isNull():
                        return
                    self.l_path.setText('{}  ({}x{})'.format(os.path.basename(file_path), icon.width(), icon.height()))
                    new_width = self.text_edit.size().width() - 10
                    proportion = icon.size().width()/new_width
                    new_height = icon.size().height()/proportion
                    # if new_height > self.text_edit.size().height() - 10:
                    #     new_height = self.text_edit.size().height() - 10
                    image = icon.scaled(new_width, new_height)
                    document = self.text_edit.document()
                    cursor = QTextCursor(document)
                    cursor.insertImage(image)
                except:
                    return
            elif not self.if_file_txt(file_path):
                return
            else:
                try:
                    f = open(file_path, 'r')
                    for i in range(preview_max_lines):
                        text = f.readline()
                        if text:
                            self.text_edit.insertPlainText(text)
                        else:
                            break
                    f.close()
                    if i >= preview_max_lines - 1:
                        if locale.getdefaultlocale()[0] == 'ru_RU':
                            self.text_edit.insertPlainText(
                                '\n{0}\nЭто не все содержимое файла.\nДля чтения файла, двойной клик по имени файла\n{0}\n'.format(
                                    '.' * 71))
                        else:
                            self.text_edit.insertPlainText('\n{0}\nThis is not all content.\nTo read a file, double click on the file name\n{0}\n'.format('.'*71))
                    return
                except:
                    self.text_edit.clear()
                    return
        elif os.path.isdir(file_path):
            self.text_edit.clear()
            try:
                lines = []
                files_all = [os.path.join(file_path, f) for f in os.listdir(file_path)]
                [lines.append('[{}]'.format(os.path.basename(d))) for d in sorted(files_all) if os.path.isdir(d)]
                [lines.append('{}'.format(os.path.basename(f))) for f in sorted(files_all) if os.path.isfile(f)]
                self.text_edit.setText('\n'.join(lines))
            except:
                return

    def if_file_txt(self, file_path):
        f = open(file_path, 'rb')
        line_f = f.read(10)
        f.close()
        for line in line_f:
            if line < 10:
                return 0
        return 1

    def start_file(self, row):
        file_name = self.model.item(row, column=0).text()
        file_path = os.path.join(self.folder_rab, file_name)
        if not os.access(file_path, os.R_OK):
            return
        if self.model.item(row, column=int(self.list_columns.index('ext'))).text() == 'denied':
            return

        if os.path.isfile(file_path):
            if sys.platform == 'win32':
                os.startfile(file_path)
            else:
                try:
                    subprocess.run(['xdg-open', file_path])
                except:
                    pass
            self.set_row(row)
            return
        elif os.path.isdir(file_path):
            self.print_list_files_in_folder(file_path)

    def print_list_files_in_folder(self, file_path):
        self.remove_lines()
        self.folder_rab = file_path
        self.reset_folder_rab()
        self.get_files_in_folder(self.folder_rab)
        self.insert_data_in_model()
        self.create_size_columns()
        self.set_row()
        self.treeView.setFocus()

    def get_row(self):
        # row = self.model.itemFromIndex(self.treeView.currentIndex()).row()
        # row = self.treeView.selectedIndexes()[0].row()
        row = self.treeView.currentIndex().row()
        return row

    def get_row_by_item_column_0(self, item):
        rows = self.model.rowCount()
        for row in range(rows):
            index = self.model.index(row, 0)
            rowtext = self.model.itemFromIndex(index).text()
            if item == rowtext:
                return row

    def get_item_by_row_min(self, rows, delete=0):
        if len(rows) > 1:
            row = min(rows)
        else:
            row = rows[0]
        if delete:
            row = row - 1
            if row < 0:
                row = 0
        item = self.model.item(row, column=0).text()
        return item

    def get_list_selected_lines(self):
        dirs, files, rows = [], [], []
        for line in self.treeView.selectedIndexes():
            row = line.row()
            if row not in rows:
                file_name = self.model.item(row, column=0).text()
                file_path = os.path.join(self.folder_rab, file_name)
                if not os.access(file_path, os.R_OK):
                    continue
                if self.model.item(row, column=int(self.list_columns.index('size'))).text() == 'denied':
                    continue
                if os.path.isdir(file_path):
                    dirs.append(file_path)
                elif os.path.isfile(file_path):
                    files.append(file_path)
                else:
                    continue
                rows.append(row)
        return dirs, files, rows

    def set_row(self, row=0):
        try:
            index = self.model.index(row, 0)
        except:
            index = self.model.index(0, 0)
        self.treeView.selectionModel().clear()
        self.treeView.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.preview(index=index.row())

    def remove_lines(self):
        self.model.removeRows(0, self.model.rowCount())

    def press_button_up(self, event):
        self.text_edit.clear()
        item = os.path.basename(self.e_folder.text())
        if self.e_folder.text() != self.folder_rab:
            self.update_lineEdit_folder_rab()
        new_folder = os.path.dirname(self.folder_rab)
        if os.path.exists(new_folder):
            self.folder_rab = new_folder
            self.print_list_files_in_folder(self.folder_rab)
            row = self.get_row_by_item_column_0(item)
            self.set_row(row)

    def update_lineEdit_folder_rab(self, item=''):
        if not os.path.exists(self.e_folder.text()):
            self.reset_folder_rab()
            return
        self.folder_rab = self.e_folder.text()
        self.print_list_files_in_folder(self.folder_rab)
        row = self.get_row_by_item_column_0(item)
        # print('row:{} item:{}'.format(row, item))
        self.set_row(row)

    def reset_folder_rab(self):
        self.e_folder.clear()
        self.e_folder.setText(self.folder_rab)

    def get_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select folder:', self.folder_rab)
        if os.path.exists(dir_path):
            self.text_edit.clear()
            self.folder_rab = dir_path
            self.print_list_files_in_folder(self.folder_rab)
            self.set_row()

    def get_filepath_by_index(self):
        try:
            row = self.get_row()
            file_name = self.model.item(row, column=0).text()
        except:
            file_name = ''
        file_path = os.path.join(self.folder_rab, file_name)
        return file_path

    def e_folder_add_context_menu(self):
        self.e_folder.setContextMenuPolicy(Qt.ActionsContextMenu)
        open_folder_Action = QAction('Open folder', self)
        open_folder_Action.triggered.connect(self.get_dir)
        self.e_folder.addAction(open_folder_Action)
        update_Action = QAction('Update', self)
        update_Action.triggered.connect(self.update_lineEdit_folder_rab)
        self.e_folder.addAction(update_Action)
        close = QAction('Quit', self)
        close.triggered.connect(self.quit_prog)
        self.e_folder.addAction(close)

    def text_edit_add_context_menu(self):
        self.text_edit.setContextMenuPolicy(Qt.ActionsContextMenu)

        rnd_str_Action = QAction('RND str', self)
        self.text_edit.addAction(rnd_str_Action)
        rnd_str_Action.triggered.connect(self.rnd_str)

        quit_Action = QAction('Quit', self)
        self.text_edit.addAction(quit_Action)
        quit_Action.triggered.connect(self.quit_prog)

    def contextMenuEvent(self, event):
        item = self.treeView.currentIndex().data()
        item_new = ''

        menu = QMenu(self)

        create_file_Action = menu.addAction('Create file')
        create_dir_Action = menu.addAction('Create folder')

        menu.addSeparator()
        rename_file_Action = menu.addAction('Rename')
        copy_dirs_files_Action = menu.addAction('Copy')
        move_dirs_files_Action = menu.addAction('Move')
        chmod_Action = menu.addAction('Chmode')
        chmod_by_maska_Action = menu.addAction('Chmode by maska')
        # chown_Action = menu.addAction('Chown')
        delete_dirs_files_Action = menu.addAction('Delete')

        menu.addSeparator()
        shred_file_Action = menu.addAction('Shred file')
        menu.addSeparator()

        update_Action = menu.addAction('Update')
        quit_Action = menu.addAction('Quit')

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == create_file_Action:
            item_new = self.create_file()
        elif action == create_dir_Action:
            item_new = self.create_dir()

        elif action == rename_file_Action:
            item_new = self.rename_file()
        elif action == copy_dirs_files_Action:
            item_new = self.copy_dirs_files()
        elif action == move_dirs_files_Action:
            item_new = self.move_dirs_files()
        elif action == delete_dirs_files_Action:
            item_new = self.delete_dirs_files()
        elif action == chmod_Action:
            item_new = self.chmod_file()
        elif action == chmod_by_maska_Action:
            item_new = self.chmod_by_maska()

        elif action == shred_file_Action:
            item_new = self.shred_file()
        elif action == update_Action:
            self.update_lineEdit_folder_rab()
        elif action == quit_Action:
            self.quit_prog()
        # menu.close()
        if item_new:
            item = item_new
        self.update_lineEdit_folder_rab(item)

    def create_file(self):
        file_path_old = self.get_filepath_by_index()
        dialog, res = QInputDialog.getText(self.treeView, 'Create file', 'Enter name:')
        if res and dialog.strip():
            file_name = dialog.strip()
            file_path = os.path.join(self.folder_rab, file_name)
            if os.path.exists(file_path):
                QMessageBox.warning(self.treeView, 'Create file', 'File with this name exists!')
                return os.path.basename(file_path_old)
            else:
                with open(file_path, 'w') as f:
                    f.flush()
                os.chmod(file_path, mode=0o700)
                return file_name
        else:
            return os.path.basename(file_path_old)

    def shred_file(self):
        dirs, files, rows = self.get_list_selected_lines()
        if not rows:
            item = os.path.basename(self.get_filepath_by_index())
            return item
        item = self.get_item_by_row_min(rows, delete=1)
        res = QMessageBox.warning(self.treeView, 'Delete files', '{}\n\nCONTINUE?'.format('\n'.join(files)),
                                  buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                  defaultButton=QMessageBox.Cancel)
        if res == 16384:
            for file_path in files:
                if os.path.isfile(file_path) and os.access(file_path, os.W_OK):
                    try:
                        subprocess.run(['shred', '-uvz', file_path])
                    except:
                        continue
        return item

    def create_dir(self):
        dir_path_old = self.get_filepath_by_index()
        dialog, res = QInputDialog.getText(self.treeView, 'Create dir', 'Enter name:')
        if res and dialog.strip():
            dir_name = dialog.strip()
            dir_path = os.path.join(self.folder_rab, dir_name)
            if os.path.exists(dir_path):
                QMessageBox.warning(self.treeView, 'Create dir', 'Folder with this name exists!')
                return os.path.basename(dir_path_old)
            else:
                os.mkdir(dir_path, mode=0o700)
                return dir_name
        else:
            return os.path.basename(dir_path_old)

    def write_chmod_file(self, file_path, maska):
        if not os.access(file_path, os.R_OK):
            return 1
        f_mode = oct(os.stat(file_path).st_mode)
        chmod_by_write = oct(int(f_mode, base=8) & int(maska, base=8))
        if chmod_by_write[-3:] == f_mode[-3:]:
            return 0
        try:
            os.chmod(file_path, mode=int(chmod_by_write, base=8))
            return 0
        except:
            return 1

    def chmod_file(self):
        dirs, files, rows = self.get_list_selected_lines()
        if not rows:
            item = os.path.basename(self.get_filepath_by_index())
            return item
        item = self.get_item_by_row_min(rows)
        dialog, res = QInputDialog.getText(self.treeView, 'Chmod', 'Enter chmod(format:777):', text='{}'.format(oct(os.stat(self.get_filepath_by_index()).st_mode)[-3:]))
        if res and dialog.strip():
            chmod_enter = dialog.strip()
            if self.is_chmod(chmod_enter):
                for file_path in files:
                    try:
                        os.chmod(file_path, mode=int(chmod_enter, base=8))
                    except:
                        continue
                for dir_path in dirs:
                    try:
                        os.chmod(dir_path, mode=int(chmod_enter, base=8))
                    except:
                        continue
        return os.path.basename(item)

    def chmod_by_maska(self):
        dirs, files, rows = self.get_list_selected_lines()
        if not rows:
            item = os.path.basename(self.get_filepath_by_index())
            return item
        item = self.get_item_by_row_min(rows)

        dialog, res = QInputDialog.getText(self.treeView, 'Chmod', 'Enter chmod maska(format:777):', text='770')
                                            # text='{}'.format(oct(os.stat(self.get_filepath_by_index()).st_mode)[-3:]))
        if res and dialog.strip():
            maska = dialog.strip()
            if self.is_chmod(maska):
                for file_path in files:
                    self.write_chmod_file(file_path, maska)
                for dir_path in dirs:
                    for path_, dirs_, files_ in os.walk(dir_path):
                        for file_ in files_:
                            file_path = os.path.join(path_, file_)
                            if os.path.isfile(file_path):
                                self.write_chmod_file(file_path, maska)
                        for dir_ in dirs_:
                            dir_path_ = os.path.join(path_, dir_)
                            self.write_chmod_file(dir_path_, maska)
                    self.write_chmod_file(dir_path, maska)
        return item

    def chown_file(self):
        QMessageBox.warning(self.treeView, 'menu', 'menu item under construction')
        # os.chown(name_path, 0, 0)

    def rename_file(self):
        file_path_old = self.get_filepath_by_index()
        if not os.path.basename(file_path_old):
            return os.path.basename(file_path_old)
        dialog, res = QInputDialog.getText(self.treeView, 'Rename file', 'New name?', text=os.path.basename(file_path_old))
        if res and dialog.strip():
            file_name_new = dialog.strip()
            file_path_new = os.path.join(self.folder_rab, file_name_new)
            if os.path.exists(file_path_new):
                QMessageBox.warning(self.treeView, 'Rename file', 'File with this name exists!')
                return os.path.basename(file_path_old)
            else:
                os.rename(file_path_old, file_path_new)
                return file_name_new
        else:
            return os.path.basename(file_path_old)

    def shutil_copy2_file(self, dir_path, files):
        self.progress.reset()
        self.progress.setMaximum(len(files))

        for i, src_file in enumerate(files):
            key_copy_on = 0
            dst_file = os.path.join(dir_path, os.path.basename(src_file))

            if self.key_copy:
                self.progress.setLabelText('Copy file:{}\nTo:{}\n'.format(src_file, dst_file))
                self.progress.setValue(i)
                self.progress.update()
                if self.progress.wasCanceled():
                    self.progress.close()
                    return 1

            if os.path.exists(dst_file):
                checksum1 = self.get_checksum_file(src_file)
                checksum2 = self.get_checksum_file(dst_file)
                if checksum1 and checksum2 and checksum1 == checksum2:
                        continue
                if not self.key_copy:
                    res = QMessageBox.warning(self.treeView, 'Copy file',
                                              '{}\nFile with this name exists!\n\nCONTINUE?'.format(dst_file),
                                              buttons=QMessageBox.YesAll | QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                              defaultButton=QMessageBox.No)
                    if res == 4194304:  # Cansel
                        return 1
                    elif res == 32768:  # YesAll
                        self.key_copy = 1
                    elif res == 65536:  # No
                        continue
                    elif res == 16384:  # Yes
                        key_copy_on = 1

                if key_copy_on or self.key_copy:
                    try:
                        os.remove(dst_file)
                        shutil.copy2(src_file, dst_file)
                        self.set_stat(src_file, dst_file)
                        continue
                    except:
                        QMessageBox.warning(self.treeView, 'Copy file',
                                            'src_file:{}\ndst_file:{}\nError copying file\nFile with this name exists!\nDenied dst_file!\n'.format(
                                                src_file, dst_file))
                        continue
                else:
                    continue

            try:
                shutil.copy2(src_file, dst_file)
                self.set_stat(src_file, dst_file)
            except:
                QMessageBox.warning(self.treeView, 'Copy file',
                                    '{}\n{}\nError copying file\nInvalid new path or folder not accessible\n\nCopying CANSELL!\n'.format(
                                        src_file, dst_file))
                return 1
        self.progress.close()
        return 0

    def copy_dir_recursive(self, src_dir, dst_dir):
        for path, dirs, files in os.walk(src_dir):
            dst_path = path.replace(src_dir, dst_dir, 1)
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)
                shutil.copystat(path, dst_path)
                if sys.platform == 'linux':
                    os.chown(dst_path, uid=os.stat(path).st_uid, gid=os.stat(path).st_gid)
            files_src = [os.path.join(path, f) for f in files]
            if self.shutil_copy2_file(dst_path, files_src):
                return 1
        return 0

    def copy_dirs_files(self):
        self.key_copy = 0
        dirs, files, rows = self.get_list_selected_lines()
        if not rows:
            item = os.path.basename(self.get_filepath_by_index())
            return item
        item = self.get_item_by_row_min(rows)

        dir_path = QFileDialog.getExistingDirectory(self, 'Select folder:', self.folder_rab)

        if not dir_path:
            return item

        if self.shutil_copy2_file(dir_path, files):
            return item

        for src_dir in dirs:
            dst_dir = os.path.join(dir_path, os.path.basename(src_dir))
            if self.copy_dir_recursive(src_dir, dst_dir):
                return item
        return item

    def shutil_move_file(self, dir_path, files):
        for src_file in files:
            key_move_on = 0
            dst_file = os.path.join(dir_path, os.path.basename(src_file))
            if os.path.exists(dst_file):
                if not self.key_move:
                    res = QMessageBox.warning(self.treeView, 'Move file',
                                              '{}\nFile with this name exists!\n\nCONTINUE?'.format(dst_file),
                                              buttons=QMessageBox.YesAll | QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                              defaultButton=QMessageBox.No)
                    if res == 4194304:  # Cansel
                        return 1
                    elif res == 32768:  # YesAll
                        self.key_move = 1
                    elif res == 65536:  # No
                        continue
                    elif res == 16384:  # Yes
                        key_move_on = 1

                if key_move_on or self.key_move:
                    try:
                        shutil.move(src_file, dst_file)
                        continue
                    except:
                        try:
                            os.remove(dst_file)
                            shutil.move(src_file, dst_file)
                        except:
                            QMessageBox.warning(self.treeView, 'Move file',
                                                'src_file:{}\ndst_file:{}\nError move file\nFile with this name exists!\nDenied dst_file!\n'.format(
                                                    src_file, dst_file))
                            continue
                else:
                    continue

            try:
                shutil.move(src_file, dst_file)
            except:
                QMessageBox.warning(self.treeView, 'Move file',
                                    '{}\n{}\nError move file\nInvalid new path or folder not accessible\n\nMove CANSELL!\n'.format(
                                        src_file, dst_file))
                return 1
        return 0

    def move_dirs_files(self):
        self.key_move = 0
        dirs, files, rows = self.get_list_selected_lines()
        if not rows:
            item = os.path.basename(self.get_filepath_by_index())
            return item
        item = self.get_item_by_row_min(rows, delete=1)
        dir_path = QFileDialog.getExistingDirectory(self, 'Select folder:', self.folder_rab)

        if not dir_path:
            return item

        if self.shutil_move_file(dir_path, files):
            return item

        if self.shutil_move_file(dir_path, dirs):
            return item

        return item

    def delete_dirs_files(self):
        dirs, files, rows = self.get_list_selected_lines()
        if not rows:
            item = os.path.basename(self.get_filepath_by_index())
            return item
        item = self.get_item_by_row_min(rows, delete=1)

        res = QMessageBox.warning(self.treeView, 'Delete', 'Delete dirs:\n{}\n\nDelete files:\n{}\n\nCONTINUE?'.format('\n'.join(dirs), '\n'.join(files)),
                                  buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                  defaultButton=QMessageBox.Cancel)
        if res == 16384:
            for file_path in files:
                try:
                    os.remove(file_path)
                except:
                    continue
            for dir_path in dirs:
                try:
                    shutil.rmtree(dir_path)
                except:
                    continue
        return item

    def is_chmod(self, chmod_enter):
        try:
            int(chmod_enter)
        except:
            return 0
        if len(str(chmod_enter)) != 3:
            return 0
        for i in range(len(str(chmod_enter))):
            if int(str(chmod_enter)[i]) > 7:
                return 0
        return 1

    def get_files_exclude(self, file_exclude):
        start_switch = '#'
        exclude_list = []
        if os.path.exists(file_exclude):
            with open(file_exclude, 'r') as f:
                f_lines = f.readlines()
            for f_line in f_lines:
                f_line = f_line.strip()
                if f_line.startswith(start_switch):
                    continue
                elif f_line:
                    exclude_list.append(f_line)
        return exclude_list

    def get_checksum_file(self, file_path):
        checksum = hashlib.md5()
        try:
            with open(file_path, 'rb') as fp:
                while True:
                    buffer = fp.read(8192)
                    if not buffer: break
                    checksum.update(buffer)
            checksum = checksum.digest()
            return checksum
        except:
            return ''

    def rnd_str(self):
        len_name_min = 9
        len_name_default = 55
        number_list = [str(n) for n in range(0, 10, 1)]
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        alphabet_upper = alphabet.upper()
        numbers = ''.join(number_list)
        # alphabet_dop = '~!@#$%^&*()_-=+{}[]<>?,.'
        alphabet_dop = '~!@#$&_'
        alphabet += alphabet_upper + numbers + alphabet_dop

        len_name, ok = QInputDialog.getInt(self.treeView, 'Create name rnd', 'Len str?', value=len_name_default, min=4, max=1024)
        if not ok:
            return

        def check_valid(my_pswd):
            if not re.search('[a-z]', my_pswd):
                return 0
            elif not re.search('[A-Z]', my_pswd):
                return 0
            elif not re.search('[0-9]', my_pswd):
                return 0
            elif not re.search('[_@$#]', my_pswd):
                return 0
            elif re.search('[\s]', my_pswd):
                return 0
            else:
                return 1

        if len_name < len_name_min:
            return

        while True:
            random_name = ''.join(random.choice(alphabet) for i in range(len_name))
            if check_valid(random_name) and random_name[0] not in number_list and random_name[0] not in alphabet_dop:
                break

        self.text_edit.clear()
        self.text_edit.setText(random_name)

    def set_stat(self, file_src, file_dst):
        shutil.copystat(file_src, file_dst)
        if sys.platform == 'linux':
            os.chown(file_dst, uid=os.stat(file_src).st_uid, gid=os.stat(file_src).st_gid)

    def on_header_clicked(self, ind):
        item = os.path.basename(self.get_filepath_by_index())
        self.sort_list_files_by_ind(ind)
        self.remove_lines()
        self.insert_data_in_model()
        row = self.get_row_by_item_column_0(item)
        self.set_row(row)
        self.treeView.setFocus()

    def sort_list_files_by_ind(self, ind=0):
        if ind == 0:
            self.dirs.sort(key=self.sort_by_name)
            self.files.sort(key=self.sort_by_name)
        elif ind == 1:
            self.dirs.sort(key=self.sort_by_size)
            self.files.sort(key=self.sort_by_size)
        elif ind == 2:
            self.dirs.sort(key=self.sort_by_rights)
            self.files.sort(key=self.sort_by_rights)
        elif ind == 3:
            self.dirs.sort(key=self.sort_by_owner)
            self.files.sort(key=self.sort_by_owner)
        elif ind == 4:
            self.dirs.sort(key=self.sort_by_group)
            self.files.sort(key=self.sort_by_group)
        elif ind == 5:
            self.dirs.sort(key=self.sort_by_ext)
            self.files.sort(key=self.sort_by_ext)
        elif ind == 6:
            self.dirs.sort(key=self.sort_by_mtime)
            self.files.sort(key=self.sort_by_mtime)
        self.sort_list_files_revers()

    def sort_list_files_revers(self):
        header = self.treeView.header()
        if not header.sortIndicatorOrder():
            self.dirs.reverse()
            self.files.reverse()

    def sort_by_name(self, f_path):
        return os.path.basename(f_path).lower()

    def sort_by_item(self, f_path):
        if os.path.isdir(f_path):
            try:
                len_item = len([d for d in os.listdir(f_path)])
            except:
                return 0
            return len_item
        # return os.path.splitext(f_path)[1].lower()
        return os.path.basename(f_path).lower()

    def sort_by_rights(self, f_path):
        return oct(os.stat(f_path).st_mode)[-3:]

    def sort_by_owner(self, f_path):
        return QFileInfo(f_path).owner()

    def sort_by_group(self, f_path):
        return QFileInfo(f_path).group()

    def sort_by_size(self, f_path):
        if os.path.isdir(f_path):
            try:
                len_dirs = len([d for d in os.listdir(f_path)])
                return len_dirs
            except:
                return 0

        elif os.path.isfile(f_path):
            return os.path.getsize(f_path)
        return 0

    def sort_by_ext(self, f_path):
        if os.path.isdir(f_path):
            return os.path.basename(f_path).lower()
        return os.path.splitext(f_path)[1].lower()

    def sort_by_mtime(self, f_path):
        return os.path.getmtime(f_path)

    def quit_prog(self):
        QApplication.quit()

    def print_help(self):
        help_en = '''
Description:
    MyFMQt_v8.py is a file manager with minimal functionality.
    The main feature is fast navigation through text, photo and video files with preview

Software requirements:
    The application requires `python3` to run.
    Run the following command to install the required dependencies:
    for Debian, Ubuntu:
    `sudo apt install python3-pyqt5`

To run the application:
    1. Download MyFMQt_v8.py from the GitHub repository.
    2. Go to the folder where the file was downloaded.
    3. Run the following command in the console:
    `$> python3 MyFMQt_v8.py`

Navigating with the mouse:
    1. Double-click the folder name - navigate to the selected folder.
    2. Double-click the file - opens the file in the default application.
    3. One click on a text file or picture - a preview of the file contents.
    4. Right-click on the address bar - call the folder selection context menu
    5. Right-click on the file list - call the file context menu
    6. Right-click on the text field - call the context menu

Keyboard navigation:
    Up and Down arrow keys - move through the list
    Enter - go to the selected folder, or go to a new address specified in the address bar
    F1 - in the text field print help
    Ctrl+R - Refresh File List
    Alt+U - go to parent folder
    Delete - delete selected files

Features:
    1. Column "Name" - by default sorting by name
    2. Column "Size" - if a folder, then this is Items/Dirs/Files in the folder
    3. Text file preview mode is limited to 300 lines.
       To read the full contents of a file, double click on the file name.
    4. To change the order of the columns:
       Grab the title with the mouse and drag it.
    5. Chmod - non-recursive change of access rights of selected items
    6. Chmod by maska - RECURSIVE change of access rights of selected elements
    '''
        help_ru = '''
Описание:
    MyFMQt_v8.py - это файловый менеджер с минимальным функционалом.
    Главная особенность - быстрая навигация по текстовым, фото и видео файлам с предпросмотром

Программные требования:
    Для запуска приложения требуется `python3`.
    Для установки необходимых зависимостей выполните следующую команду:
    для Debian, Ubuntu:
    `sudo apt install python3-pyqt5`

Для запуска приложения:
    1. Загрузите MyFMQt_v8.py из репозитория GitHub.
    2. Зайдите в папку, в которую был скачан файл.
    3. Выполните следующую команду в консоли:
    `$> python3 MyFMQt_v8.py`

Навигация с помощью мыши:
    1. Дважды щелкните имя папки - переход к выбранную папку.
    2. Дважды щелкните файл - открывает файл в приложении по умолчанию.
    3. Один щелчок по текстовому файлу или рисунку - предварительный просмотр содержимого файла.
    4. Клик правой кнопкой на строке адреса - вызов контекстного меню выбора папки
    5. Клик правой кнопкой на списке файлов - вызов контекстного меню файлов
    6. Клик правой кнопкой на текстовом поле - вызов контекстного меню

Навигация клавишами клавиатуры:
    Клавиши курсора Вверх и Вниз - передвижение по списку
    Enter - перейти в выбранную папку, или перейти по новому адресу, указанному в адресной строке
    F1 - в текстовом поле напечатать помощь
    Ctrl+R - обновить список файлов
    Alt+U - перейти в родительскую папку
    Delete - удалить выбранные файлы

Особенности:
    1. Столбец "Name" - по по умолчанию сортировка по имени
    2. Столбец "Size" - если папка, то это Items/Dirs/Files в папке
    3. Режим предпросмотра текстового файла ограничен 300 строками.
       Для прочтения полного содержимого файла, дважды кликните по имени файла.
    4. Для изменения порядка следования колонок:
       Захватите заголовок мышкой и перетащить его.
    5. Chmod - не рекурсивное изменение прав доступа выбранных элементов
    6. Chmod by maska - РЕКУРСИВНОЕ изменение прав доступа выбранных элементов
        '''
        self.text_edit.clear()
        if locale.getdefaultlocale()[0] == 'ru_RU':
            self.text_edit.setText(help_ru)
        else:
            self.text_edit.setText(help_en)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyFMQt()
    ex.show()
    app.exec_()

    sys.exit(0)
