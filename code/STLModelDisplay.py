# import matplotlib; matplotlib.use("TkAgg")
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
from PIL import Image
import os
from configurations import *

class STLModelDisplay:
    def __init__(self,stl_model,term):
        self.stl_model=stl_model
        self.term=term

    def prepareSTLModelGraph(self,show_draught=False):
        """
        Créer le graphique 3d pour le fichier STL
        :param show_draught: afficher ou non le trait permettant de visualiser le tirant d'eau
        :return: l'objet figure
        """
        fig=plt.figure()
        axis = fig.add_subplot(projection='3d')
        axis.set_xlabel('x-axis')
        axis.set_ylabel('y-axis')
        axis.set_zlabel('z-axis')

        axis.view_init(elev=VIEW_ELEV, azim=VIEW_AZIM)

        axis.set_xlim3d(self.stl_model.x_range[0] - X_MARGIN, self.stl_model.x_range[1] + X_MARGIN)
        axis.set_ylim3d(self.stl_model.y_range[0] - Y_MARGIN, self.stl_model.y_range[1] + Y_MARGIN)
        axis.set_zlim3d(-self.stl_model.height if self.stl_model.height!=0 else -1,self.stl_model.height if self.stl_model.height!=0 else 1)

        submerged_facets_flatten = self.stl_model.submerged_facets.reshape(3 * self.stl_model.submerged_facets_number,3)
        axis.add_collection3d(Poly3DCollection(submerged_facets_flatten, linewidths=0.4, edgecolors=SUBMERGED_PART_BORDER_COLOR, facecolors=SUBMERGED_PART_COLOR))

        emerged_facets_flatten = self.stl_model.emerged_facets.reshape(3 * len(self.stl_model.emerged_facets), 3)
        axis.add_collection3d(Poly3DCollection(emerged_facets_flatten, linewidths=0.4, edgecolors=EMERGED_PART_BORDER_COLOR, facecolors=EMERGED_PART_COLOR))

        if show_draught:
            axis.quiver(0,self.stl_model.y_range[0]-Y_MARGIN/2, 0, 0, 0, -1, length=-self.stl_model.bottom_ref if self.stl_model.bottom_ref<0 else 0, color=DRAUGHT_LINE_COLOR, arrow_length_ratio=0,pivot='tail')
        return fig


    def showSTLModel(self,show_draught=False):
        """
        Afficher le graphique 3d pour visualiser les facettes contenues dans fichier STL
        :param show_draught: afficher ou non le trait permettant de visualiser le tirant d'eau
        """
        self.term.addProcessMessage('Preparing the display of the 3d model')
        fig=self.prepareSTLModelGraph(show_draught)
        plt.show()
        plt.close(fig)
        self.term.addSuccessMessage('3d model displayed')

    def saveSTLModelGraph(self,folder,filename,show_draught=False):
        """
        Enregistrer une image du graphique 3d du fichier STL
        :param folder: dossier destiné à accueillir l'image
        :param filename: nom à donner au fichier image
        :param show_draught: afficher ou non le trait permettant de visualiser le tirant d'eau
        """
        self.term.addProcessMessage('Recording the 3d graph \''+folder+filename+'.png\'')
        fig=self.prepareSTLModelGraph(show_draught)
        plt.savefig(folder+filename)
        plt.close(fig)
        self.term.addSuccessMessage('3d graph saved')

    def prepareDraughGraph(self,X,Y,dichotomy_precision):
        """
        Créer le graphique 2d pour tracer la courbe de l'évolution du tirant d'eau
        :param X: liste des valeurs pour l'axe des abscisses
        :param Y: liste des valeurs pour l'axe des ordonnées
        :return: l'objet figure
        """
        fig = plt.figure()

        axis = fig.add_subplot()

        axis.set_title('Draught\'s evolution')
        axis.set_xlabel('Number of iterations of the dichotomy algorithm')
        axis.set_ylabel('Draught (m)')
        axis.set_xticks(X)
        axis.set_ylim(0,self.stl_model.height if self.stl_model.height!=0 else 1)

        axis.plot(X,Y,marker='p',color=DRAUGHT_LINE_COLOR)
        plt.text(0,self.stl_model.height*0.9 if self.stl_model.height!=0 else 0.9,'Current draught value : '+str(round(Y[-1],str(float(dichotomy_precision)).count('0')))+' m',color=DRAUGHT_LINE_COLOR)

        return fig

    def showDraughGraph(self,X,Y,dichotomy_precision):
        """
        Afficher le graphique 2d pour visualiser l'évolution du tirant d'eau en fonction du nombre de dichotomie effectuée
        :param X: liste des valeurs pour l'axe des abscisses
        :param Y: liste des valeurs pour l'axe des ordonnées
        """
        self.term.addProcessMessage('Preparing the display of the draught graph')
        fig = self.prepareDraughGraph(X,Y,dichotomy_precision)
        plt.show()
        plt.close(fig)
        self.term.addSuccessMessage('Draught graph displayed')

    def saveDraughGraph(self,filename,X,Y,dichotomy_precision):
        """
        Enregistrer une image du graphique 2d du tirant d'eau
        :param filename: nom à donner au fichier image
        :param X: liste des valeurs pour l'axe des abscisses
        :param Y: liste des valeurs pour l'axe des ordonnées
        """
        self.term.addProcessMessage('Recording the 2d graph \''+DRAUGHT_GRAPHS_FOLDER+filename+'.png\'')
        fig=self.prepareDraughGraph(X,Y,dichotomy_precision)
        plt.savefig(DRAUGHT_GRAPHS_FOLDER + filename)
        plt.close(fig)
        self.term.addSuccessMessage('2d graph saved')

    def generateGIFAnimations(self):
        """
        Génerer les GIF avec les images contenues dans les dossiers en question
        """
        animations=os.listdir(ANIMATIONS_FOLDER)
        if len(animations)==0:
            animations_saved_number=0
        else:
            animations=sorted([int(animation.replace(ANIMATION_FOLDER_BASENAME,'')) for animation in animations])
            animations_saved_number=animations[-1]
        new_animation_folder=ANIMATIONS_FOLDER+ANIMATION_FOLDER_BASENAME+str(animations_saved_number+1)+'/'
        os.mkdir(new_animation_folder)
        self.term.addProcessMessage('Creation of animations in gif format')
        self.term.addSubProcessMessage('Creation of the animation of the 3d model')
        self._generateGIFAnimationFromFolder(STL_MODEL_GRAPHS_FOLDER,new_animation_folder,'3d_model_animation')
        self.term.addSubProcessMessage('Creation of the animation of the draught graph')
        self._generateGIFAnimationFromFolder(DRAUGHT_GRAPHS_FOLDER,new_animation_folder,'draught_evolution_animation')
        self.term.addSuccessMessage('Creation of animations complete\nFiles saved in \''+new_animation_folder+'\'')

    def _generateGIFAnimationFromFolder(self,fromfolder,tofolder,filename):
        """
        Récupérer les images du dossier fromfolder, créer un GIF nommée filename et le sauvegarder dans tofolder
        :param fromfolder: dossier contenant les images
        :param tofolder: dossier dans lequel sera enregistré le GIF
        :param filename: nom du fichier GIF enregistré
        :return:
        """
        frames = os.listdir(fromfolder)
        frames_number = len(frames)
        if frames_number == 0:
            self.term.addErrorMessage('Impossible to generate the animation from \'' + fromfolder + '\' : no recorded frames')
            return
        frames = sorted(frames, key=lambda frame: int(frame.replace(FRAMES_BASENAME,'').split('.')[0]))
        converted_frames = [Image.open(fromfolder + frame) for frame in frames]
        converted_frames[0].save(tofolder+filename+'.gif', format='GIF', append_images=converted_frames[1:], save_all=True, duration=GIF_DELAY_BETWEEN_TWO_FRAMES * frames_number, optimize=True, loop=0)

    def emptyFolder(self,folder):
        """
        Vider le dossier folder
        :param folder: chemin et nom du dossier à vider
        """
        frames = os.listdir(folder)
        if len(frames) != 0:
            for frame in frames:
                os.remove(folder + frame)