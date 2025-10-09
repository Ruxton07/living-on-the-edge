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
        option3_surf = option_font.render('3) inc_food_basic_sim (increment food each run)', True, (220, 220, 230))
        option4_surf = option_font.render('4) inc_food_greedy_sim (increment food each run)', True, (220, 220, 230))
        hint_surf = hint_font.render('Esc to quit | \\ to show chart early', True, (180, 180, 190))

        # Positions centered horizontally, spaced vertically
        y_center = height * 0.35
        spacing = max(8, int(height * 0.05))
        title_pos = (width // 2 - title_surf.get_width() // 2, int(y_center - spacing * 1.5))
        option1_pos = (width // 2 - option1_surf.get_width() // 2, int(y_center))
        option2_pos = (width // 2 - option2_surf.get_width() // 2, int(y_center + spacing))
        option3_pos = (width // 2 - option3_surf.get_width() // 2, int(y_center + spacing * 2))
        option4_pos = (width // 2 - option4_surf.get_width() // 2, int(y_center + spacing * 3))
        hint_pos = (width // 2 - hint_surf.get_width() // 2, int(y_center + spacing * 4.5))

        screen.blit(title_surf, title_pos)
        screen.blit(option1_surf, option1_pos)
        screen.blit(option2_surf, option2_pos)
        screen.blit(option3_surf, option3_pos)
        screen.blit(option4_surf, option4_pos)
        screen.blit(hint_surf, hint_pos)
        pygame.display.flip()

    # Wrapper for preliminary menu that has access to screen and clock
    def draw_preliminary_menu_local() -> str:
        # Returns 'run' or 'view'
        while True:
            screen.fill(BACKGROUND_COLOR)
            width, height = screen.get_size()
            pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)
            title_font = pygame.font.Font(pygame.font.get_default_font(), max(14, int(height * 0.05)))
            opt_font = pygame.font.Font(pygame.font.get_default_font(), max(12, int(height * 0.04)))
            title = title_font.render('Main Menu', True, (240, 240, 245))
            opt1 = opt_font.render('1) Run simulations', True, (220, 220, 230))
            opt2 = opt_font.render('2) View graphs', True, (220, 220, 230))
            screen.blit(title, (width // 2 - title.get_width() // 2, int(height * 0.25)))
            screen.blit(opt1, (width // 2 - opt1.get_width() // 2, int(height * 0.4)))
            screen.blit(opt2, (width // 2 - opt2.get_width() // 2, int(height * 0.47)))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return 'run'
                    if event.key == pygame.K_2:
                        return 'view'
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
            clock.tick(30)

    def view_graphs_flow_local() -> None:
        files = [
            ('Basic avg population vs food', os.path.join(os.getcwd(), 'log', 'basic_average_population_vs_food.csv')),
            ('Greedy avg population vs food', os.path.join(os.getcwd(), 'log', 'greedy_average_population_vs_food.csv')),
        ]
        idx = 0
        while True:
            screen.fill(BACKGROUND_COLOR)
            # Draw selected CSV graph
            title, path = files[idx]
            render_csv_graph(screen, path)
            # Draw footer text
            font = pygame.font.SysFont(None, 18)
            info = font.render(f'{title} | Left/Right to switch | Esc to return', True, (200, 200, 210))
            screen.blit(info, (10, screen.get_height() - 24))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        idx = (idx + 1) % len(files)
                    if event.key == pygame.K_LEFT:
                        idx = (idx - 1) % len(files)
                    if event.key == pygame.K_ESCAPE:
                        return
            clock.tick(30)

    # Preliminary menu: choose to run simulations or view stored graphs
    while True:
        choice = draw_preliminary_menu_local()
        if choice == 'view':
            view_graphs_flow_local()
            continue
        if choice == 'run':
            break

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
                if event.key == pygame.K_3:
                    selected = 'inc_food_basic_sim'
                if event.key == pygame.K_4:
                    selected = 'inc_food_greedy_sim'
        clock.tick(30)
    # After selecting simulation type, ask whether food should scale with population
    def draw_scale_menu() -> None:
        screen.fill(BACKGROUND_COLOR)
        width, height = screen.get_size()
        pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)
        title_size = max(14, int(height * 0.05))
        option_size = max(12, int(height * 0.04))
        title_font = pygame.font.Font(pygame.font.get_default_font(), title_size)
        option_font = pygame.font.Font(pygame.font.get_default_font(), option_size)
        title = title_font.render('Scale food with population?', True, (240, 240, 245))
        opt_yes = option_font.render('Y) Yes', True, (220, 220, 230))
        opt_no = option_font.render('N) No (specify amount)', True, (220, 220, 230))
        screen.blit(title, (width // 2 - title.get_width() // 2, int(height * 0.35 - 30)))
        screen.blit(opt_yes, (width // 2 - opt_yes.get_width() // 2, int(height * 0.4)))
        screen.blit(opt_no, (width // 2 - opt_no.get_width() // 2, int(height * 0.45)))
        pygame.display.flip()

    def prompt_fixed_amount(initial: int = 5) -> int:
        # allow user to type an integer amount (digits), Backspace to edit, Enter to confirm
        value_str = str(initial)
        while True:
            screen.fill(BACKGROUND_COLOR)
            width, height = screen.get_size()
            pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)
            title_size = max(14, int(height * 0.05))
            option_size = max(12, int(height * 0.04))
            title_font = pygame.font.Font(pygame.font.get_default_font(), title_size)
            option_font = pygame.font.Font(pygame.font.get_default_font(), option_size)
            title = title_font.render('Set fixed food amount', True, (240, 240, 245))
            amt = option_font.render(f'Amount: {value_str}', True, (220, 220, 230))
            hint = option_font.render('Type a number | Backspace to edit | Enter to confirm | Esc to cancel', True, (160, 160, 170))
            screen.blit(title, (width // 2 - title.get_width() // 2, int(height * 0.35 - 36)))
            screen.blit(amt, (width // 2 - amt.get_width() // 2, int(height * 0.4)))
            screen.blit(hint, (width // 2 - hint.get_width() // 2, int(height * 0.48)))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return initial
                    # handle digits (both main keyboard and numpad)
                    if event.unicode and event.unicode.isdigit():
                        # append digit, avoid leading zeros unless intended
                        if value_str == '0':
                            value_str = event.unicode
                        else:
                            value_str += event.unicode
                    elif event.key == pygame.K_BACKSPACE:
                        value_str = value_str[:-1] if len(value_str) > 0 else ''
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        try:
                            val = int(value_str) if value_str != '' else 0
                        except ValueError:
                            val = initial
                        return max(0, val)
            clock.tick(30)

    scale_food = None
    fixed_food_amount = None
    # If an incremental-food sim was selected, skip scale prompt and ask for a starting fixed food
    if selected in ('inc_food_basic_sim', 'inc_food_greedy_sim'):
        # Prompt for starting food amount (default 5)
        fixed_food_amount = prompt_fixed_amount(initial=5)
        scale_food = False
    else:
        while scale_food is None:
            draw_scale_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_y or event.key == pygame.K_1:
                    scale_food = True
                if event.key == pygame.K_n or event.key == pygame.K_2:
                    scale_food = False
        clock.tick(30)

    if scale_food is False and selected not in ('inc_food_basic_sim', 'inc_food_greedy_sim'):
        # Prompt for fixed food amount (default 5)
        fixed_food_amount = prompt_fixed_amount(initial=5)

    # Ask whether verbose logging should be enabled (default off)
    def draw_verbose_menu() -> None:
        screen.fill(BACKGROUND_COLOR)
        width, height = screen.get_size()
        pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)
        title_size = max(14, int(height * 0.05))
        option_size = max(12, int(height * 0.04))
        title_font = pygame.font.Font(pygame.font.get_default_font(), title_size)
        option_font = pygame.font.Font(pygame.font.get_default_font(), option_size)
        title = title_font.render('Verbose logging?', True, (240, 240, 245))
        opt_yes = option_font.render('Y) Yes', True, (220, 220, 230))
        opt_no = option_font.render('N) No (default)', True, (220, 220, 230))
        hint = option_font.render('Verbose: print per-day details to console', True, (160, 160, 170))
        screen.blit(title, (width // 2 - title.get_width() // 2, int(height * 0.35 - 30)))
        screen.blit(opt_yes, (width // 2 - opt_yes.get_width() // 2, int(height * 0.4)))
        screen.blit(opt_no, (width // 2 - opt_no.get_width() // 2, int(height * 0.45)))
        screen.blit(hint, (width // 2 - hint.get_width() // 2, int(height * 0.52)))
        pygame.display.flip()

    verbose_choice = None
    while verbose_choice is None:
        draw_verbose_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_y:
                    verbose_choice = True
                if event.key == pygame.K_n:
                    verbose_choice = False
        clock.tick(30)

    pygame.display.set_caption(f'Ecosystem Simulator – {selected}')
    simulation_id = 1
    current_speed_steps = 1
    while True:
        # For incremental-food sims we will run a sequence of simulations (50 runs)
        if selected in ('inc_food_basic_sim', 'inc_food_greedy_sim'):
            # starting food is fixed_food_amount
            start_food = fixed_food_amount if isinstance(fixed_food_amount, int) else 5
            runs = 50
            # determine CSV path base name
            if selected == 'inc_food_basic_sim':
                avg_csv_name = 'basic_average_population_vs_food.csv'
                sim_factory = BasicSimulation
            else:
                avg_csv_name = 'greedy_average_population_vs_food.csv'
                sim_factory = GreedySimulation
            # ensure log dir exists
            log_dir = os.path.join(os.getcwd(), 'log')
            os.makedirs(log_dir, exist_ok=True)
            avg_csv_path = os.path.join(log_dir, avg_csv_name)
            # write header if missing
            if not os.path.exists(avg_csv_path):
                with open(avg_csv_path, 'w', newline='') as f:
                    w = csv.writer(f)
                    w.writerow(['food', 'average_population'])

            current_food = start_food
            run_idx = 1
            # Infinite sequence of runs; each run lasts exactly 50 days. User may terminate the program when done.
            while True:
                sim = sim_factory(WORLD_WIDTH, WORLD_HEIGHT)
                # Force non-scaling and fixed food
                setattr(sim, 'food_scaling', False)
                setattr(sim, 'fixed_food_count', int(current_food))
                setattr(sim, 'verbose', bool(verbose_choice))
                sim.speed_steps = max(1, current_speed_steps)
                pygame.display.set_caption(f'Ecosystem Simulator – {selected} (run {run_idx}/{runs} food={current_food})')

                # Each run lasts exactly 50 days. We still allow early extinction but continue counting days.
                day_rows = []
                for day in range(1, 50 + 1):
                    sim.day = day

                    start_creatures, food_spawned, survivors, died = sim.simulate_day(screen, clock)
                    current_speed_steps = sim.speed_steps
                    sim.log_day(simulation_id, day, start_creatures, food_spawned, survivors, died)
                    end_creatures = survivors
                    day_rows.append((day, start_creatures, food_spawned, survivors, died, end_creatures))

                    # reproduce survivors to set up next day
                    sim.reproduce_survivors()

                    # Allow user to manually stop an individual day/run via sim.manual_stop (handled by simulate_day)
                    if getattr(sim, 'manual_stop', False):
                        break

                # At end of 50-day run (or earlier if manual_stop), show final frame and write recent CSV
                screen.fill(BACKGROUND_COLOR)
                pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, sim.width, sim.height), width=2)
                for creature in sim.creatures:
                    creature.draw(screen)
                for food in sim.foods:
                    food.draw(screen)
                render_population_graph(screen, day_rows[-20:])
                pygame.display.flip()
                base_delay_ms = 5000
                delay_ms = max(500, base_delay_ms // max(1, sim.speed_steps))
                write_recent_csv(simulation_id, day_rows)
                pygame.time.delay(delay_ms)

                # After the run, compute average population (average start_creatures per day)
                if day_rows:
                    avg_pop = sum(r[1] for r in day_rows) / len(day_rows)
                else:
                    avg_pop = 0
                # Append to avg CSV
                with open(avg_csv_path, 'a', newline='') as f:
                    w = csv.writer(f)
                    w.writerow([int(current_food), float(avg_pop)])

                # Increment food for next run and loop (user will terminate when they've seen enough)
                current_food += 1
                simulation_id += 1
                run_idx += 1

            # (never reached) continue
        if selected == 'BasicSimulation':
            sim = BasicSimulation(WORLD_WIDTH, WORLD_HEIGHT)
        elif selected == 'GreedySimulation':
            sim = GreedySimulation(WORLD_WIDTH, WORLD_HEIGHT)
        else:
            sim = BasicSimulation(WORLD_WIDTH, WORLD_HEIGHT)

        # Apply food-scaling options selected in the menu
        # Default: scaling enabled
        setattr(sim, 'food_scaling', True if scale_food is None else bool(scale_food))
        setattr(sim, 'fixed_food_count', fixed_food_amount if fixed_food_amount is not None else None)
        # Apply verbose option
        setattr(sim, 'verbose', bool(verbose_choice))

        sim.speed_steps = max(1, current_speed_steps)
        pygame.display.set_caption(f'Ecosystem Simulator – {selected} (x{sim.speed_steps})')

        day = 0
        # Collect per-day stats for graphing and recent CSV. Keep all days; graph will show last 20.
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
            # Always record day rows (we'll show the most recent N in the graph)
            day_rows.append((day, start_creatures, food_spawned, survivors, died, end_creatures))

            # Stop conditions: extinction or manual stop
            if survivors == 0 or getattr(sim, 'manual_stop', False):
                screen.fill(BACKGROUND_COLOR)
                pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, sim.width, sim.height), width=2)
                for creature in sim.creatures:
                    creature.draw(screen)
                for food in sim.foods:
                    food.draw(screen)
                # Also render a simple graph of population vs day (start-of-day population)
                # Render only the most recent 20 days for clarity
                render_population_graph(screen, day_rows[-20:])
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
    min_day = min(days)
    max_day = max(days)
    max_pop = max(max(pops), 1)
    # Add 5% headroom above max for easier viewing
    display_max_pop = max_pop * 1.05
    # Scale and draw line
    points = []
    for (d, p) in zip(days, pops):
        if max_day == min_day:
            # single point -> center horizontally
            x = graph_rect.left + graph_rect.width / 2
        else:
            x = graph_rect.left + (d - min_day) / max(1, (max_day - min_day)) * graph_rect.width
        # y axis always begins at 0
        y = graph_rect.bottom - (p / display_max_pop) * graph_rect.height
        points.append((int(x), int(y)))
    if len(points) >= 2:
        pygame.draw.lines(screen, (80, 200, 120), False, points, 2)
    elif len(points) == 1:
        pygame.draw.circle(screen, (80, 200, 120), points[0], 2)
    # Draw axes ticks/labels (minimal)
    font = pygame.font.SysFont(None, 18)
    label = font.render('Population vs Day (start of day)', True, (200, 200, 210))
    screen.blit(label, (graph_rect.left, graph_rect.top - 22))
    # Day labels min and max
    d_min_label = font.render(str(min_day), True, (160, 160, 170))
    d_max_label = font.render(str(max_day), True, (160, 160, 170))
    screen.blit(d_min_label, (graph_rect.left - 5, graph_rect.bottom + 4))
    screen.blit(d_max_label, (graph_rect.right - d_max_label.get_width(), graph_rect.bottom + 4))
    # Y-axis labels: 0 at bottom and max_pop at top; show intermediate ticks
    y0 = font.render('0', True, (160, 160, 170))
    y_mid_val = int(max_pop / 2)
    y_mid = font.render(str(y_mid_val), True, (160, 160, 170))
    mp = font.render(str(max_pop), True, (160, 160, 170))
    screen.blit(y0, (graph_rect.left - 18, graph_rect.bottom - 8))
    screen.blit(y_mid, (graph_rect.left - 28, int(graph_rect.top + graph_rect.height / 2) - 8))
    screen.blit(mp, (graph_rect.left - 30, graph_rect.top - 8))
    # Draw Y ticks
    pygame.draw.line(screen, axis_color, (graph_rect.left - 6, graph_rect.bottom), (graph_rect.left, graph_rect.bottom), 1)
    pygame.draw.line(screen, axis_color, (graph_rect.left - 6, int(graph_rect.top + graph_rect.height / 2)), (graph_rect.left, int(graph_rect.top + graph_rect.height / 2)), 1)
    pygame.draw.line(screen, axis_color, (graph_rect.left - 6, graph_rect.top), (graph_rect.left, graph_rect.top), 1)
    # Draw intermediate X ticks (up to 5 ticks)
    tick_count = min(5, max(2, max_day - min_day + 1))
    for i in range(tick_count):
        tx = graph_rect.left + i / max(1, tick_count - 1) * graph_rect.width
        pygame.draw.line(screen, axis_color, (int(tx), graph_rect.bottom), (int(tx), graph_rect.bottom + 6), 1)
        # Label every tick
        label_day = int(min_day + i / max(1, tick_count - 1) * (max_day - min_day))
        lbl = font.render(str(label_day), True, (160, 160, 170))
        screen.blit(lbl, (int(tx) - lbl.get_width() // 2, graph_rect.bottom + 6))


def render_csv_graph(screen: pygame.Surface, csv_path: str) -> None:
    # Read CSV of two columns: food, average_population
    if not os.path.exists(csv_path):
        # Display message
        width, height = screen.get_size()
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(None, 20)
        msg = font.render('CSV not found: ' + os.path.basename(csv_path), True, (200, 200, 210))
        screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 10))
        pygame.display.flip()
        return

    xs = []
    ys = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for r in reader:
            try:
                x = float(r[0])
                y = float(r[1])
            except Exception:
                continue
            xs.append(x)
            ys.append(y)

    if not xs:
        return

    # Build day_rows-like structure where x is food (treated as day index) and y as population
    day_rows = [(int(x), int(y), 0, 0, 0, 0) for x, y in zip(xs, ys)]

    # Use the same renderer but we need to draw x->index mapping. For simplicity
    # we will map food values to sequential positions and use y as population.
    width = screen.get_width()
    height = screen.get_height()
    # Prepare rect same as render_population_graph
    original_margin = 40
    original_graph_width = width - 2 * original_margin
    original_graph_height = height - 2 * original_margin
    new_graph_width = int(0.75 * original_graph_width)
    new_graph_height = int(0.75 * original_graph_height)
    margin_x = (width - new_graph_width) // 2
    margin_y = (height - new_graph_height) // 2
    graph_rect = pygame.Rect(margin_x, margin_y, new_graph_width, new_graph_height)

    # Draw axes
    pygame.draw.rect(screen, EDGE_COLOR, graph_rect, width=1)
    font = pygame.font.SysFont(None, 18)
    label = font.render('Average Population vs Food', True, (200, 200, 210))
    screen.blit(label, (graph_rect.left, graph_rect.top - 22))

    max_y = max(ys)
    display_max_y = max_y * 1.05

    points = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        px = graph_rect.left + (i / max(1, len(xs) - 1)) * graph_rect.width
        py = graph_rect.bottom - (y / display_max_y) * graph_rect.height
        points.append((int(px), int(py)))

    if len(points) >= 2:
        pygame.draw.lines(screen, (120, 180, 220), False, points, 2)
    elif len(points) == 1:
        pygame.draw.circle(screen, (120, 180, 220), points[0], 3)

    # Labels and ticks
    axis_color = (180, 180, 190)
    if xs:
        left_label = font.render(str(int(xs[0])), True, (160, 160, 170))
        right_label = font.render(str(int(xs[-1])), True, (160, 160, 170))
        screen.blit(left_label, (graph_rect.left - 10, graph_rect.bottom + 4))
        screen.blit(right_label, (graph_rect.right - right_label.get_width(), graph_rect.bottom + 4))
        # Y ticks and labels: 0, mid, max
        y0 = font.render('0', True, (160, 160, 170))
        y_mid_val = int(max_y / 2)
        y_mid = font.render(str(y_mid_val), True, (160, 160, 170))
        y_max = font.render(str(int(max_y)), True, (160, 160, 170))
        screen.blit(y0, (graph_rect.left - 18, graph_rect.bottom - 8))
        screen.blit(y_mid, (graph_rect.left - 28, int(graph_rect.top + graph_rect.height / 2) - 8))
        screen.blit(y_max, (graph_rect.left - 30, graph_rect.top - 8))
        # Draw Y tick marks
        pygame.draw.line(screen, axis_color, (graph_rect.left - 6, graph_rect.bottom), (graph_rect.left, graph_rect.bottom), 1)
        pygame.draw.line(screen, axis_color, (graph_rect.left - 6, int(graph_rect.top + graph_rect.height / 2)), (graph_rect.left, int(graph_rect.top + graph_rect.height / 2)), 1)
        pygame.draw.line(screen, axis_color, (graph_rect.left - 6, graph_rect.top), (graph_rect.left, graph_rect.top), 1)
        # Draw X ticks (up to 7 ticks depending on food count)
        tick_count = min(7, max(2, len(xs)))
        for i in range(tick_count):
            tx = graph_rect.left + i / max(1, tick_count - 1) * graph_rect.width
            pygame.draw.line(screen, axis_color, (int(tx), graph_rect.bottom), (int(tx), graph_rect.bottom + 6), 1)
            idx = int(i / max(1, tick_count - 1) * (len(xs) - 1))
            label_food = xs[idx]
            lbl = font.render(str(int(label_food)), True, (160, 160, 170))
            screen.blit(lbl, (int(tx) - lbl.get_width() // 2, graph_rect.bottom + 6))


def draw_preliminary_menu() -> str:
    # Returns 'run' or 'view'
    # This helper requires screen and clock; wrapper in run_simulation will call it
    raise NotImplementedError("draw_preliminary_menu must be called with screen and clock")

def view_graphs_flow() -> None:
    # This helper requires screen and clock; wrapper in run_simulation will call it
    raise NotImplementedError("view_graphs_flow must be called with screen and clock")

if __name__ == '__main__':
    run_simulation()