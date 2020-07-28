import numpy as np
from configurations import *

class STLModel:
    def __init__(self,filepath,term):
        self.term=term
        self.term.addProcessMessage('STL file recovery')
        self.term.addSubProcessMessage('STL file opening')
        file=open(filepath)
        self.term.addSubProcessMessage('STL file reading')
        self.file_content=file.read().split('\n')
        file.close()

        self.vertex,self.facet_normal=self.extract_facets_data()
        self.facets_number=len(self.vertex)

        if self.facets_number==0:
            self.term.addErrorMessage('Invalid STL : the STL file must be in ascii format')
        else:
            self.vertex_flatten=self.vertex.reshape(3*self.facets_number,3)
            X,Y,Z=self.vertex_flatten[:,0],self.vertex_flatten[:,1],self.vertex_flatten[:,2]
            self.x_range=[min(X),max(X)]
            self.y_range=[min(Y),max(Y)]
            self.bottom_ref=min(Z)
            self.height=max(Z)-self.bottom_ref

            self.weight=DEFAULT_OBJECT_MASS*GRAVITY

            self.sort_facets()

    def setMass(self,mass):
        """
        Définir la masse de l'objet puis calculer son poids
        :param mass : masse de l'objet
        """
        self.term.addInformativeMessage('Mass set to '+str(mass)+' kg')
        self.weight=mass*GRAVITY

    def extract_facets_data(self):
        """
        Extraire les informations essentielles du fichier STL
        :return: numpy array des coordonnées des sommets de triangle, numpy array des vecteurs normaux
        """
        self.term.addProcessMessage('Extraction of the different facets data')
        self.term.addSubProcessMessage('Extraction of vertex coordinates')
        self.term.addSubProcessMessage('Extraction of normal vectors')
        data_types=['facet normal','vertex']

        vertex=[]
        facet_normal=[]
        for line in self.file_content:
            if data_types[0] in line:
                facet_normal.append([float(i) for i in line.split(' ')[-3:]])
                vertex.append([])
            elif data_types[1] in line:
                vertex[-1].append([float(i) for i in line.split(' ')[-3:]])
        self.term.addSuccessMessage('Extraction of the different facets data complete')
        return np.array(vertex),np.array(facet_normal)
    
    def translateZ(self,delta):
        """
        Translater verticalement toutes les facettes du modele 3d
        :param delta: valeur de la translation (>0 vers le haut, <0 vers le bas)
        """
        for vertex in self.vertex:
            vertex[:,2]+=delta
        self.bottom_ref+=delta
        self.term.addInformativeMessage('3d model vertically translated by '+str(delta)+' m')
        self.sort_facets()

    def get_coordinates_intersection_point_fluid_leved_facet_side(self,A,B):
        """
        A et B deux points de part et d'autre du niveau d'eau
        Calculer les coordonnées du point I, point d'intersection entre le segment AB et le plan z=0
        :param A: coordonnées du point A
        :param B: coordonnées du point B
        :return: coordonnées du point I
        """
        Ax,Ay,Az=A
        Bx,By,Bz=B
        k=-Az/(Bz-Az)
        return np.array([k*(Bx-Ax)+Ax,k*(By-Ay)+Ay,0])

    def sort_facets(self):
        """
        Trier les facettes en 2 groupes : emergées et immergées en fonction de la position de leurs sommets
        :return: numpay array des facettes emergées, immergées, leurs normales et leur nombre
        """
        self.term.addProcessMessage('Separation of emerged and submerged facets')
        emerged_facets=[]

        submerged_facets=[]
        submerged_facet_normal=[]

        for i in range(self.facets_number):
            facet=self.vertex[i]
            z=facet[:,2]
            true_values=np.count_nonzero(z>=0)
            false_values=np.count_nonzero(z<=0)
            if true_values==3:
                emerged_facets.append(facet)
            elif false_values==3:
                submerged_facets.append(facet)
                submerged_facet_normal.append(self.facet_normal[i])
            else:
                sup=np.array([v for v in facet if v[2]>0])
                inf=np.array([v for v in facet if v[2]<0])

                sup_number=len(sup)
                inf_number=len(inf)

                if sup_number==1 and inf_number==1: # plan z=0 passe par le sommet d'une facette donc 1 seule intersection avec un côté
                    A,B=sup[0],inf[0]
                    C=np.array([v for v in facet if v[2]==0])[0]
                    I=self.get_coordinates_intersection_point_fluid_leved_facet_side(A,B)
                    emerged_facets.append(np.array([I,C,A]))
                    submerged_facets.append(np.array([I,C,B]))
                    submerged_facet_normal.append(self.facet_normal[i])
                elif sup_number==2 and inf_number==1: # triangle avec 2 sommets au dessus du plan z=0 et 1 en dessous
                    A,B=sup
                    C=inf[0]
                    I=self.get_coordinates_intersection_point_fluid_leved_facet_side(A,C)
                    J=self.get_coordinates_intersection_point_fluid_leved_facet_side(B,C)
                    emerged_facets.append(np.array([I,J,A]))
                    emerged_facets.append(np.array([A,B,J]))
                    submerged_facets.append(np.array([I,J,C]))
                    submerged_facet_normal.append(self.facet_normal[i])
                else: # facette avec 2 sommet au dessous de z=0 et 1 au dessus
                    A, B = inf
                    C = sup[0]
                    I = self.get_coordinates_intersection_point_fluid_leved_facet_side(A,C)
                    J = self.get_coordinates_intersection_point_fluid_leved_facet_side(B,C)
                    emerged_facets.append(np.array([I,J,C]))
                    submerged_facets.append(np.array([I,J,A]))
                    submerged_facet_normal.append(self.facet_normal[i])
                    submerged_facets.append(np.array([A, B, J]))
                    submerged_facet_normal.append(self.facet_normal[i])
        self.emerged_facets,self.submerged_facets,self.submerged_facet_normal=np.array(emerged_facets),np.array(submerged_facets),np.array(submerged_facet_normal)
        self.submerged_facets_number=len(submerged_facets)
        self.term.addSuccessMessage('Separation of emerged and submerged facets complete')