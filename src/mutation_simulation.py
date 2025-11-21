import random
from typing import List, Tuple

import pygame

from constants import (
    CREATURE_RADIUS,
    FOOD_RADIUS,
    CREATURE_MAX_ENERGY,
    FOOD_ENERGY,
    CREATURE_STEP_SIZE,
    START_CREATURES,
)
from constants import MUTATION_SPEED_DELTA
from simulation import Simulation
from basic_simulation import (
    Food,
    point_on_random_edge,
    random_point_interior,
    distance,
    random_unit_vector,
)


class Creature:
    """Creature for mutation simulation. Has a traits dict (currently only 'speed' multiplier).

    energy is a float so we can model fractional energy drain for speed multipliers.
    """

    def __init__(self, position: Tuple[float, float], direction: Tuple[float, float], speed_mult: float = 1.0):
        self.position = position
        self.direction = direction
        self.traits = {'speed': float(speed_mult)}
        self.energy = float(CREATURE_MAX_ENERGY)
        self.has_eaten = 0
        self.is_survivor = False

    def move(self) -> None:
        speed = self.traits.get('speed', 1.0)
        dx = self.direction[0] * CREATURE_STEP_SIZE * speed
        dy = self.direction[1] * CREATURE_STEP_SIZE * speed
        self.position = (self.position[0] + dx, self.position[1] + dy)
        # energy drained per move scales with speed (linear)
        self.energy -= (1.0 * speed)

    def handle_edges(self, width: int, height: int) -> None:
        x, y = self.position
        touched_edge = (
            x <= CREATURE_RADIUS or x >= width - CREATURE_RADIUS or
            y <= CREATURE_RADIUS or y >= height - CREATURE_RADIUS
        )

        if self.has_eaten > 0 and touched_edge:
            self.is_survivor = True
            # clamp into bounds
            x = max(CREATURE_RADIUS, min(x, width - CREATURE_RADIUS))
            y = max(CREATURE_RADIUS, min(y, height - CREATURE_RADIUS))
            self.position = (x, y)
            return

        if self.has_eaten == 0:
            bounced = False
            if x < CREATURE_RADIUS:
                x = CREATURE_RADIUS
                self.direction = (-self.direction[0], self.direction[1])
                bounced = True
            elif x > width - CREATURE_RADIUS:
                x = width - CREATURE_RADIUS
                self.direction = (-self.direction[0], self.direction[1])
                bounced = True
            if y < CREATURE_RADIUS:
                y = CREATURE_RADIUS
                self.direction = (self.direction[0], -self.direction[1])
                bounced = True
            elif y > height - CREATURE_RADIUS:
                y = height - CREATURE_RADIUS
                self.direction = (self.direction[0], -self.direction[1])
                bounced = True
            if bounced:
                if random.random() < 0.5:
                    self.direction = random_unit_vector()
            self.position = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        color = (220, 60, 60) if (not self.is_survivor and self.energy <= 0) else (61, 178, 255)
        pygame.draw.circle(surface, color, (int(self.position[0]), int(self.position[1])), CREATURE_RADIUS)


class MutationSimulation(Simulation):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        num_creatures = START_CREATURES.get('mutation_simulation', START_CREATURES.get('basic_simulation', 5))
        for _ in range(num_creatures):
            start_pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
            self.creatures.append(Creature(position=start_pos, direction=random_unit_vector()))

    def spawn_food_for_day(self, start_creature_count: int) -> None:
        if getattr(self, 'food_scaling', True):
            count = start_creature_count
        else:
            fixed = getattr(self, 'fixed_food_count', None)
            count = fixed if (isinstance(fixed, int) and fixed >= 0) else start_creature_count
        self.foods = []
        margin = max(FOOD_RADIUS + 2, CREATURE_RADIUS + 2)
        for _ in range(count):
            pos = random_point_interior(self.width, self.height, margin)
            self.foods.append(Food(position=pos))
        self.food_spawned = count

    def reproduce_survivors(self) -> None:
        survivors = [c for c in self.creatures if c.is_survivor]
        new_creatures: List[Creature] = []
        for survivor in survivors:
            # recreate the survivor on the edge
            pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
            new_creatures.append(Creature(position=pos, direction=random_unit_vector(), speed_mult=survivor.traits.get('speed', 1.0)))
            # if they ate 2 or more foods, they replicate once with possible mutation
            if survivor.has_eaten >= 2:
                # child inherits speed with a percent change in [-MUTATION_SPEED_DELTA, +MUTATION_SPEED_DELTA]
                parent_speed = survivor.traits.get('speed', 1.0)
                change = random.uniform(-MUTATION_SPEED_DELTA, MUTATION_SPEED_DELTA)
                mutated = parent_speed * (1.0 + change)
                pos2 = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
                new_creatures.append(Creature(position=pos2, direction=random_unit_vector(), speed_mult=mutated))
        self.creatures = new_creatures

    def handle_creature_collision(self, creature, food_index: int) -> None:
        creature.has_eaten += 1
        # add energy from food, clamped
        creature.energy = min(creature.energy + FOOD_ENERGY, float(self.get_creature_max_energy()))

    def get_simulation_name(self) -> str:
        return 'MutationSimulation'

    def get_creature_max_energy(self) -> int:
        return CREATURE_MAX_ENERGY

    def get_creature_radius(self) -> int:
        return CREATURE_RADIUS

    def get_food_radius(self) -> int:
        return FOOD_RADIUS

    def distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return distance(a, b)
