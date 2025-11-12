import math
import random
from typing import List, Tuple

from constants import (
    CREATURE_RADIUS,
    FOOD_RADIUS,
    CREATURE_MAX_ENERGY,
    FOOD_ENERGY,
    GREEDY_CONSTANT,
    GREEDY_UNCERTAINTY,
    START_CREATURES,
)
from simulation import Simulation
from basic_simulation import (
    Creature,
    Food,
    point_on_random_edge,
    random_point_interior,
    distance,
    random_unit_vector,
)

class GreedySimulation(Simulation):
    # GreedySimulation.__init__(width, height)
    # 
    # @param width  the world width in pixels
    # @param height  the world height in pixels
    # @return None
    # 
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        # Start with creatures randomly along the edge
        num_creatures = START_CREATURES['greedy_simulation']
        for _ in range(num_creatures):
            start_pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
            self.creatures.append(Creature(position=start_pos, direction=random_unit_vector()))

    # Simulation.spawn_food_for_day(start_creature_count)
    # 
    # @param start_creature_count  number of creatures alive at day start
    # @return None
    # 
    def spawn_food_for_day(self, start_creature_count: int) -> None:
        # Check if the sim wants fixed food or scaling
        if getattr(self, 'food_scaling', True):
            base_count = math.ceil(GREEDY_CONSTANT * start_creature_count)
            # Add randomness using GREEDY_UNCERTAINTY: ±3 food items
            uncertainty_range = 3
            random_offset = random.randint(-uncertainty_range, uncertainty_range)
            # Apply uncertainty factor to the random offset
            adjusted_offset = int(random_offset * GREEDY_UNCERTAINTY)
            count = max(0, base_count + adjusted_offset)  # Ensure non-negative
        else:
            fixed = getattr(self, 'fixed_food_count', None)
            count = fixed if (isinstance(fixed, int) and fixed >= 0) else 0

        self.foods = []
        margin = max(FOOD_RADIUS + 2, CREATURE_RADIUS + 2)
        for _ in range(count):
            pos = random_point_interior(self.width, self.height, margin)
            self.foods.append(Food(position=pos))
        self.food_spawned = count

    # Simulation.reproduce_survivors()
    # 
    # @return None
    # 
    def reproduce_survivors(self) -> None:
        # In greedy simulation, all survivors carry over, but only those that ate 2+ food duplicate
        survivors = [c for c in self.creatures if c.is_survivor]
        new_creatures: List[Creature] = []
        
        for survivor in survivors:
            # Each survivor gets recreated on the edge for the next day
            pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
            new_creatures.append(Creature(position=pos, direction=random_unit_vector()))
            
            # If they ate 2+ foods, they also create a duplicate
            if survivor.has_eaten >= 2:
                pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
                new_creatures.append(Creature(position=pos, direction=random_unit_vector()))
        
        self.creatures = new_creatures

    # Simulation.handle_creature_collision(creature, food_index)
    # 
    # @param creature  the creature that collided
    # @param food_index  index of the food that was eaten
    # @return None
    # 
    def handle_creature_collision(self, creature, food_index: int) -> None:
        # Greedy simulation: track how many foods eaten using has_eaten counter
        creature.has_eaten += 1
        # Add food energy, clamped to max
        creature.energy = int(min(creature.energy + FOOD_ENERGY, CREATURE_MAX_ENERGY))

    def get_simulation_name(self) -> str:
        return "GreedySimulation"

    def get_creature_max_energy(self) -> int:
        return CREATURE_MAX_ENERGY

    def get_creature_radius(self) -> int:
        return CREATURE_RADIUS

    def get_food_radius(self) -> int:
        return FOOD_RADIUS

    def distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return distance(a, b)


