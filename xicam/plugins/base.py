from PySide import QtCore, QtGui
from pyqtgraph.parametertree import ParameterTree
from functools import partial
import widgets
from xicam import config
from xicam import models, xglobals
from xicam.plugins import explorer, login

activeplugin = None

# DEFAULTS
w = QtGui.QSplitter()
w.setOrientation(QtCore.Qt.Vertical)
w.setContentsMargins(0, 0, 0, 0)
l = QtGui.QVBoxLayout()
l.setContentsMargins(0, 0, 0, 0)
l.setSpacing(0)

loginwidget = login.LoginDialog()

import os
preview = widgets.previewwidget()
w.addWidget(preview)

fileexplorer = explorer.MultipleFileExplorer(w)
filetree = fileexplorer.explorers['Local'].file_view

fileexplorer.sigLoginRequest.connect(loginwidget.loginRequest)
fileexplorer.sigLoginSuccess.connect(loginwidget.loginSuccessful)
fileexplorer.sigPreview.connect(preview.loaditem)

l.addWidget(loginwidget)
l.addWidget(fileexplorer)

booltoolbar = QtGui.QToolBar()

booltoolbar.actionTimeline = QtGui.QAction(QtGui.QIcon('gui/icons_26.png'), 'Timeline', w)
booltoolbar.actionAdd = QtGui.QAction(QtGui.QIcon('gui/icons_11.png'), 'actionAdd', w)
booltoolbar.actionSubtract = QtGui.QAction(QtGui.QIcon('gui/icons_13.png'), 'actionSubtract', w)
booltoolbar.actionAdd_with_coefficient = QtGui.QAction(QtGui.QIcon('gui/icons_14.png'), 'actionAdd_with_coefficient', w)
booltoolbar.actionSubtract_with_coefficient = QtGui.QAction(QtGui.QIcon('gui/icons_15.png'),
                                                            'actionSubtract_with_coefficient', w)
booltoolbar.actionDivide = QtGui.QAction(QtGui.QIcon('gui/icons_12.png'), 'actionDivide', w)
booltoolbar.actionAverage = QtGui.QAction(QtGui.QIcon('gui/icons_16.png'), 'actionAverage', w)

booltoolbar.addAction(booltoolbar.actionTimeline)
booltoolbar.addAction(booltoolbar.actionAdd)
booltoolbar.addAction(booltoolbar.actionSubtract)
booltoolbar.addAction(booltoolbar.actionAdd_with_coefficient)
booltoolbar.addAction(booltoolbar.actionSubtract_with_coefficient)
booltoolbar.addAction(booltoolbar.actionDivide)
booltoolbar.addAction(booltoolbar.actionAverage)
booltoolbar.setIconSize(QtCore.QSize(32, 32))
l.addWidget(booltoolbar)

panelwidget = QtGui.QWidget()
panelwidget.setLayout(l)
w.addWidget(panelwidget)
w.setSizes([250, w.height() - 250])

leftwidget = w


class plugin(QtCore.QObject):
    name = 'Unnamed Plugin'
    sigUpdateExperiment = QtCore.Signal()
    hidden = False

    def __init__(self, placeholders):
        super(plugin, self).__init__()

        self.placeholders = placeholders

        if not hasattr(self, 'centerwidget'):
            self.centerwidget = None

        if not hasattr(self, 'rightwidget'):
            w = QtGui.QWidget()
            l = QtGui.QVBoxLayout()
            l.setContentsMargins(0, 0, 0, 0)

            configtree = ParameterTree()
            configtree.setParameters(config.activeExperiment, showTop=False)
            config.activeExperiment.sigTreeStateChanged.connect(self.sigUpdateExperiment)
            l.addWidget(configtree)

            self.propertytable = widgets.frameproptable()
            #
            # propertytable.verticalHeader().hide()
            # propertytable.horizontalHeader().hide()

            # propertytable.horizontalHeader().setStretchLastSection(True)
            l.addWidget(self.propertytable)
            w.setLayout(l)
            self.rightwidget = w

        if not hasattr(self, 'bottomwidget'):
            self.bottomwidget = None

        if not hasattr(self, 'leftwidget'):
            self.leftwidget = leftwidget
            self.filetree = filetree
            self.booltoolbar = booltoolbar
            self.loginwidget = loginwidget

        if not hasattr(self, 'toolbar'):
            self.toolbar = None

        for widget, placeholder in zip(
                [self.centerwidget, self.rightwidget, self.bottomwidget, self.toolbar, self.leftwidget],
                self.placeholders):
            if widget is not None and placeholder is not None:
                placeholder.addWidget(widget)

    def openSelected(self, operation=None, operationname=None):
        indices = self.filetree.selectedIndexes()
        paths = [self.filetree.filetreemodel.filePath(index) for index in indices]

        self.openfiles(paths, operation, operationname)

    def openfiles(self, files, operation=None, operationname=None):
        pass

    @property
    def isActive(self):
        return activeplugin == self

    def opendirectory(files, operation=None):
        pass

    def addfiles(files, operation=None):
        pass

    def calibrate(self):
        self.centerwidget.currentWidget().widget.calibrate()

    def activate(self):

        for widget, placeholder in zip(
                [self.centerwidget, self.rightwidget, self.bottomwidget, self.toolbar, self.leftwidget],
                self.placeholders):
            if widget is not None and placeholder is not None:
                placeholder.setCurrentWidget(widget)
                placeholder.show()
            if widget is None and placeholder is not None:
                placeholder.hide()

        global activeplugin
        activeplugin = self

    def currentImage(self):
        pass