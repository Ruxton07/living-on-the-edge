import math
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
    INTELLIGENCE_BASE_RANGE,
    INTELLIGENCE_BASE_ERROR_DEGREES,
    INTELLIGENCE_TURN_RATE,
    INTELLIGENCE_ENERGY_COST,
)
from constants import MUTATION_SPEED_DELTA, MUTATION_SIZE_DELTA, MUTATION_INTELLIGENCE_DELTA
from simulation import Simulation
from basic_simulation import (
    Food,
    point_on_random_edge,
    random_point_interior,
    distance,
    random_unit_vector,
)


class Creature:
    """Creature for mutation simulation.

    Traits:
    - speed: multiplier on base step size (affects movement and energy drain)
    - size: area multiplier (radius scales with sqrt(size); energy drain scales linearly with size)
    - intelligence: improves food tracking through longer range and less steering error

    energy is a float so we can model fractional energy drain for speed/size multipliers.
    """

    def __init__(
        self,
        position: Tuple[float, float],
        direction: Tuple[float, float],
        speed_mult: float = 1.0,
        size_mult: float = 1.0,
        intelligence_mult: float = 1.0,
        base_radius: int = CREATURE_RADIUS,
    ):
        self.position = position
        self.direction = direction
        self.traits = {
            'speed': float(speed_mult),
            'size': float(size_mult),
            'intelligence': float(intelligence_mult),
        }
        self.base_radius = base_radius
        self.energy = float(CREATURE_MAX_ENERGY)
        self.has_eaten = 0
        self.is_survivor = False

    @property
    def radius(self) -> float:
        size_mult = max(0.0001, self.traits.get('size', 1.0))
        return float(self.base_radius) * math.sqrt(size_mult)

    def _normalize_direction(self, direction: Tuple[float, float]) -> Tuple[float, float]:
        mag = math.hypot(direction[0], direction[1])
        if mag <= 0:
            return random_unit_vector()
        return direction[0] / mag, direction[1] / mag

    def _rotate_vector(self, vector: Tuple[float, float], angle: float) -> Tuple[float, float]:
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (
            vector[0] * cos_a - vector[1] * sin_a,
            vector[0] * sin_a + vector[1] * cos_a,
        )

    def steer(self, foods: List, food_radius: int) -> None:
        intelligence = max(0.1, self.traits.get('intelligence', 1.0))
        sensing_range = INTELLIGENCE_BASE_RANGE * intelligence
        nearest_food = None
        nearest_distance = None

        for food in foods:
            dist = distance(self.position, food.position)
            if dist <= sensing_range and (nearest_distance is None or dist < nearest_distance):
                nearest_food = food
                nearest_distance = dist

        if nearest_food is None:
            if random.random() < 0.05:
                self.direction = random_unit_vector()
            return

        target_vector = (
            nearest_food.position[0] - self.position[0],
            nearest_food.position[1] - self.position[1],
        )
        desired_direction = self._normalize_direction(target_vector)

        # Smarter creatures get less angular error, but still imperfect information.
        max_error_radians = math.radians(INTELLIGENCE_BASE_ERROR_DEGREES) / intelligence
        noisy_direction = self._rotate_vector(
            desired_direction,
            random.uniform(-max_error_radians, max_error_radians),
        )
        noisy_direction = self._normalize_direction(noisy_direction)

        if nearest_distance is not None and nearest_distance <= (self.radius + food_radius):
            self.direction = noisy_direction
            return

        turn_weight = max(0.05, min(1.0, INTELLIGENCE_TURN_RATE * intelligence))
        blended_direction = (
            (1.0 - turn_weight) * self.direction[0] + turn_weight * noisy_direction[0],
            (1.0 - turn_weight) * self.direction[1] + turn_weight * noisy_direction[1],
        )
        self.direction = self._normalize_direction(blended_direction)

    def move(self) -> None:
        speed = self.traits.get('speed', 1.0)
        size_mult = max(0.0001, self.traits.get('size', 1.0))
        intelligence = max(0.1, self.traits.get('intelligence', 1.0))
        dx = self.direction[0] * CREATURE_STEP_SIZE * speed
        dy = self.direction[1] * CREATURE_STEP_SIZE * speed
        self.position = (self.position[0] + dx, self.position[1] + dy)
        # energy drained per move scales with speed, size, and modestly with intelligence.
        intelligence_factor = 1.0 + INTELLIGENCE_ENERGY_COST * max(0.0, intelligence - 1.0)
        self.energy -= (1.0 * speed * size_mult * intelligence_factor)

    def handle_edges(self, width: int, height: int) -> None:
        x, y = self.position
        r = self.radius
        touched_edge = (
            x <= r or x >= width - r or
            y <= r or y >= height - r
        )

        if self.has_eaten > 0 and touched_edge:
            self.is_survivor = True
            # clamp into bounds
            x = max(r, min(x, width - r))
            y = max(r, min(y, height - r))
            self.position = (x, y)
            return

        if self.has_eaten == 0:
            bounced = False
            if x < r:
                x = r
                self.direction = (-self.direction[0], self.direction[1])
                bounced = True
            elif x > width - r:
                x = width - r
                self.direction = (-self.direction[0], self.direction[1])
                bounced = True
            if y < r:
                y = r
                self.direction = (self.direction[0], -self.direction[1])
                bounced = True
            elif y > height - r:
                y = height - r
                self.direction = (self.direction[0], -self.direction[1])
                bounced = True
            if bounced:
                if random.random() < 0.5:
                    self.direction = random_unit_vector()
            self.position = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        color = (220, 60, 60) if (not self.is_survivor and self.energy <= 0) else (61, 178, 255)
        pygame.draw.circle(surface, color, (int(self.position[0]), int(self.position[1])), int(self.radius))


