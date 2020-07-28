import numpy as np
from configurations import *

class STLModelPressure:
    def __init__(self, stl_model,term):
        self.stl_model=stl_model
        self.term=term

        self.draught_range=[-DEPTH_COEFFICIENT*self.stl_model.height if self.stl_model.height!=0 else -1,0]
        self.dichotomy_achieved=0

        self.fluid_density=DEFAULT_FLUID_DENSITY

    def setFluidDensity(self,fluid_density):
        """
        Définir la densité du fluide
        :param fluid_density: densité du fluide dans lequel l'objet est immergé
        """
        self.term.addInformativeMessage('Fluid density set to '+str(fluid_density)+' kg/m3')
        self.fluid_density=fluid_density

    def calc_submerged_facets_surfaces(self):
        """
        Calculer les surfaces de toutes les facettes immergées
        :return: numpy array des surfaces des facettes immergées
        """
        self.term.addSubProcessMessage('Calculation of submerged facet surfaces')
        submerged_facet_surfaces=[]
        for i in range(self.stl_model.submerged_facets_number):
            A,B,C=self.stl_model.submerged_facets[i]
            submerged_facet_surfaces.append(np.linalg.norm(np.cross(B-A,C-A))/2*self.stl_model.submerged_facet_normal[i])
        return np.array(submerged_facet_surfaces)

    def calc_submerged_facets_z_means(self):
        """
        Calculer les altitudes moyennes des facettes immergées
        :return: numpy array des z moyens des facettes immergées
        """
        self.term.addSubProcessMessage('Calculation of z-means of submerged facets')
        z_means=[]
        for vertex in self.stl_model.submerged_facets:
            z_means.append(sum(vertex[:,2])/3)
        return np.array(z_means)

    def calc_submerged_facets_pressure_forces(self):
        """
        Calculer les forces de pression exercées sur chaque facette immergée
        :return: numpy array des forces de pression exercées sur chaque facette immergée
        """
        self.term.addSubProcessMessage('Calculation of the pressure forces exerted on the submerged facets')
        if self.stl_model.submerged_facets_number>0:
            z_means = self.calc_submerged_facets_z_means()
            submerged_facets_surfaces = self.calc_submerged_facets_surfaces()
            submerged_facets_pressure = []
            for i in range(self.stl_model.submerged_facets_number):
                submerged_facets_pressure.append(self.fluid_density*GRAVITY*z_means[i]*submerged_facets_surfaces[i])
            return submerged_facets_pressure
        return np.array([0,0,0])

    def calc_Archimedes_push(self):
        """
        Déterminer le vecteur poussée d'Archimède
        :return: numpy array de la poussée d'Archimède
        """
        self.term.addProcessMessage('Calculation of the Archimedes force')
        archimedes_push=sum(self.calc_submerged_facets_pressure_forces())
        self.term.addSuccessMessage('Calculation of the Archimedes force complete')
        return archimedes_push

    def dichotomy(self):
        """
        Réduire l'intervalle du tirant d'eau de moitié
        :return: la hauteur de la coque immergée
        """
        self.dichotomy_achieved+=1

        middle_range=sum(self.draught_range)/2
        delta = middle_range - self.stl_model.bottom_ref
        self.stl_model.translateZ(delta)
        if self.stl_model.weight>self.calc_Archimedes_push()[2]: # suffisant car P(z) décroissant si z décroit
            self.draught_range=[self.draught_range[0],middle_range]
        else:
            self.draught_range = [middle_range,self.draught_range[1]]
        return -self.stl_model.bottom_ref if self.stl_model.bottom_ref<0 else 0