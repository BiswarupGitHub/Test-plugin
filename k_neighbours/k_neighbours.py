# -*- coding: utf-8 -*-
"""
/***************************************************************************
 kneighbours
                                 A QGIS plugin
 K Neighbours plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-11-08
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Biswarup Deb
        email                : biswarup.2622@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .k_neighbours_dialog import kneighboursDialog
from sklearn.linear_model import LogisticRegression
import os.path

import tensorflow as tf
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd
import gzip

#matplotlib inline
ina = "E:\\Nesac_py\\plugin project\\pixel-data_60m\\pixel_data\\60m\\PNL_A018780_20201010_60m.csv"
with open(ina, 'rb') as fd1:
    gzip_fd1 = gzip.GzipFile(fileobj=fd1)
    data1 = pd.read_csv(gzip_fd1)
    #print(data1.iloc[0])
    
#Second satellite image
inb = 'E:\\Nesac_py\\plugin project\\pixel-data_60m\\pixel_data\\60m\\PQM_A018880_20201017_60m.csv'
with open(inb, 'rb') as fd2:
    gzip_fd2 = gzip.GzipFile(fileobj=fd2)
    data2 = pd.read_csv(gzip_fd2)
    #print(data2.iloc[0])

data = pd.concat([data1, data2], ignore_index=True)
#print(data)

xallpd = data.iloc[:, 2:]
indpd = data.iloc[:,0]
yallpd = data.iloc[:,1]

xall = pd.DataFrame(xallpd).to_numpy()
indall = pd.DataFrame(indpd).to_numpy()
yall = pd.DataFrame(yallpd).to_numpy()

yall[yall==1] = 0
yall[yall==2] = 1

# print(np.count_nonzero(yall==0))
# print(np.count_nonzero(yall==1))

inc = "E:\\Nesac_py\\plugin project\\pixel-data_60m\\pixel_data\\60m\\PNM_A027474_20200925T082711_60m.csv"
with open(inc, 'rb') as fd3:
    gzip_fd3 = gzip.GzipFile(fileobj=fd3)
    data3 = pd.read_csv(gzip_fd3) 

xallpd_test = data3.iloc[:, 2:]
indpd_test = data3.iloc[:,0]
yallpd_test = data3.iloc[:,1]
#print(data3.iloc[0])

xall_test = pd.DataFrame(xallpd_test).to_numpy()
indall_test = pd.DataFrame(indpd_test).to_numpy()
yall_test = pd.DataFrame(yallpd_test).to_numpy()

yall_test[yall_test==1] = 0
yall_test[yall_test==2] = 1


#.....................................................................PRINCIPAL COMPONENT ANALYSIS FOR TEST.............................................................

from sklearn.decomposition import PCA
pca = PCA(n_components=3)
pcacomp = pca.fit_transform(xall)

xall = pcacomp

pca_test = PCA(n_components=3)
pcacomp_test = pca_test.fit_transform(xall_test)

xall_test = pcacomp_test

from sklearn import preprocessing
import random

# Let's shuffle the data
alltog1 = np.append(xall, indall, axis=1)
alltog = np.append(alltog1, yall, axis=1)
np.random.shuffle(alltog)

xall = alltog[:,:-2]
indall = alltog[:,-2]
yall = alltog[:,-1]

x_train = xall
y_train = yall
  
scaler = preprocessing.StandardScaler().fit(x_train)
x_train = scaler.transform(x_train)

# Check prints
# print(np.shape(x_train))
# print(np.shape(y_train))

# # Let's shuffle the data
alltog1_test = np.append(xall_test, indall_test, axis=1)
alltog_test = np.append(alltog1_test, yall_test, axis=1)
np.random.shuffle(alltog_test)

xall_test = alltog_test[:,:-2]
indall_test = alltog_test[:,-2]
yall_test = alltog_test[:,-1]

x_test = xall_test
y_test = yall_test

scaler2 = preprocessing.StandardScaler().fit(x_test)
x_test = scaler2.transform(x_test)

# print(np.shape(x_test))
# print(np.shape(y_test))

from sklearn.neighbors import KNeighborsClassifier


class kneighbours:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'kneighbours_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&K Neighbours')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('kneighbours', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/k_neighbours/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'K Neighbours'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&K Neighbours'),
                action)
            self.iface.removeToolBarIcon(action)
    
    def select_output_file(self):
      filename, _filter = QFileDialog.getSaveFileName(
        self.dlg, "Select   output file ","", '*.txt')
      self.dlg.lineEdit_4.setText(filename)

    def select_output_file_a(self):
      filename, _filter = QFileDialog.getSaveFileName(
        self.dlg, "Select   output file ","", '*.txt')
      self.dlg.lineEdit_5.setText(filename)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = kneighboursDialog()
            self.dlg.pushButton_4.clicked.connect(self.select_output_file)
            self.dlg.pushButton_5.clicked.connect(self.select_output_file_a)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            knn = KNeighborsClassifier(n_neighbors=8)
            knn.fit(x_train,y_train.flatten())
            knnpre = knn.predict(x_test)

            y_knnpre = np.append(knnpre.reshape((np.shape(x_test)[0],1)), indall_test.reshape((np.shape(x_test)[0],1)), axis=1)

            # # Check prints
            # #print(knnpre[:10])
            # #print(y_test.flatten()[:10])

            # # Naive implementation for calculating prediction accuracy
            # #knnsum = sum(x == y for x, y in zip(knnpre, y_test.flatten()))
            # #knnacc = knnsum / float(len(knnpre))
            # #print(knnacc)

            # print(knn.score(x_train, y_train))
            # print(knn.score(x_test, y_test))

            # Let's save the obtained predictions into a txt file
            np.savetxt(self.dlg.lineEdit_4.text(), y_knnpre, delimiter=',')

            

            # Try out different C values and see how it affects prediction accuracy!
            logre = LogisticRegression(C=1e-6)
            logre.fit(x_train, y_train.flatten())
            logpre = logre.predict(x_test)

            y_logpre = np.append(logpre.reshape((np.shape(x_test)[0],1)), indall_test.reshape((np.shape(x_test)[0],1)), axis=1)

            # Check prints
            #print(logpre[:10])
            #print(y_test.flatten()[:10])

            print(logre.score(x_train, y_train))
            print(logre.score(x_test, y_test))

            # Let's save the obtained predictions into a txt file
            np.savetxt(self.dlg.lineEdit_5.text(), y_logpre, delimiter=',')