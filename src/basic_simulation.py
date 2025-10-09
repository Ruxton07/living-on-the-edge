import math
import os
import random
import csv
from dataclasses import dataclass
from typing import List, Tuple, Optional

import pygame

from constants import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    BACKGROUND_COLOR,
    EDGE_COLOR,
    CREATURE_COLOR,
    FOOD_COLOR,
    DEAD_COLOR,
    CREATURE_RADIUS,
    FOOD_RADIUS,
    TICKS_PER_SECOND,
    CREATURE_MAX_ENERGY,
    CREATURE_STEP_SIZE,
    START_CREATURES,
)
from simulation import Simulation


# clamp(value, min_value, max_value)
# 
# @param value  the numeric value to clamp
# @param min_value  the inclusive minimum
# @param max_value  the inclusive maximum
# @return the value clamped into [min_value, max_value]
# 
def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


# random_unit_vector()
# 
# @return a random 2D unit vector as (x, y)
# 
def random_unit_vector() -> Tuple[float, float]:
    angle = random.uniform(0, 2 * math.pi)
    return math.cos(angle), math.sin(angle)


# distance(a, b)
# 
# @param a  point (x, y)
# @param b  point (x, y)
# @return Euclidean distance between a and b
# 
def distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


# point_on_random_edge(width, height, margin)
# 
# @param width  the world width in pixels
# @param height  the world height in pixels
# @param margin  inset to keep circles visible fully on-screen
# @return a random point on one of the four borders
# 
def point_on_random_edge(width: int, height: int, margin: int = 0) -> Tuple[float, float]:
    edge = random.choice(['top', 'bottom', 'left', 'right'])
    if edge == 'top':
        return random.uniform(margin, width - margin), margin
    if edge == 'bottom':
        return random.uniform(margin, width - margin), height - margin
    if edge == 'left':
        return margin, random.uniform(margin, height - margin)
    return width - margin, random.uniform(margin, height - margin)


# random_point_interior(width, height, margin)
# 
# @param width  the world width in pixels
# @param height  the world height in pixels
# @param margin  inset to keep inside the border by at least this many pixels
# @return a random point strictly inside the rectangle
# 
def random_point_interior(width: int, height: int, margin: int) -> Tuple[float, float]:
    return (
        random.uniform(margin, width - margin),
        random.uniform(margin, height - margin),
    )


# Food
# 
# Represents a single food item placed in the world, drawn as a green circle.
@dataclass
class Food:
    position: Tuple[float, float]

    # Food.draw(surface)
    # 
    # @param surface  the pygame surface to draw to
    # @return None
    # 
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, FOOD_COLOR, (int(self.position[0]), int(self.position[1])), FOOD_RADIUS)


# Creature
# 
# A moving agent with limited energy that must eat and then return to the edge.
@dataclass
class Creature:
    position: Tuple[float, float]
    direction: Tuple[float, float]
    energy: int = CREATURE_MAX_ENERGY
    has_eaten: int = 0  # Number of foods eaten (changed from bool to int)
    is_survivor: bool = False

    def __str__(self) -> str:
        status = "alive" if self.energy > 0 else "dead"
        return f"Creature({status}, eaten {self.has_eaten}, energy: {self.energy})"

    # Creature.move()
    # 
    # @return None
    # 
    def move(self) -> None:
        if random.random() < 0.05:
            self.direction = random_unit_vector()
        dx = self.direction[0] * CREATURE_STEP_SIZE
        dy = self.direction[1] * CREATURE_STEP_SIZE
        self.position = (self.position[0] + dx, self.position[1] + dy)
        self.energy -= 1

    # Creature.handle_edges(width, height)
    # 
    # @param width  the world width in pixels
    # @param height  the world height in pixels
    # @return None
    # 
    def handle_edges(self, width: int, height: int) -> None:
        x, y = self.position
        touched_edge = (
            x <= CREATURE_RADIUS or x >= width - CREATURE_RADIUS or
            y <= CREATURE_RADIUS or y >= height - CREATURE_RADIUS
        )

        if self.has_eaten > 0 and touched_edge:
            self.is_survivor = True
            x = clamp(x, CREATURE_RADIUS, width - CREATURE_RADIUS)
            y = clamp(y, CREATURE_RADIUS, height - CREATURE_RADIUS)
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

    # Creature.draw(surface)
    # 
    # @param surface  the pygame surface to draw to
    # @return None
    # 
    def draw(self, surface: pygame.Surface) -> None:
        color = DEAD_COLOR if (not self.is_survivor and self.energy <= 0) else CREATURE_COLOR
        pygame.draw.circle(surface, color, (int(self.position[0]), int(self.position[1])), CREATURE_RADIUS)


class BasicSimulation(Simulation):
    # BasicSimulation.__init__(width, height)
    # 
    # @param width  the world width in pixels
    # @param height  the world height in pixels
    # @return None
    # 
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        # Start with creatures randomly along the edge
        num_creatures = START_CREATURES['basic_simulation']
        for _ in range(num_creatures):
            start_pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
            self.creatures.append(Creature(position=start_pos, direction=random_unit_vector()))

    # Simulation.spawn_food_for_day(start_creature_count)
    # 
    # @param start_creature_count  number of creatures alive at day start
    # @return None
    # 
    def spawn_food_for_day(self, start_creature_count: int) -> None:
        # Determine food count based on sim settings
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

    # Simulation.reproduce_survivors()
    # 
    # @return None
    # 
    def reproduce_survivors(self) -> None:
        survivors = [c for c in self.creatures if c.is_survivor]
        new_creatures: List[Creature] = []
        for _ in survivors:
            for _child in range(2):
                pos = point_on_random_edge(self.width, self.height, margin=CREATURE_RADIUS)
                new_creatures.append(Creature(position=pos, direction=random_unit_vector()))
        self.creatures = new_creatures

    def handle_creature_collision(self, creature, food_index: int) -> None:
        # Basic simulation: eating one food resets energy and increments eaten count
        creature.has_eaten += 1
        creature.energy = CREATURE_MAX_ENERGY

    def get_simulation_name(self) -> str:
        return "BasicSimulation"

    def get_creature_max_energy(self) -> int:
        return CREATURE_MAX_ENERGY

    def get_creature_radius(self) -> int:
        return CREATURE_RADIUS

    def get_food_radius(self) -> int:
        return FOOD_RADIUS

    def distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return distance(a, b)


