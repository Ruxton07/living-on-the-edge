from typing import Tuple, List, Optional
import os
import csv
import pygame

from constants import WORLD_WIDTH, WORLD_HEIGHT, BACKGROUND_COLOR, EDGE_COLOR, TICKS_PER_SECOND


class Simulation:
    # Simulation.__init__(width, height)
    # 
    # @param width  the world width in pixels
    # @param height  the world height in pixels
    # @return None
    # 
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.day: int = 0
        # speed controller (steps per frame)
        self.speed_steps: int = 1
        # common simulation state
        self.creatures: List = []
        self.foods: List = []
        self.food_spawned = 0
        # food spawning configuration (menu-controlled)
        self.food_scaling = True
        self.fixed_food_count = None
        self.manual_stop = False
        # verbose logging flag (menu-controlled)
        self.verbose = False

        # prepare logging
        self.log_dir = os.path.join(os.getcwd(), 'log')
        os.makedirs(self.log_dir, exist_ok=True)
        self.csv_path = os.path.join(self.log_dir, 'day_stats.csv')
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['day', 'start_creatures', 'food_spawned', 'survivors', 'died', 'end_creatures'])

    # Simulation.spawn_food_for_day(start_creature_count)
    # 
    # @param start_creature_count  number of creatures alive at day start
    # @return None
    # 
    def spawn_food_for_day(self, start_creature_count: int) -> None:
        raise NotImplementedError

    # Simulation.reproduce_survivors()
    # 
    # @return None
    # 
    def reproduce_survivors(self) -> None:
        raise NotImplementedError

    # Simulation.handle_creature_collision(creature, food_index)
    # 
    # @param creature  the creature that collided
    # @param food_index  index of the food that was eaten
    # @return None
    # 
    def handle_creature_collision(self, creature, food_index: int) -> None:
        raise NotImplementedError

    # Simulation.simulate_day(screen, clock)
    # 
    # @param screen  the pygame screen surface for drawing
    # @param clock  the pygame clock for frame timing
    # @return (start_creatures, food_spawned, survivors, died)
    # 
    def simulate_day(self, screen: pygame.Surface, clock: pygame.time.Clock) -> Tuple[int, int, int, int]:
        # reset daily flags
        for c in self.creatures:
            c.energy = self.get_creature_max_energy()
            c.has_eaten = 0
            c.is_survivor = False

        start_creatures = len(self.creatures)
        if start_creatures == 0:
            return 0, 0, 0, 0

        self.spawn_food_for_day(start_creatures)

        running_day = True
        self.manual_stop = False
        while running_day:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        # allow doubling up to 128x
                        self.speed_steps = min(128, self.speed_steps * 2)
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                        self.speed_steps = max(1, max(1, self.speed_steps // 2))
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_BACKSLASH:
                        # manual stop: end the day immediately and proceed to charts
                        self.manual_stop = True
                        running_day = False
                        break
                    elif event.key == pygame.K_1:
                        self.speed_steps = 1
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_2:
                        self.speed_steps = 2
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_3:
                        self.speed_steps = 4
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_4:
                        self.speed_steps = 8
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_5:
                        self.speed_steps = 16
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_6:
                        self.speed_steps = 32
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_7:
                        self.speed_steps = 64
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')
                    elif event.key == pygame.K_8:
                        self.speed_steps = 128
                        pygame.display.set_caption(f'Ecosystem Simulator – {self.get_simulation_name()} (x{self.speed_steps})')

            for _ in range(self.speed_steps):
                # Cceate a copy to iterate over to avoid issues with list modification
                creatures_to_process = self.creatures.copy()
                for creature in creatures_to_process:
                    if creature.is_survivor:
                        continue
                    if creature.energy <= 0:
                        continue
                    creature.move()
                    creature.handle_edges(self.width, self.height)
                    # allow creatures to eat multiple foods per day: do not gate
                    # collisions on has_eaten. Only require the creature to be alive.
                    if creature.energy > 0:
                        collided_index: Optional[int] = None
                        for idx, food in enumerate(self.foods):
                            if self.distance(creature.position, food.position) <= (self.get_creature_radius() + self.get_food_radius()):
                                collided_index = idx
                                break
                        if collided_index is not None:
                            del self.foods[collided_index]
                            self.handle_creature_collision(creature, collided_index)

                # if no food remains, all uneaten creatures instantly die
                if len(self.foods) == 0:
                    for c in self.creatures:
                        if c.has_eaten == 0 and not c.is_survivor and c.energy > 0:
                            c.energy = 0

                # check if day finished and only count living creatures (not dead bodies)
                all_done = True
                for c in self.creatures:
                    if c.is_survivor:
                        continue
                    if c.energy > 0:  # Still alive
                        all_done = False
                        break
                if all_done:
                    running_day = False
                    break

            screen.fill(BACKGROUND_COLOR)
            pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, self.width, self.height), width=2)
            for food in self.foods:
                food.draw(screen)
            for creature in self.creatures:
                creature.draw(screen)
            pygame.display.flip()
            clock.tick(TICKS_PER_SECOND)

        # count survivors and deaths (dead creatures still in list as bodies)
        survivors = sum(1 for c in self.creatures if c.is_survivor)
        died = sum(1 for c in self.creatures if (not c.is_survivor))

        # remove dead creatures at end of day for next day's reproduction
        self.creatures = [c for c in self.creatures if c.is_survivor]

        return start_creatures, self.food_spawned, survivors, died

    # Simulation.log_day(sim_id, day, start_creatures, food_spawned, survivors, died)
    # 
    # @param sim_id  the simulation identifier (1-based)
    # @param day  the day index (1-based)
    # @param start_creatures  number of creatures at start of day
    # @param food_spawned  number of food items spawned
    # @param survivors  number of creatures that survived
    # @param died  number of creatures that died
    # @return None
    # 
    def log_day(self, sim_id: int, day: int, start_creatures: int, food_spawned: int, survivors: int, died: int) -> None:
        end_creatures = survivors
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([day, start_creatures, food_spawned, survivors, died, end_creatures])
        # per-day summary only when verbose is enabled
        if getattr(self, 'verbose', False):
            creature_summaries = []
            for idx, c in enumerate(self.creatures, start=1):
                creature_summaries.append(f"#{idx}: eaten={c.has_eaten} energy={c.energy} survivor={c.is_survivor}")
            summary_lines = [f"Simulation {sim_id} | Day {day:03d} | start={start_creatures} food={food_spawned} survived={survivors} died={died} end={end_creatures}"]
            if creature_summaries:
                summary_lines.append("Creatures:")
                # show up to first 10 creature summaries to avoid spamming
                for line in creature_summaries[:10]:
                    summary_lines.append(f"  {line}")
                if len(creature_summaries) > 10:
                    summary_lines.append(f"  ...(+{len(creature_summaries)-10} more)")
            print("\n".join(summary_lines))

    # abstract methods that subclasses must implement
    def get_simulation_name(self) -> str:
        raise NotImplementedError

    def get_creature_max_energy(self) -> int:
        raise NotImplementedError

    def get_creature_radius(self) -> int:
        raise NotImplementedError

    def get_food_radius(self) -> int:
        raise NotImplementedError

    def distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        raise NotImplementedError