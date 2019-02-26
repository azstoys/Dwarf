"""
Dwarf - Copyright (C) 2019 Giovanni Rocca (iGio90)
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog

from lib.session import Session
from lib.android import AndroidDecompileUtil
from lib.adb import Adb

from ui.dialog_list import ListDialog
from ui.dialog_input import InputDialog


class AndroidSession(Session):
    """ All Android Stuff goes here
        if u look for something android related its here then
    """

    def __init__(self):
        super(AndroidSession, self).__init__()
        self.adb = Adb()
        # main menu every session needs
        self._menu = [QMenu(self.session_type + ' Session')]
        #self._menu[0].addAction('Save Session', self._save_session)
        self._menu[0].addAction('Close Session', self.stop_session)

        # connect to onUiReady so we know when sessionui is created
        self.onUiReady.connect(self._ui_ready)

    def _ui_ready(self):
        # session ui is available via self.session_ui now
        # if u requested memory to create in sessionui then
        # it is available via self.session_ui.memory and so on
        print('ui ready')

    @property
    def session_ui_sections(self):
        # what sections we want in session_ui
        return ['registers', 'memory', 'threads', 'console', 'watchers', 'hooks']

    @property
    def session_type(self):
        """ return session name to show in menus etc
        """
        return 'Android'

    @property
    def main_menu(self):
        """ return our created menu
        """
        return self._menu

    def initialize(self, config):
        # session supports load/save then use config

        if not self.adb.available:
            self.onStopped.emit()
            return

        # setup ui etc for android
        self._setup_menu()
        # all fine were done wait for ui_ready
        self.onCreated.emit()

    def _setup_menu(self):
        """ Build Menus
        """
        # additional menus
        file_menu = QMenu('&File')
        save_apk = QAction("&Save APK", self)
        save_apk.triggered.connect(self.save_apk)
        decompile_apk = QAction("&Decompile APK", self)
        decompile_apk.triggered.connect(self.decompile_apk)

        file_menu.addAction(save_apk)
        file_menu.addAction(decompile_apk)

        self._menu.append(file_menu)

        # additional menus
        device_menu = QMenu('&Device')
        self._menu.append(device_menu)

    def stop_session(self):
        # cleanup ur stuff

        # end session
        super().stop_session()

    def start(self, args):
        print(args)

    def decompile_apk(self):
        packages = self.adb.list_packages()
        if packages:
            accept, items = ListDialog.build_and_show(
                self.build_packages_list,
                packages,
                double_click_to_accept=True)
            if accept:
                if len(items) > 0:
                    path = items[0].get_apk_path()
                    AndroidDecompileUtil.decompile(self.adb, path)

    def save_apk(self):
        packages = self.adb.list_packages()
        if packages:
            accept, items = ListDialog.build_and_show(
                self.build_packages_list,
                packages,
                double_click_to_accept=True)
            if accept:
                if len(items) > 0:
                    path = items[0].get_apk_path()
                    r = QFileDialog.getSaveFileName()
                    if len(r) > 0 and len(r[0]) > 0:
                        self.adb.pull(path, r[0])