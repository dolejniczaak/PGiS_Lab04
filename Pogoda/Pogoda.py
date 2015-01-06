# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Pogoda
                                 A QGIS plugin
 Pogoda w wojewodztwach
                              -------------------
        begin                : 2015-01-03
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Dominika Olejniczak
        email                : d.olejniczaak@wp.pl
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from Pogoda_dialog import PogodaDialog
import os.path
from qgis.core import *
from PyQt4.QtCore import QVariant  
import json
import urllib
import processing
import time, calendar

class Pogoda:
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
            'Pogoda_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PogodaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pogoda')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Pogoda')
        self.toolbar.setObjectName(u'Pogoda')

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
        return QCoreApplication.translate('Pogoda', message)


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
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Pogoda/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Wyswietlanie pogody'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Pogoda'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
			szejp=QgsVectorLayer("C:/Program Files/QGIS Brighton/apps/qgis/python/plugins/Pogoda/wojewodztwa/wojewodztwa.shp", "Wojewodztwa", "ogr")
			current=calendar.timegm(time.gmtime())
			features = processing.features(szejp)
			data=[]
			current=calendar.timegm(time.gmtime())
			for feature in features:
				idx = szejp.fieldNameIndex('Data')
				data.append(feature.attributes()[idx])
			mimi=min(data)
			print mimi
			diffrence=current-mimi
			if diffrence>600:
				QgsMapLayerRegistry.instance().addMapLayer(szejp)
				# warsaw # zg # szczecin # gdansk # olsztyn # bialystok # lublin # rzeszow # katowice # krakow # opole # wroclaw # poznan # bydgoszcz # kielce # lodz#
				miasta=[3099434, 763166, 776069, 765876, 759734, 3096472, 3094802, 3090048, 3081368, 3088171, 3102014, 769250, 3093133, 756135, 3083829, 3080165]
				szejp.startEditing()
				for i in miasta:
						adres="http://api.openweathermap.org/data/2.5/group?units=metric&lang=pl&APPID=58c69221430719fc84f0a91477ee6a90&id="
						adres=adres+str(i)
						response = urllib.urlopen(adres)
						data = json.loads(response.read())
						data2=data["list"]
						wartosci=[]
						daty=[]
						for i in range(0, len(data2)):
							id=data2[i]['id']
							tmp=data2[i]['main']['temp']
							tmpmax=data2[i]['main']['temp_max']
							tmpmin=data2[i]['main']['temp_min']
							cisn=data2[i]['main']['pressure']
							wilg=data2[i]['main']['humidity']
							prw=data2[i]['wind']['speed']
							kw=data2[i]['wind']['deg']
							chm=data2[i]['clouds']['all']
							dt=calendar.timegm(time.gmtime())
							wartosci.append(id)
							wartosci.append(tmp)
							wartosci.append(tmpmax)
							wartosci.append(tmpmin)
							wartosci.append(cisn)
							wartosci.append(wilg)
							wartosci.append(prw)
							wartosci.append(kw)
							wartosci.append(chm)
							wartosci.append(dt)
							ff='"kod"='+str(wartosci[0])
							field_names = [field.name() for field in szejp.pendingFields() ]
							ids = [f.id() for f in szejp.getFeatures(QgsFeatureRequest().setFilterExpression(ff))]
							fields = szejp.pendingFields()
							i1=fields.indexFromName('Temp')
							i2=fields.indexFromName('TempMax')
							i3=fields.indexFromName('TempMin')
							i4=fields.indexFromName('Cisn')
							i5=fields.indexFromName('Wilg')
							i6=fields.indexFromName('PredkWia')
							i7=fields.indexFromName('KierWia')
							i8=fields.indexFromName('Chmury')
							i9=fields.indexFromName('Data')
							szejp.changeAttributeValue(ids[0],i1,wartosci[1])
							szejp.changeAttributeValue(ids[0],i2,wartosci[2])
							szejp.changeAttributeValue(ids[0],i3,wartosci[3])
							szejp.changeAttributeValue(ids[0],i4,wartosci[4])
							szejp.changeAttributeValue(ids[0],i5,wartosci[5])
							szejp.changeAttributeValue(ids[0],i6,wartosci[6])
							szejp.changeAttributeValue(ids[0],i7,wartosci[7])
							szejp.changeAttributeValue(ids[0],i8,wartosci[8])
							szejp.changeAttributeValue(ids[0],i9,wartosci[9])
							szejp.updateFields()
				szejp.commitChanges()
				adres2="http://api.openweathermap.org/data/2.5/group?units=metric&lang=pl&APPID=58c69221430719fc84f0a91477ee6a90&id="
				response2 = urllib.urlopen(adres2)
				dataa = json.loads(response2.read())
				plik=open("C:/Program Files/QGIS Brighton/apps/qgis/python/plugins/Pogoda/dane.json","w")
				plik.write(json.dumps(dataa))
				plik.close()

			else:
				QgsMapLayerRegistry.instance().addMapLayer(szejp)
			pass
