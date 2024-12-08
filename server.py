from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from model import WarZoneModel
from agents import CivilianAgent, MilitaryAgent, TerroristAgent

def agent_portrayal(agent):
    """
    Define how each type of agent will be represented on the grid.
    """
    if isinstance(agent, CivilianAgent):
        portrayal = {"Shape": "circle", "Color": "blue", "Filled": True, "r": 0.5, "Layer": 1}
    elif isinstance(agent, MilitaryAgent):
        portrayal = {"Shape": "circle", "Color": "green", "Filled": True, "r": 0.7, "Layer": 2}
    elif isinstance(agent, TerroristAgent):
        portrayal = {"Shape": "circle", "Color": "red", "Filled": True, "r": 0.7, "Layer": 3}
    return portrayal


# Define grid size
grid_width = 20
grid_height = 20

# Create a CanvasGrid for visualization
grid = CanvasGrid(agent_portrayal, grid_width, grid_height, 500, 500)

# Add a chart to track data (optional)
chart = ChartModule(
    [{"Label": "Civilians", "Color": "blue"},
     {"Label": "Military", "Color": "green"},
     {"Label": "Terrorists", "Color": "red"}]
)

# Create a server to run the model with visualization
server = ModularServer(
    WarZoneModel,
    [grid, chart],
    "WarZoneMAS",
    {"width": grid_width, "height": grid_height, "n_civilians": 50, "n_military": 10, "n_terrorists": 5}
)

if __name__ == "__main__":
    server.port = 8521  # Default port
    server.launch()
