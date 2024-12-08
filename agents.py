from mesa import Agent
import random

class CivilianAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.morale_rate=100
        self.target_area = random.choice(self.model.crowded_areas)

    def step(self):
        if self.pos == self.target_area:
            self.target_area = self.get_new_target_area()
        self.move_towards(self.target_area)

    def get_new_target_area(self):
        # Choose a new random crowded area different from the current one
        new_target = random.choice(self.model.crowded_areas)
        while new_target == self.target_area:
            new_target = random.choice(self.model.crowded_areas)
        return new_target

    def move_towards(self, target):
        # Calculate the next step towards the target
        next_step = self.get_next_step_towards(target)
        # Move to the next step
        self.model.grid.move_agent(self, next_step)

    def get_next_step_towards(self, target):
        # Get the current position
        current_pos = self.pos
        # Calculate the direction to move in
        direction = (target[0] - current_pos[0], target[1] - current_pos[1])
        # Normalize the direction to get a step
        step = (current_pos[0] + (1 if direction[0] > 0 else -1 if direction[0] < 0 else 0),
                current_pos[1] + (1 if direction[1] > 0 else -1 if direction[1] < 0 else 0))
        return step

    @staticmethod
    def get_distance(pos1, pos2):
        # Calculate the Manhattan distance between two points
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


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
            self.move_towards(target)

    def find_high_density_area(self):
        # Create a dictionary to count civilians in each cell
        civilian_counts = {}
        for agent in self.model.schedule.agents:
            if isinstance(agent, CivilianAgent):
                pos = agent.pos
                if pos in civilian_counts:
                    civilian_counts[pos] += 1
                else:
                    civilian_counts[pos] = 1

        # Find the position with the highest number of civilians
        if civilian_counts:
            max_civilians = max(civilian_counts.values())
            high_density_areas = [pos for pos, count in civilian_counts.items() if count == max_civilians]
            # Find the closest high-density area
            closest_area = min(high_density_areas, key=lambda pos: self.get_distance(self.pos, pos))
            return closest_area
        return None

    def move_towards(self, target):
        # Calculate the next step towards the target
        next_step = self.get_next_step_towards(target)
        # Move to the next step
        self.model.grid.move_agent(self, next_step)

    def get_next_step_towards(self, target):
        # Get the current position
        current_pos = self.pos
        # Calculate the direction to move in
        direction = (target[0] - current_pos[0], target[1] - current_pos[1])
        # Normalize the direction to get a step
        step = (current_pos[0] + (1 if direction[0] > 0 else -1 if direction[0] < 0 else 0),
                current_pos[1] + (1 if direction[1] > 0 else -1 if direction[1] < 0 else 0))
        return step

    @staticmethod
    def get_distance(pos1, pos2):
        # Calculate the Manhattan distance between two points
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class TerroristAgent(Agent):
    """A t agent aiming for high-value targets."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.target = None

    def step(self):
        self.update_target()
        if self.target:
            self.move_towards_target()
        self.check_and_remove_agents()

    def update_target(self):
        # Create dictionaries to count civilians and military agents in each cell
        civilian_counts = {}
        military_counts = {}
        for agent in self.model.schedule.agents:
            if isinstance(agent, CivilianAgent):
                pos = agent.pos
                if pos in civilian_counts:
                    civilian_counts[pos] += 1
                else:
                    civilian_counts[pos] = 1
            elif isinstance(agent, MilitaryAgent):
                pos = agent.pos
                if pos in military_counts:
                    military_counts[pos] += 1
                else:
                    military_counts[pos] = 1
            # Find positions with more civilians and less than 4 military agents
        potential_targets = [pos for pos, count in civilian_counts.items() if count > 0 and military_counts.get(pos, 0) < 4]

        # Communicate with other TAgents to distribute themselves
        occupied_positions = [agent.target for agent in self.model.schedule.agents if isinstance(agent, TerroristAgent) and agent.target]
        potential_targets = [pos for pos in potential_targets if pos not in occupied_positions]

        if potential_targets:
            # Find the closest potential target
            self.target = min(potential_targets, key=lambda pos: self.get_distance(self.pos, pos))
        else:
            self.target = None

    def move_towards_target(self):
        # Calculate the next step towards the target
        next_step = self.get_next_step_towards(self.target)
        # Move to the next step
        self.model.grid.move_agent(self, next_step)

    def get_next_step_towards(self, target):
        # Get the current position
        current_pos = self.pos
        # Calculate the direction to move in
        direction = (target[0] - current_pos[0], target[1] - current_pos[1])
        # Normalize the direction to get a step
        step = (current_pos[0] + (1 if direction[0] > 0 else -1 if direction[0] < 0 else 0),
                current_pos[1] + (1 if direction[1] > 0 else -1 if direction[1] < 0 else 0))
        return step

    def check_and_remove_agents(self):
        # Get the 24 closest cells around the agent
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=2)
        close_neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=True, radius=1)

        # Count the number of first and second type agents in the 24 closest cells
        count = 0
        for neighbor in neighbors:
            cell_agents = self.model.grid.get_cell_list_contents([neighbor])
            for agent in cell_agents:
                if isinstance(agent, (CivilianAgent, MilitaryAgent)):
                    count += 1

        # If more than 14 out of 24 cells are occupied by first or second type agents
        if count > 14:
            # Remove agents in the closest 8 cells
            for neighbor in close_neighbors:
                cell_agents = self.model.grid.get_cell_list_contents([neighbor])
                for agent in cell_agents:
                    if isinstance(agent, (CivilianAgent, MilitaryAgent)):
                        self.model.grid.remove_agent(agent)
                        self.model.schedule.remove(agent)
                # Color the cell orange
                self.model.grid.place_agent(OrangeCell(neighbor), neighbor)

    @staticmethod
    def get_distance(pos1, pos2):
        # Calculate the Manhattan distance between two points
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class OrangeCell(Agent):
    """An agent representing an orange-colored cell."""
    def __init__(self, pos):
        self.pos = pos
