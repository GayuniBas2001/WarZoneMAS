from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents import CivilianAgent, MilitaryAgent, TerroristAgent, OrangeCell
from mesa.datacollection import DataCollector
from report_element import display_report
import tkinter as tk
from tkinter import messagebox

class WarZoneModel(Model):
    """The main WarZoneMAS model."""
    def __init__(self, num_civilians, num_military, num_terrorists):
        self.num_civilians = num_civilians
        self.num_military = num_military
        self.num_terrorists = num_terrorists
        self.grid = MultiGrid(30, 30, True)
        self.schedule = RandomActivation(self)
        self.running = True

        self.crowded_areas = [(2,2), (7, 15), (15, 7), (10, 15), (10, 29), (27, 25), (28,3), (2,28)]
        self.high_value_areas = [(30 // 2, 30 // 2)]  # Example high-value area

        # Track initial populations
        self.initial_civilians = num_civilians
        self.initial_military = num_military
        self.initial_terrorists = num_terrorists

        # Track casualties
        self.civilian_casualties = 0
        self.military_casualties = 0
        self.terrorist_casualties = 0
        self.danger_zones_created = 0

        # Add civilians
        for i in range(num_civilians):
            civilian = CivilianAgent(i,self)
            self.schedule.add(civilian)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(civilian, (x, y))

        # Add military agents
        for i in range(num_civilians, num_civilians + num_military):
            military = MilitaryAgent(i, self)
            self.schedule.add(military)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(military, (x, y))

        # Add terrorist agents
        for i in range(num_civilians + num_military, num_civilians + num_military + num_terrorists):
            terrorist = TerroristAgent(i, self)
            self.schedule.add(terrorist)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(terrorist, (x, y))

                # Add data collector
        self.datacollector = DataCollector(
            {
                "Civilians": lambda m: self.count_type(m, CivilianAgent),
                "Military": lambda m: self.count_type(m, MilitaryAgent),
                "Terrorists": lambda m: self.count_type(m, TerroristAgent),
            }
        )

        # Initialize report attribute
        self.report = None

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.check_for_report()

    def check_for_report(self):
        civilian_count = self.count_type(self, CivilianAgent)
        military_count = self.count_type(self, MilitaryAgent)
        terrorist_count = self.count_type(self, TerroristAgent)

        if civilian_count == 0 or military_count == 0 or terrorist_count == 0:
            self.generate_report()

    def generate_report(self):
        final_civilians = self.count_type(self, CivilianAgent)
        final_military = self.count_type(self, MilitaryAgent)
        final_terrorists = self.count_type(self, TerroristAgent)

        self.civilian_casualties = self.initial_civilians-final_civilians
        self.military_casualties = self.initial_military-final_military
        self.terrorist_casualties = self.initial_terrorists-final_terrorists
        self.danger_zones_created = self.count_type(self, OrangeCell)

        self.report = {
            "Initial vs. Final Population": {
                "Civilians": f"{self.initial_civilians} -> {final_civilians}",
                "Military": f"{self.initial_military} -> {final_military}",
                "Terrorists": f"{self.initial_terrorists} -> {final_terrorists}",
            },
            "Casualty Distribution": { #Number of civilians, military personnel, and terrorists removed over time
                "Civilians": f"{self.civilian_casualties}",
                "Military": f"{self.military_casualties}",
                "Terrorists": f"{self.terrorist_casualties}",
            },
            "Rate of Attrition": { #The pace at which each type of agent was removed
                "Civilians": self.civilian_casualties / self.schedule.steps,
                "Military": self.military_casualties / self.schedule.steps,
                "Terrorists": self.terrorist_casualties / self.schedule.steps,
            },
            "Military Effectiveness": {
                "Terrorists Neutralized": self.terrorist_casualties,
                "Military Losses": self.military_casualties,
            },
            "Terrorist Impact": {
                "Civilian Casualties": self.civilian_casualties,
                "Danger Zones Created": self.danger_zones_created,
            },
            "Effective Ratio": {
                "Civilians to Military": final_civilians / final_military if final_military > 0 else "N/A",
                "Civilians to Terrorists": final_civilians / final_terrorists if final_terrorists > 0 else "N/A",
                "Military to Terrorists": final_military / final_terrorists if final_terrorists > 0 else "N/A",
            }
        }
        print("Simulation Report:")
        for key, value in self.report.items():
            print(f"{key}: {value}")
        print("All Done!")

        root = tk.Tk()
        # root.withdraw()  # Hide the root window
        report_text = ""
        for key, value in self.report.items():
            report_text += f"{key}:\n"
            for sub_key, sub_value in value.items():
                report_text += f"  {sub_key}: {sub_value}\n"
            report_text += "\n"
        messagebox.showinfo("Simulation Report", report_text)
        root.destroy()
        self.running = False

    @staticmethod
    def count_type(model, agent_type):
        count = 0
        for agent in model.schedule.agents:
            if isinstance(agent, agent_type):
                count += 1
        return count

    def remove_agent(self, agent):
        if isinstance(agent, CivilianAgent):
            self.civilian_casualties += 1
        elif isinstance(agent, MilitaryAgent):
            self.military_casualties += 1
        elif isinstance(agent, TerroristAgent):
            self.terrorist_casualties += 1
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def create_danger_zone(self, pos):
        self.danger_zones_created += 1
        self.grid.place_agent(OrangeCell(pos), pos)