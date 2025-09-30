import math
import random
from typing import List, Tuple

from constants import (
    CREATURE_RADIUS,
    FOOD_RADIUS,
    CREATURE_MAX_ENERGY,
    GREEDY_CONSTANT,
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
        # Start with one creature randomly along the edge
        start_pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
        self.creatures.append(Creature(position=start_pos, direction=random_unit_vector()))

    # Simulation.spawn_food_for_day(start_creature_count)
    # 
    # @param start_creature_count  number of creatures alive at day start
    # @return None
    # 
    def spawn_food_for_day(self, start_creature_count: int) -> None:
        count = min(2, math.floor(GREEDY_CONSTANT * start_creature_count))
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
        # In greedy simulation, only creatures that ate 2+ food reproduce
        reproducers = [c for c in self.creatures if c.is_survivor and getattr(c, 'foods_eaten', 0) >= 2]
        new_creatures: List[Creature] = []
        for _ in reproducers:
            # Split into two creatures on the edge at the start of next day
            for _child in range(2):
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
        # Greedy simulation: track how many foods eaten
        if not hasattr(creature, 'foods_eaten'):
            creature.foods_eaten = 0
        creature.foods_eaten += 1
        
        # Reset energy on any food consumption
        creature.energy = CREATURE_MAX_ENERGY
        
        # Mark as eaten if they've had at least 1 food (survival requirement)
        if creature.foods_eaten >= 1:
            creature.has_eaten = True

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


