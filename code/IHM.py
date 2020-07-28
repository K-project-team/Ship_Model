from PySide2.QtWidgets import QApplication,QWidget,QVBoxLayout,QGridLayout,QPushButton, QLabel,QFileDialog,QLineEdit,QCheckBox, QComboBox
from PySide2.QtGui import QIcon, QPixmap, Qt
from PySide2.QtCore import QSize
import threading
import time

from STLModel import *
from STLModelPressure import *
from STLModelDisplay import *
from Terminal import *
from configurations import *

class MainWindow(QWidget):
    """
    Créer la fenêtre principale
    """
    def __init__(self):
        QWidget.__init__(self)
        """
        PROCESSING ATTRIBUTES
        """
        self.loop_simulation = False
        self.parameters_window=None

        self.term = Terminal()
        self.stl_model = None
        self.stl_model_pressure = None
        self.stl_model_display = None

        self.object_mass = DEFAULT_OBJECT_MASS
        self.dichotomy_precision = DEFAULT_DICHOTOMY_PRECISION
        self.fluid_density = DEFAULT_FLUID_DENSITY

        self.show_draught = DEFAULT_SHOW_DRAUGHT

        self.setWindowTitle("G5 SIMULATION OBJECT FLOTABILITY")
        self.setFixedSize(1280,1024)

        self.main_layout=QVBoxLayout()
        self.main_layout.setMargin(0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        """
        TOPBAR WIDGETS
        """
        self.topbar_layout=QGridLayout()
        self.topbar_layout.setAlignment(Qt.AlignTop)
        self.topbar_layout.setSpacing(32)

        buttons_icons=['stl_file','parameters','prepare_simulation','start_simulation','loop_simulation','stop_simulation','generate_animation_gif']
        group_buttons_labels=['LOAD 3D MODEL','PARAMETERS','SIMULATION']
        buttons_slots=[self.loadSTLModel,self.displayParametersWindow,self.prepareSimulation,self.startSimulation,self.loopSimulation,self.stopSimulation,self.generateAnimationsGIF]
        buttons_tooltips=['Load 3d model','Set parameters','Prepare the simulation','Start the simulation','Loop the simulation','Stop the simulation','Generate animations GIF']
        self.buttons=[QPushButton() for i in range(7)]
        for i,button in enumerate(self.buttons):
            button.setIcon(QIcon(ICONS_FOLDER+buttons_icons[i]+'_icon.png'))
            button.setIconSize(QSize(50, 50))
            button.setStyleSheet('border:none; margin-top : 24px;')
            button.clicked.connect(buttons_slots[i])
            button.setToolTip(buttons_tooltips[i])
            if i>0: button.setDisabled(True)
            self.topbar_layout.addWidget(button,0,i,1,1)

        for i,group_buttons_label in enumerate(group_buttons_labels):
            label=QLabel(group_buttons_label)
            label.setFixedHeight(32)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('border-top : 2px solid #dfdfdf; font-family: Calibri; font-size : 10pt; color: #2C3E50;')
            self.topbar_layout.addWidget(label, 1,i,1, 1 if i!=2 else 5)
        self.main_layout.addLayout(self.topbar_layout)

        """
        BODY_WIDGETS
        """
        self.body_layout = QGridLayout()
        self.body_layout.setSpacing(0)

        self.stl_model_graph=QLabel()
        self.stl_model_graph.setPixmap(QPixmap(DEFAULT_STL_MODEL_GRAPH_FOLDER))
        self.stl_model_graph.setFixedSize(640,480)

        self.draught_graph=QLabel()
        self.draught_graph.setPixmap(QPixmap(DEFAULT_DRAUGHT_GRAPH_FOLDER))
        self.draught_graph.setFixedSize(640,480)

        self.body_layout.addWidget(self.stl_model_graph,0,0,1,1)
        self.body_layout.addWidget(self.draught_graph, 0, 1, 1, 1)

        self.colored_parts_legend=QLabel()
        self.colored_parts_legend.setPixmap(QPixmap(LEGEND_FOLDER+'colored_parts_legend.png'))
        self.colored_parts_legend.setStyleSheet('padding : 0 0 13px 24px; background : #fff')
        self.body_layout.addWidget(self.colored_parts_legend, 1, 0, 1, 2)

        self.draught_legend = QLabel()
        self.draught_legend.setPixmap(QPixmap(LEGEND_FOLDER + 'draught_legend.png'))
        self.draught_legend.setStyleSheet('padding : 0 0 13px 24px; background : #fff')
        self.draught_legend.hide()
        self.body_layout.addWidget(self.draught_legend, 2, 0, 1, 2)

        self.term.setFixedWidth(1280)
        self.main_layout.addLayout(self.body_layout)
        self.main_layout.addWidget(self.term)

        self.show()

    def updatePreview(self,show_draught=False):
        self.stl_model_display.emptyFolder(STL_MODEL_LOADED_VIEW_FOLDER)
        self.stl_model_display.saveSTLModelGraph(STL_MODEL_LOADED_VIEW_FOLDER, 'preview',show_draught)
        self.term.addProcessMessage('Displaying of the updated preview of the STL model')
        self.stl_model_graph.setPixmap(QPixmap(STL_MODEL_LOADED_VIEW_FOLDER + 'preview.png'))

    def loadSTLModel(self):
        """
        Charger la maquette du fichier STL sélectionné et afficher un aperçu
        """
        ### BEFORE PROCESS
        for i in range(1,7):
            self.buttons[i].setDisabled(True)
        ### START_PROCESS
        self.explorer = QFileDialog()
        self.explorer.setNameFilter("*.stl")
        if self.explorer.exec_():
            self.stl_model=STLModel(self.explorer.selectedFiles()[0],self.term)
            if self.stl_model.facets_number!=0:
                self.initial_bottom_ref=self.stl_model.bottom_ref
                self.stl_model_display=STLModelDisplay(self.stl_model,self.term)

                self.updatePreview()

                ### END_PROCESS
                self.buttons[1].setDisabled(False)
                self.buttons[2].setDisabled(False)
                self.term.addSuccessMessage('STL model properly loaded')

    def displayParametersWindow(self):
        """
        Appeler la classe ParametersWindow pour afficher la fenêtre de paramètres
        """
        self.term.addInformativeMessage('Display the parameters window')
        self.parameters_window=ParametersWindow(self)

    def prepareSimulation(self):
        """
        Lancer l'algorithme de dichotomie et enregistrer les graphiques étape par étape
        """
        ### BEFORE_PROCESS
        self.buttons[2].setDisabled(True)

        # reset
        self.stl_model.translateZ(self.initial_bottom_ref-self.stl_model.bottom_ref)
        self.updatePreview(self.show_draught)

        if isinstance(self.parameters_window,ParametersWindow):
            self.parameters_window.close()
        for i in range(7):
            if i!=2: self.buttons[i].setDisabled(True)
        X,Y=[0],[-self.stl_model.bottom_ref if self.stl_model.bottom_ref<0 else 0]

        self.stl_model_display.emptyFolder(STL_MODEL_GRAPHS_FOLDER)
        self.stl_model_display.emptyFolder(DRAUGHT_GRAPHS_FOLDER)

        self.stl_model_display.saveSTLModelGraph(STL_MODEL_GRAPHS_FOLDER,FRAMES_BASENAME+'0')
        self.stl_model_display.saveDraughGraph(FRAMES_BASENAME+'0', X,Y,self.dichotomy_precision)

        self.stl_model_pressure=STLModelPressure(self.stl_model,self.term)

        self.stl_model.setMass(self.object_mass)
        self.stl_model_pressure.setFluidDensity(self.fluid_density)
        ### START_PROCESS
        self.term.addProcessMessage('Launching the dichotomy algorithm')
        while self.stl_model_pressure.draught_range[1]-self.stl_model_pressure.draught_range[0]>self.dichotomy_precision:
            Y.append(self.stl_model_pressure.dichotomy())
            X.append(self.stl_model_pressure.dichotomy_achieved)
            self.stl_model_display.saveSTLModelGraph(STL_MODEL_GRAPHS_FOLDER,FRAMES_BASENAME + str(self.stl_model_pressure.dichotomy_achieved),self.show_draught)
            self.stl_model_display.saveDraughGraph(FRAMES_BASENAME + str(self.stl_model_pressure.dichotomy_achieved), X, Y,self.dichotomy_precision)
        self.term.addSuccessMessage('Preparation of the simulation complete')
        ### END_PROCESS
        for i in range(7):
            if i!=5: self.buttons[i].setDisabled(False)
            if i==2: self.buttons[i].setDisabled(True)

    def startSimulation(self):
        """
        Lancer l'animation des graphiques en asynchrone pour ne pas bloquer les clicked event
        """
        thread=threading.Thread(target=self._startSimulation)
        thread.start()

    def _startSimulation(self):
        """
        Recuperer et afficher avec une temporisation les images des graphiques afin de constituer l'animation
        """
        ### BEFORE PROCESS
        for i in range(7):
            if i!=5: self.buttons[i].setDisabled(True)

        self.term.addProcessMessage('Recovery of all the images needed for the animation')
        stl_model_frames = os.listdir(STL_MODEL_GRAPHS_FOLDER)
        stl_model_frames = sorted(stl_model_frames, key=lambda frame: int(frame.replace(FRAMES_BASENAME, '').split('.')[0]))
        stl_draught_frames = os.listdir(DRAUGHT_GRAPHS_FOLDER)
        stl_draught_frames = sorted(stl_draught_frames, key=lambda frame: int(frame.replace(FRAMES_BASENAME, '').split('.')[0]))
        self.term.addSuccessMessage('All the images have been recovered')
        self.term.addInformativeMessage('Launching simulation animation')
        frames_number = len(stl_model_frames)
        if frames_number == len(stl_draught_frames):
            for i in range(frames_number):
                self.stl_model_graph.setPixmap(STL_MODEL_GRAPHS_FOLDER + stl_model_frames[i])
                self.draught_graph.setPixmap(DRAUGHT_GRAPHS_FOLDER + stl_draught_frames[i])
                time.sleep(.1)
            while self.loop_simulation:
                for i in range(frames_number):
                    self.stl_model_graph.setPixmap(STL_MODEL_GRAPHS_FOLDER + stl_model_frames[i])
                    self.draught_graph.setPixmap(DRAUGHT_GRAPHS_FOLDER + stl_draught_frames[i])
                    time.sleep(.1)
            self.term.addSuccessMessage('Animation of the simulation correctly carried out')
            for i in range(7):
                if i in [0,1,3,4,6]: self.buttons[i].setDisabled(False)
        else:
            self.term.addErrorMessage('An error occurred during frames synchronization')

    def loopSimulation(self):
        """
        Activer ou désactive la répétition infinie de l'animation
        """
        self.loop_simulation=not self.loop_simulation
        loop_button=self.buttons[4]
        stop_button=self.buttons[5]
        loop_icon='loop_simulation_icon.png'
        if self.loop_simulation:
            loop_icon='selected_'+loop_icon
            stop_button.setDisabled(False)
            self.term.addInformativeMessage('The displayed simulation will now be looped')
        else:
            stop_button.setDisabled(True)
            self.term.addInformativeMessage('The displayed simulation will now be played only once')
        loop_button.setIcon(QIcon(ICONS_FOLDER+loop_icon))

    def stopSimulation(self):
        """
        Interrompre la boucle pour arrêter l'animation
        """
        self.loop_simulation=False
        loop_button=self.buttons[4]
        stop_button = self.buttons[5]
        loop_button.setIcon(QIcon(ICONS_FOLDER+'loop_simulation_icon.png'))
        stop_button.setDisabled(True)
        self.term.addInformativeMessage('Simulation properly stopped')

    def generateAnimationsGIF(self):
        """
        Générer et télécharger des GIF de la simulation produite
        """
        self.stl_model_display.generateGIFAnimations()

class ParametersWindow(QWidget):
    """
    Créer la fenêtre des paramètres
    """
    def __init__(self,settings):
        QWidget.__init__(self)
        self.settings=settings

        self.setWindowTitle('PARAMETERS')
        self.setFixedSize(360,500)

        self.main_layout=QGridLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        calculous_parameters_label=QLabel('CALCULOUS PARAMETERS')
        calculous_parameters_label.setAlignment(Qt.AlignCenter)
        calculous_parameters_label.setFixedHeight(58)
        calculous_parameters_label.setStyleSheet('font-family: Calibri; font-size : 10pt; color: #2C3E50;')
        self.main_layout.addWidget(calculous_parameters_label,0,0,1,2)

        object_mass_label=QLabel('Object mass (kg)')
        object_mass_label.setStyleSheet('font-family: Calibri; font-size : 10pt; color: #2C3E50;')
        object_mass_label.setFixedHeight(32)
        self.main_layout.addWidget(object_mass_label,1,0,1,1)

        self.object_mass_input=QLineEdit()
        self.object_mass_input.setAlignment(Qt.AlignRight)
        self.object_mass_input.setText(str(self.settings.object_mass))
        self.object_mass_input.textChanged.connect(self.updateObjectMass)
        self.main_layout.addWidget(self.object_mass_input,1,1,1,1)

        dichotomy_precision_label=QLabel('Dichotomy precision')
        dichotomy_precision_label.setFixedHeight(32)
        dichotomy_precision_label.setStyleSheet('font-family: Calibri; font-size : 10pt; color: #2C3E50;')
        self.main_layout.addWidget(dichotomy_precision_label,2,0,1,1)

        self.dichotomy_precision_input = QLineEdit()
        self.dichotomy_precision_input.setAlignment(Qt.AlignRight)
        self.dichotomy_precision_input.setText(str(self.settings.dichotomy_precision))
        self.dichotomy_precision_input.textChanged.connect(self.updateDichotomyPrecision)
        self.main_layout.addWidget(self.dichotomy_precision_input,2, 1, 1, 1)

        fluid_density_label=QLabel('Fluid density (kg/m3)')
        fluid_density_label.setFixedHeight(32)
        fluid_density_label.setStyleSheet('font-family: Calibri; font-size : 10pt; color: #2C3E50;')
        self.main_layout.addWidget(fluid_density_label, 3, 0, 1, 1)

        self.fluid_density_options=QComboBox()
        if self.settings.fluid_density==SALTWATER_DENSITY:
            self.fluid_density_options.addItem('saltwater ('+str(SALTWATER_DENSITY)+' kg/m3)')
            self.fluid_density_options.addItem('freshwater ('+str(FRESHWATER_DENSITY)+' kg/m3)')
        else:
            self.fluid_density_options.addItem('freshwater ('+str(FRESHWATER_DENSITY)+' kg/m3)')
            self.fluid_density_options.addItem('saltwater ('+str(SALTWATER_DENSITY)+' kg/m3)')
        self.fluid_density_options.addItem('Other')
        self.fluid_density_options.activated.connect(self.updateFluidDensityWithOption)
        self.main_layout.addWidget(self.fluid_density_options,3,1,1,1)

        self.fluid_density_input=QLineEdit()
        self.fluid_density_input.setAlignment(Qt.AlignRight)
        self.fluid_density_input.textChanged.connect(self.updateFluidDensityWithInput)
        if self.settings.fluid_density in [FRESHWATER_DENSITY,SALTWATER_DENSITY]:
            self.fluid_density_input.hide()
        else:
            self.fluid_density_input.setText(str(self.settings.fluid_density))
        self.main_layout.addWidget(self.fluid_density_input, 4, 1, 1, 1)

        display_parameters_label = QLabel('DISPLAY PARAMETERS')
        display_parameters_label.setAlignment(Qt.AlignCenter)
        display_parameters_label.setFixedHeight(58)
        display_parameters_label.setStyleSheet('font-family: Calibri; font-size : 10pt; color: #2C3E50;')
        self.main_layout.addWidget(display_parameters_label, 5, 0, 1, 2)

        show_draught_label=QLabel('Show draught')
        show_draught_label.setFixedHeight(32)
        show_draught_label.setStyleSheet('font-family: Calibri; font-size : 10pt; color: #2C3E50;')
        self.main_layout.addWidget(show_draught_label, 6, 0, 1, 1)
        self.show_draught_checkbox=QCheckBox()
        self.show_draught_checkbox.stateChanged.connect(self.updateShowDraught)
        self.show_draught_checkbox.setCheckState(Qt.CheckState.Checked if self.settings.show_draught else Qt.CheckState.Unchecked)
        self.main_layout.addWidget(self.show_draught_checkbox, 6, 1, 1, 1)

        self.show()

    def updateObjectMass(self):
        """
        Mettre à jour la masse entrée par l'utilisateur
        """
        try:
            if float(self.object_mass_input.text())!=self.settings.object_mass:
                self.settings.object_mass=float(self.object_mass_input.text())
                self.lockSimulationButtons()
                self.settings.term.addSuccessMessage('The mass you entered is in a valid format')
        except Exception:
            self.settings.term.addErrorMessage('The mass you entered is not in a valid format')
        finally:
            pass

    def updateDichotomyPrecision(self):
        """
        Mettre à jour la précision entrée par l'utilisateur
        """
        try:
            if float(self.dichotomy_precision_input.text())!=self.settings.dichotomy_precision:
                self.settings.dichotomy_precision=float(self.dichotomy_precision_input.text())
                self.lockSimulationButtons()
                self.settings.term.addSuccessMessage('The dichotomy_precision you entered is in a valid format')
        except Exception:
            self.settings.term.addErrorMessage('The dichotomy_precision you entered is not in a valid format')
        finally:
            pass

    def updateFluidDensityWithOption(self):
        """
        Mettre à jour la densité sélectionnée par l'utilisateur
        """
        option=self.fluid_density_options.currentText()
        if option=='Other':
            self.fluid_density_input.show()
        else:
            self.fluid_density_input.hide()
            if option=='freshwater ('+str(FRESHWATER_DENSITY)+' kg/m3)':
                if self.settings.fluid_density!=FRESHWATER_DENSITY:
                    self.settings.fluid_density=FRESHWATER_DENSITY
                    self.lockSimulationButtons()
            else:
                if self.settings.fluid_density!=SALTWATER_DENSITY:
                    self.settings.fluid_density=SALTWATER_DENSITY
                    self.lockSimulationButtons()
            self.settings.term.addSuccessMessage('The density of the fluid has correctly been changed')

    def updateFluidDensityWithInput(self):
        """
        Permettre à l'utilisateur d'entrer une densité de lui-même
        """
        try:
            if float(self.fluid_density_input.text())!=self.settings.fluid_density:
                self.settings.fluid_density = float(self.fluid_density_input.text())
                self.lockSimulationButtons()
                self.settings.term.addSuccessMessage('The fluid density you entered is in a valid format')
        except Exception:
            self.settings.term.addErrorMessage('The fluid density entered is not in a valid format')
        finally:
            pass

    def updateShowDraught(self):
        """
        Afficher le tirant d'eau si l'utilisateur le désire
        """
        if self.show_draught_checkbox.isChecked()!=self.settings.show_draught:
            self.settings.show_draught=self.show_draught_checkbox.isChecked()
            self.lockSimulationButtons()
            if self.settings.show_draught:
                self.settings.draught_legend.show()
            else:
                self.settings.draught_legend.hide()
            self.settings.term.addSuccessMessage('Show draught has correctly changed')

            self.settings.updatePreview(self.settings.show_draught)

    def lockSimulationButtons(self):
        """
        Désactiver certains boutons lors de la modification des paramètres
        """
        for i in range(3,7):
            self.settings.buttons[i].setDisabled(True)
        self.settings.buttons[2].setDisabled(False)

if __name__=='__main__':
    app = QApplication([])
    main_window=MainWindow()
    app.exec_()
