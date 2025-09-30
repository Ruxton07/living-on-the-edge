import sys
import os
import csv
import pygame

from constants import WORLD_WIDTH, WORLD_HEIGHT, BACKGROUND_COLOR, EDGE_COLOR
from basic_simulation import BasicSimulation
from greedy_simulation import GreedySimulation


# run_simulation()
# 
# @return None
# 
def run_simulation() -> None:
    # Initialize pygame, present a simple menu to choose a simulation, then run it.
    pygame.init()
    # Use SCALED to handle HiDPI/Retina so the logical size appears correct
    screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption('Ecosystem Simulator – Select Simulation')
    clock = pygame.time.Clock()

    def draw_menu() -> None:
        # Dynamically size menu based on current window size to avoid cutoff
        screen.fill(BACKGROUND_COLOR)
        width, height = screen.get_size()
        pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)

        # Font sizes relative to window height; anti-aliased and smaller scaling
        title_size = max(14, int(height * 0.05))
        option_size = max(12, int(height * 0.04))
        hint_size = max(10, int(height * 0.03))
        title_font = pygame.font.Font(pygame.font.get_default_font(), title_size)
        option_font = pygame.font.Font(pygame.font.get_default_font(), option_size)
        hint_font = pygame.font.Font(pygame.font.get_default_font(), hint_size)

        title_surf = title_font.render('Select Simulation:', True, (240, 240, 245))
        option1_surf = option_font.render('1) BasicSimulation', True, (220, 220, 230))
        option2_surf = option_font.render('2) GreedySimulation', True, (220, 220, 230))
        hint_surf = hint_font.render('Esc to quit | \\ to show chart early', True, (180, 180, 190))

        # Positions centered horizontally, spaced vertically
        y_center = height * 0.35
        spacing = max(8, int(height * 0.05))
        title_pos = (width // 2 - title_surf.get_width() // 2, int(y_center - spacing * 1.5))
        option1_pos = (width // 2 - option1_surf.get_width() // 2, int(y_center))
        option2_pos = (width // 2 - option2_surf.get_width() // 2, int(y_center + spacing))
        hint_pos = (width // 2 - hint_surf.get_width() // 2, int(y_center + spacing * 2.5))

        screen.blit(title_surf, title_pos)
        screen.blit(option1_surf, option1_pos)
        screen.blit(option2_surf, option2_pos)
        screen.blit(hint_surf, hint_pos)
        pygame.display.flip()

    selected = None
    while selected is None:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_1:
                    selected = 'BasicSimulation'
                if event.key == pygame.K_2:
                    selected = 'GreedySimulation'
        clock.tick(30)

    pygame.display.set_caption(f'Ecosystem Simulator – {selected}')
    simulation_id = 1
    current_speed_steps = 1
    while True:
        if selected == 'BasicSimulation':
            sim = BasicSimulation(WORLD_WIDTH, WORLD_HEIGHT)
        elif selected == 'GreedySimulation':
            sim = GreedySimulation(WORLD_WIDTH, WORLD_HEIGHT)
        else:
            sim = BasicSimulation(WORLD_WIDTH, WORLD_HEIGHT)

        sim.speed_steps = max(1, current_speed_steps)
        pygame.display.set_caption(f'Ecosystem Simulator – {selected} (x{sim.speed_steps})')

        day = 0
        # Collect per-day stats for graphing and recent CSV. Limit to 20 days.
        day_rows = []  # list of (day, start, food, survivors, died, end)
        while True:
            if len(sim.creatures) == 0:
                break
            day += 1
            sim.day = day

            start_creatures, food_spawned, survivors, died = sim.simulate_day(screen, clock)
            current_speed_steps = sim.speed_steps
            sim.log_day(simulation_id, day, start_creatures, food_spawned, survivors, died)
            end_creatures = survivors
            if len(day_rows) < 20:
                day_rows.append((day, start_creatures, food_spawned, survivors, died, end_creatures))

            # Stop conditions: extinction or reached 20 days
            if survivors == 0 or day >= 20 or getattr(sim, 'manual_stop', False):
                screen.fill(BACKGROUND_COLOR)
                pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, sim.width, sim.height), width=2)
                for creature in sim.creatures:
                    creature.draw(screen)
                for food in sim.foods:
                    food.draw(screen)
                # Also render a simple graph of population vs day (start-of-day population)
                render_population_graph(screen, day_rows)
                pygame.display.flip()
                # Increase base delay to 5000ms and scale with speed
                base_delay_ms = 5000
                delay_ms = max(500, base_delay_ms // max(1, sim.speed_steps))
                # Write/update recent CSV (last 10 simulations x up to 20 days)
                write_recent_csv(simulation_id, day_rows)
                pygame.time.delay(delay_ms)
                break

            sim.reproduce_survivors()

        simulation_id += 1


# write_recent_csv(simulation_id, day_rows)
# 
# @param simulation_id  id of the finished simulation
# @param day_rows  list of tuples (day, start, food, survivors, died, end)
# @return None
# 
def write_recent_csv(simulation_id: int, day_rows: list) -> None:
    log_dir = os.path.join(os.getcwd(), 'log')
    os.makedirs(log_dir, exist_ok=True)
    recent_path = os.path.join(log_dir, 'recent_stats.csv')

    # Load existing rows
    existing = []
    if os.path.exists(recent_path):
        with open(recent_path, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for r in reader:
                try:
                    existing.append((int(r[0]), int(r[1]), int(r[2]), int(r[3]), int(r[4]), int(r[5]), int(r[6])))
                except Exception:
                    continue
    # Append this simulation's rows (cap to 20 already ensured by caller)
    for (day, start_c, food, surv, died, end_c) in day_rows:
        existing.append((simulation_id, day, start_c, food, surv, died, end_c))

    # Keep only last 10 simulation ids
    sim_ids = sorted({sid for (sid, *_rest) in existing}, reverse=True)
    keep_ids = set(sim_ids[:10])
    filtered = [r for r in existing if r[0] in keep_ids]
    # Sort by sim_id then day
    filtered.sort(key=lambda r: (r[0], r[1]))

    # Write back
    with open(recent_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sim_id', 'day', 'start_creatures', 'food_spawned', 'survivors', 'died', 'end_creatures'])
        for r in filtered:
            writer.writerow(r)


# render_population_graph(screen, day_rows)
# 
# @param screen  pygame surface to draw graph on
# @param day_rows  list of tuples (day, start, food, survivors, died, end)
# @return None
# 
def render_population_graph(screen: pygame.Surface, day_rows: list) -> None:
    # Draw a simple line graph of start population vs day in the lower-right area
    width = screen.get_width()
    height = screen.get_height()
    # Calculate margins to make graph 75% of original size but centered
    original_margin = 40
    original_graph_width = width - 2 * original_margin
    original_graph_height = height - 2 * original_margin
    new_graph_width = int(0.75 * original_graph_width)
    new_graph_height = int(0.75 * original_graph_height)
    margin_x = (width - new_graph_width) // 2
    margin_y = (height - new_graph_height) // 2
    graph_rect = pygame.Rect(margin_x, margin_y, new_graph_width, new_graph_height)
    # Axes
    axis_color = (180, 180, 190)
    pygame.draw.rect(screen, EDGE_COLOR, graph_rect, width=1)
    # Extract data
    if not day_rows:
        return
    days = [row[0] for row in day_rows]
    pops = [row[1] for row in day_rows]  # start_creatures per day
    max_day = max(days)
    max_pop = max(max(pops), 1)
    # Scale and draw line
    points = []
    for (d, p) in zip(days, pops):
        x = graph_rect.left + (d - 1) / max(1, 20 - 1) * graph_rect.width
        y = graph_rect.bottom - (p / max_pop) * graph_rect.height
        points.append((int(x), int(y)))
    if len(points) >= 2:
        pygame.draw.lines(screen, (80, 200, 120), False, points, 2)
    elif len(points) == 1:
        pygame.draw.circle(screen, (80, 200, 120), points[0], 2)
    # Draw axes ticks/labels (minimal)
    font = pygame.font.SysFont(None, 18)
    label = font.render('Population vs Day (start of day)', True, (200, 200, 210))
    screen.blit(label, (graph_rect.left, graph_rect.top - 22))
    # Day labels 1 and 20
    d1 = font.render('1', True, (160, 160, 170))
    d20 = font.render('20', True, (160, 160, 170))
    screen.blit(d1, (graph_rect.left - 5, graph_rect.bottom + 4))
    screen.blit(d20, (graph_rect.right - 20, graph_rect.bottom + 4))
    # Max pop label
    mp = font.render(str(max_pop), True, (160, 160, 170))
    screen.blit(mp, (graph_rect.left - 30, graph_rect.top - 8))


if __name__ == '__main__':
    run_simulation()


