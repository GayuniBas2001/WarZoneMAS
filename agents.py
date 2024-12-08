from mesa import Agent
import random

class CivilianAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.health_rate=random.randint(0, 10)

    def step(self):
        self.random_move()

    def random_move(self):
        # Get possible steps in Moore neighborhood
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        # Pick a random position to move to
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


class MilitaryAgent(Agent):
    """A military agent moving towards high-density civilian areas."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # Additional properties can be defined here if needed

    def step(self):
        target = self.find_high_density_area()
        if target:
            self.model.grid.move_agent(self, target)

    def find_high_density_area(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        max_density = 0
        target = None
        for cell in neighbors:
            agents = self.model.grid.get_cell_list_contents([cell])
            civilians = [agent for agent in agents if isinstance(agent, CivilianAgent)]
            if len(civilians) > max_density:
                max_density = len(civilians)
                target = cell
        return target


class TerroristAgent(Agent):
    """A terrorist agent aiming for high-value targets."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.target = None

    def step(self):
        self.update_target()
        if self.target:
            self.move_towards_target()

    def update_target(self):
        high_value_areas = self.model.high_value_areas
        military_positions = [
            agent.pos for agent in self.model.schedule.agents if isinstance(agent, MilitaryAgent)
        ]
        self.target = None
        min_distance = float("inf")
        for area in high_value_areas:
            distance = self.get_distance(self.pos, area)
            if area not in military_positions and distance < min_distance:
                self.target = area
                min_distance = distance

    def move_towards_target(self):
        if self.target:
            neighborhood = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            # Select the next step that minimizes the distance to the target
            next_step = min(neighborhood, key=lambda x: self.get_distance(x, self.target))
            self.model.grid.move_agent(self, next_step)

    @staticmethod
    def get_distance(pos1, pos2):
        """Calculate Manhattan distance between two points."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

