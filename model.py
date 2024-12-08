from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents import CivilianAgent, MilitaryAgent, TerroristAgent
from mesa.datacollection import DataCollector

class WarZoneModel(Model):
    """The main WarZoneMAS model."""
    def __init__(self, width, height, n_civilians, n_military, n_terrorists):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        self.high_value_areas = [(width // 2, height // 2)]  # Example high-value area

        # Add civilians
        for i in range(n_civilians):
            civilian = CivilianAgent(i,self)
            self.schedule.add(civilian)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(civilian, (x, y))

        # Add military agents
        for i in range(n_civilians, n_civilians + n_military):
            military = MilitaryAgent(i, self)
            self.schedule.add(military)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(military, (x, y))

        # Add terrorist agents
        for i in range(n_civilians + n_military, n_civilians + n_military + n_terrorists):
            terrorist = TerroristAgent(i, self)
            self.schedule.add(terrorist)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(terrorist, (x, y))

        # Add a DataCollector to track agent counts
        self.datacollector = DataCollector(
            {
                "Civilians": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, CivilianAgent)
                ),
                "Military": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, MilitaryAgent)
                ),
                "Terrorists": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, TerroristAgent)
                ),
            }
        )
        self.datacollector.collect(self)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
