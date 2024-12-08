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
        # Check if the next step is within the grid boundaries
        if self.model.grid.out_of_bounds(next_step):
            return
        # Check if the cell contains any agents
        cell_contents = self.model.grid.get_cell_list_contents([next_step])
        if not cell_contents or not isinstance(cell_contents[0], OrangeCell):
            self.model.grid.move_agent(self, next_step)

        else:
            # Find an alternative step
            self.find_alternative_step(target)

    def find_alternative_step(self, target):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        for step in possible_steps:
            if not self.model.grid.out_of_bounds(step):
                cell_contents = self.model.grid.get_cell_list_contents([step])
                if not cell_contents or not isinstance(cell_contents[0], OrangeCell):
                    self.model.grid.move_agent(self, step)
                    return

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
    """A military agent forming groups to surround and remove TAgents."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.group = []

    def step(self):
        self.form_group()
        target = self.find_terrorist_agent()
        if target:
            self.move_towards(target)
            self.check_and_remove_terrorist_agent(target)

    def form_group(self):
        # Communicate with other MilitaryAgents to form groups of 4
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=2)
        self.group = [agent for agent in neighbors if isinstance(agent, MilitaryAgent)]
        if len(self.group) < 4:
            self.group.append(self)
    def find_terrorist_agent(self):
        # Find the closest TAgent
        terrorist_agents = [agent for agent in self.model.schedule.agents if isinstance(agent, TerroristAgent)]
        if terrorist_agents:
            closest_terrorist_agent = min(terrorist_agents, key=lambda agent: self.get_distance(self.pos, agent.pos))
            return closest_terrorist_agent.pos
        return None

    def move_towards(self, target):
        # Calculate the next step towards the target
        next_step = self.get_next_step_towards(target)
        # Check if the next step is within the grid boundaries
        if self.model.grid.out_of_bounds(next_step):
            return
        # Check if the cell contains any agents
        cell_contents = self.model.grid.get_cell_list_contents([next_step])
        if not cell_contents or not isinstance(cell_contents[0], OrangeCell):
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

    def check_and_remove_terrorist_agent(self, target):
        # Check if the TAgent is surrounded by 4 MilitaryAgents
        neighbors = self.model.grid.get_neighbors(target, moore=True, include_center=False, radius=1)
        military_agents = [agent for agent in neighbors if isinstance(agent, MilitaryAgent)]
        if len(military_agents) >= 4:
            # Remove the TAgent
            terrorist_agent = [agent for agent in self.model.grid.get_cell_list_contents([target]) if isinstance(agent, TerroristAgent)]
            if terrorist_agent:
                self.model.grid.remove_agent(terrorist_agent[0])
                self.model.schedule.remove(terrorist_agent[0])

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
