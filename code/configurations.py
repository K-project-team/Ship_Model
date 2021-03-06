"""
DISPLAY PARAMETERS
"""
### GRAPH SETTINGS ###
X_MARGIN=1
Y_MARGIN=1
# /!\ si X_MARGIN!=Y_MARGIN appararition de déformations
DEPTH_COEFFICIENT=1
VIEW_ELEV=15
VIEW_AZIM=-40

### COLORS SETTINGS ###
EMERGED_PART_COLOR='#f1c40f'
EMERGED_PART_BORDER_COLOR='#d35400'
DRAUGHT_LINE_COLOR='#d35400'

SUBMERGED_PART_COLOR='#3498db'
SUBMERGED_PART_BORDER_COLOR='#2c3e50'

TERMINAL_BACKGROUND_COLOR='#2c3e50'
TERMINAL_ERROR_MESSAGE_COLOR='#d35400'
TERMINAL_SUCCESS_MESSAGE_COLOR='#2ecc71'
TERMINAL_PROCESS_MESSAGE_COLOR='#fff'
TERMINAL_INFORMATIVE_MESSAGE_COLOR='#3498db'

"""
FILE PARAMETERS
"""
ICONS_FOLDER='ressources/icons/'

LEGEND_FOLDER='ressources/legend/'

DEFAULT_STL_MODEL_GRAPH_FOLDER='ressources/graphs/default_graphs/default_STL_model_graph.png'
DEFAULT_DRAUGHT_GRAPH_FOLDER='ressources/graphs/default_graphs/default_draught_graph.png'

STL_MODEL_GRAPHS_FOLDER='ressources/graphs/STL_model_graphs/'
DRAUGHT_GRAPHS_FOLDER='ressources/graphs/draught_graphs/'

STL_MODEL_LOADED_VIEW_FOLDER='ressources/graphs/STL_model_loaded_view/'

FRAMES_BASENAME='frame_'

ANIMATIONS_FOLDER='animations/'
ANIMATION_FOLDER_BASENAME='animation_'

"""
ANIMATION PARAMETERS
"""
GIF_DELAY_BETWEEN_TWO_FRAMES=10 # ms

"""
CONSTANTS
"""
GRAVITY=9.81
FRESHWATER_DENSITY=1000
SALTWATER_DENSITY=1025

"""
DEFAULT CALCULOUS PARAMETERS
"""
DEFAULT_OBJECT_MASS=1000.0
DEFAULT_DICHOTOMY_PRECISION=1e-3
DEFAULT_FLUID_DENSITY=FRESHWATER_DENSITY

"""
DEFAULT DISPLAY PARAMETERS
"""
DEFAULT_SHOW_DRAUGHT=False