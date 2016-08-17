# -*- coding: utf-8 -*-
"""
@author: lbluque
"""
import time
from PySide import QtGui, QtCore
from PySide.QtUiTools import QUiLoader


class LoginDialog(QtGui.QWidget):
    """
    Class for user credential input and login to NERSC/SPOT through NEWT/SPOT API
    """
    REMOTE_NAMES = ('SPOT', 'NERSC', 'Globus')

    loginClicked = QtCore.Signal(tuple)
    logoutClicked = QtCore.Signal()
    sigLoggedIn = QtCore.Signal(bool)

    def __init__(self, remotename='SPOT', parent=None):
        super(LoginDialog, self).__init__(parent)

        if remotename not in self.REMOTE_NAMES:
            raise ValueError('Remote must be one of %s, not %s' % (self.REMOTE_NAMES, remotename))

        self.ui = QUiLoader().load('gui/login_widget.ui', self)
        self.ui.stackedWidget.setCurrentWidget(self.ui.login_page)
        self.ui.pass_box.setEchoMode(QtGui.QLineEdit.Password)

        self.ui.login_button.clicked.connect(self.handleLogin)
        self.ui.pass_box.returnPressed.connect(self.handleLogin)
        self.ui.host_box.returnPressed.connect(self.handleLogin)
        self.ui.logout_button.clicked.connect(self.handleLogout)
        self.setStyleSheet('background-color:#111111;')

        self.hide()

        l = QtGui.QVBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.ui)
        self.setLayout(l)

        self._login_slot = None

    @property
    def login_slot(self):
        return self._login_slot

    @login_slot.setter
    def login_slot(self, slot):
        if self.login_slot is not None:
            self.loginClicked.disconnect(self.login_slot)
        self._login_slot = slot
        self.loginClicked.connect(self._login_slot)

    @QtCore.Slot(QtCore.Signal, bool)
    def loginRequest(self, login_clicked_slot, show_host=False):
        if show_host:
            self.ui.host_box.show()
        else:
            self.ui.host_box.hide()
        self.ui.user_box.setFocus()
        self.login_slot = login_clicked_slot
        self.setCurrentWidget(self.ui.login_page)
        self.show()

    def handleLogin(self):
        host, usr, pwd = self.ui.host_box.text(), self.ui.user_box.text(), self.ui.pass_box.text()
        if usr == '':
            QtGui.QMessageBox.warning(self, 'Username missing', 'You forgot to mention who you are!')
        elif pwd == '':
            QtGui.QMessageBox.warning(self, 'Password missing',
                                      'You need to provide proof that you really are {}!'.format(usr))
        elif host == '' and not self.ui.host_box.isHidden():
            QtGui.QMessageBox.warning(self, 'Host missing',
                                      'Xi-cam can not guess what host you want to connect to yet!')
        else:
            self.setCurrentWidget(self.ui.progress_page)
            self.progressMessage('Logging in...')
            self.startProgress()
            credentials = {'username': usr, 'password': pwd} if self.ui.host_box.isHidden() \
                else {'username': usr, 'password': pwd, 'host': host}
            self.loginClicked.emit(credentials)

    def loginSuccessful(self, status, client_callback=None):
        self.stopProgress()
        self.setCurrentWidget(self.ui.login_page)
        if status is True:
            for box in (self.ui.pass_box, self.ui.user_box, self.ui.host_box):
                box.clear()
            self.hide()
        else:
            self.ui.pass_box.clear()
        self.sigLoggedIn.emit(status)


    def setCurrentWidget(self, widget):
        self.ui.stackedWidget.setCurrentWidget(widget)

    def startProgress(self):
        self.ui.progressBar.setRange(0, 0)

    def stopProgress(self):
        self.ui.progressBar.setRange(0, 1)

    def progressMessage(self, message):
        # Not working for some reason
        self.ui.progress_label.setText(message)

    def handleLogout(self):
        self.setCurrentWidget(self.ui.progress_page)
        self.progressMessage('Goodbye {}...'.format(self.ui.user_box.text()))
        self.startProgress()
        self.ui.user_box.clear()
        self.logoutClicked.emit()

    def logoutSuccessful(self):
        self.stopProgress()
        self.setCurrentWidget(self.ui.login_page)