class MutationSimulation(Simulation):
    def __init__(
        self,
        width: int,
        height: int,
        mutation_speed_enabled: bool = True,
        mutation_size_enabled: bool = True,
        mutation_intelligence_enabled: bool = True,
    ):
        super().__init__(width, height)
        self.mutation_speed_enabled = mutation_speed_enabled
        self.mutation_size_enabled = mutation_size_enabled
        self.mutation_intelligence_enabled = mutation_intelligence_enabled
        self.base_radius = CREATURE_RADIUS
        num_creatures = START_CREATURES.get('mutation_simulation', START_CREATURES.get('basic_simulation', 5))
        for _ in range(num_creatures):
            start_pos = point_on_random_edge(self.width, self.height, margin=self.base_radius)
            self.creatures.append(Creature(position=start_pos, direction=random_unit_vector(), base_radius=self.base_radius))

    def spawn_food_for_day(self, start_creature_count: int) -> None:
        if getattr(self, 'food_scaling', True):
            count = start_creature_count
        else:
            fixed = getattr(self, 'fixed_food_count', None)
            count = fixed if (isinstance(fixed, int) and fixed >= 0) else start_creature_count
        self.foods = []
        margin = max(FOOD_RADIUS + 2, self.base_radius + 2)
        for _ in range(count):
            pos = random_point_interior(self.width, self.height, margin)
            self.foods.append(Food(position=pos))
        self.food_spawned = count

    def reproduce_survivors(self) -> None:
        survivors = [c for c in self.creatures if c.is_survivor]
        new_creatures: List[Creature] = []
        speed_mut_on = getattr(self, 'mutation_speed_enabled', True)
        size_mut_on = getattr(self, 'mutation_size_enabled', True)
        intelligence_mut_on = getattr(self, 'mutation_intelligence_enabled', True)
        for survivor in survivors:
            # recreate the survivor on the edge
            pos = point_on_random_edge(self.width, self.height, margin=self.base_radius)
            new_creatures.append(Creature(
                position=pos,
                direction=random_unit_vector(),
                speed_mult=survivor.traits.get('speed', 1.0),
                size_mult=survivor.traits.get('size', 1.0),
                intelligence_mult=survivor.traits.get('intelligence', 1.0),
                base_radius=self.base_radius,
            ))
            # if they ate 2 or more foods, they replicate once with possible mutation
            if survivor.has_eaten >= 2:
                # child inherits speed with a percent change in [-MUTATION_SPEED_DELTA, +MUTATION_SPEED_DELTA]
                parent_speed = survivor.traits.get('speed', 1.0)
                parent_size = survivor.traits.get('size', 1.0)
                parent_intelligence = survivor.traits.get('intelligence', 1.0)

                speed_val = self._mutate_trait(parent_speed, MUTATION_SPEED_DELTA, enabled=speed_mut_on)
                size_val = self._mutate_trait(parent_size, MUTATION_SIZE_DELTA, enabled=size_mut_on)
                intelligence_val = self._mutate_trait(
                    parent_intelligence,
                    MUTATION_INTELLIGENCE_DELTA,
                    enabled=intelligence_mut_on,
                )

                pos2 = point_on_random_edge(self.width, self.height, margin=self.base_radius)
                new_creatures.append(Creature(
                    position=pos2,
                    direction=random_unit_vector(),
                    speed_mult=speed_val,
                    size_mult=size_val,
                    intelligence_mult=intelligence_val,
                    base_radius=self.base_radius,
                ))
        self.creatures = new_creatures

    def handle_creature_collision(self, creature, food_index: int) -> None:
        creature.has_eaten += 1
        # add energy from food, clamped
        creature.energy = min(creature.energy + FOOD_ENERGY, float(self.get_creature_max_energy()))

    def move_creature(self, creature: Creature) -> None:
        creature.steer(self.foods, self.get_food_radius())
        creature.move()

    def get_simulation_name(self) -> str:
        return 'MutationSimulation'

    def get_creature_max_energy(self) -> int:
        return CREATURE_MAX_ENERGY

    def get_creature_radius(self) -> int:
        # base radius; actual radius may vary per creature via size trait
        return self.base_radius

    def get_creature_radius_for(self, creature: Creature) -> float:
        try:
            return float(getattr(creature, 'radius', self.base_radius))
        except Exception:
            return float(self.base_radius)

    def get_food_radius(self) -> int:
        return FOOD_RADIUS

    def distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return distance(a, b)

    @staticmethod
    def _mutate_trait(value: float, delta: float, enabled: bool = True) -> float:
        if not enabled:
            return float(value)
        change = random.uniform(-delta, delta)
        mutated = float(value) * (1.0 + change)
        # prevent collapsing to zero/negative size or speed
        return max(0.1, mutated)
