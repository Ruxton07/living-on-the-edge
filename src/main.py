import sys
import os
import csv
import pygame

from constants import WORLD_WIDTH, WORLD_HEIGHT, BACKGROUND_COLOR, EDGE_COLOR, SIM_GRAPH_Y_MARGIN, DATA_SIM_RUNS, DATA_SIM_ENERGY_START, DATA_SIM_ENERGY_INCREMENT, MUTATION_SPEED_DELTA, MUTATION_SIZE_DELTA, MUTATION_INTELLIGENCE_DELTA
from basic_simulation import BasicSimulation
from greedy_simulation import GreedySimulation
from mutation_simulation import MutationSimulation


# run_simulation()
#
# @return None
#
def run_simulation() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption('Ecosystem Simulator – Select Simulation')
    clock = pygame.time.Clock()

    def wait_for_results_dismiss(draw_results) -> None:
        while True:
            draw_results()
            font = pygame.font.SysFont(None, 18)
            info = font.render("Press \\ to continue", True, (200, 200, 210))
            screen.blit(info, (10, screen.get_height() - 24))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSLASH:
                    return
            clock.tick(30)

    def draw_menu(mode: str) -> None:
        # dynamically size menu based on current window size to avoid cutoff
        screen.fill(BACKGROUND_COLOR)
        width, height = screen.get_size()
        pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)

        # font sizes relative to window height; anti-aliased and smaller scaling
        title_size = max(14, int(height * 0.05))
        option_size = max(12, int(height * 0.04))
        hint_size = max(10, int(height * 0.03))
        title_font = pygame.font.Font(pygame.font.get_default_font(), title_size)
        option_font = pygame.font.Font(pygame.font.get_default_font(), option_size)
        hint_font = pygame.font.Font(pygame.font.get_default_font(), hint_size)

        # title
        title_surf = title_font.render('Select Simulation:', True, (240, 240, 245))
        # options vary based on mode; caller should pass mode into this function (see draw_mode_menu_local)
        # if mode == 'standard' show basic/greedy; if 'research' show incremental experiments
        if mode == 'standard':
            opts = [
                option_font.render('1) BasicSimulation', True, (220, 220, 230)),
                option_font.render('2) GreedySimulation', True, (220, 220, 230)),
                option_font.render('3) MutationSimulation', True, (220, 220, 230)),
            ]
            hint_text = 'Esc to quit'
        else:
            opts = [
                option_font.render('1) inc_food_basic_sim', True, (220, 220, 230)),
                option_font.render('2) inc_food_greedy_sim', True, (220, 220, 230)),
                option_font.render('3) inc_energy_basic_sim', True, (220, 220, 230)),
                option_font.render('4) inc_energy_greedy_sim', True, (220, 220, 230)),
            ]
            hint_text = 'Esc to quit'

        hint_surf = hint_font.render(hint_text, True, (180, 180, 190))

        # positions centered horizontally, spaced vertically
        y_center = height * 0.35
        spacing = max(8, int(height * 0.05))
        title_pos = (width // 2 - title_surf.get_width() // 2, int(y_center - spacing * 1.5))
        screen.blit(title_surf, title_pos)
        for idx, opt_surf in enumerate(opts):
            pos = (width // 2 - opt_surf.get_width() // 2, int(y_center + spacing * idx))
            screen.blit(opt_surf, pos)
        hint_pos = (width // 2 - hint_surf.get_width() // 2, int(y_center + spacing * (len(opts) + 1)))
        screen.blit(hint_surf, hint_pos)
        pygame.display.flip()

    # wrapper for preliminary menu that has access to screen and clock
    def draw_preliminary_menu_local() -> str:
        # returns 'run' or 'view'
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
            ('Basic avg population vs energy', os.path.join(os.getcwd(), 'log', 'basic_average_population_vs_energy.csv')),
            ('Greedy avg population vs energy', os.path.join(os.getcwd(), 'log', 'greedy_average_population_vs_energy.csv')),
            ('Mutation traits vs day', os.path.join(os.getcwd(), 'log', 'mutation_simulation_traits.csv')),
        ]
        idx = 0
        while True:
            screen.fill(BACKGROUND_COLOR)
            # draw selected CSV graph
            title, path = files[idx]
            base_name = os.path.basename(path).lower()
            # If this is a mutation traits CSV, parse and render multiple graphs
            if 'mutation' in base_name and 'traits' in base_name:
                render_mutation_traits_graphs(screen, path)
            else:
                render_csv_graph(screen, path)
            # draw footer text
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

    # preliminary menu: choose to run simulations or view stored graphs
    while True:
        choice = draw_preliminary_menu_local()
        if choice == 'view':
            view_graphs_flow_local()
            continue
        if choice == 'run':
            break

    # mode selection: standard vs research
    def draw_mode_menu_local() -> str:
        # returns 'standard' or 'research'
        while True:
            screen.fill(BACKGROUND_COLOR)
            width, height = screen.get_size()
            pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)
            title_font = pygame.font.Font(pygame.font.get_default_font(), max(14, int(height * 0.05)))
            opt_font = pygame.font.Font(pygame.font.get_default_font(), max(12, int(height * 0.04)))
            title = title_font.render('Select Mode', True, (240, 240, 245))
            opt1 = opt_font.render('1) standard - run static simulations', True, (220, 220, 230))
            opt2 = opt_font.render('2) research - run incremental experiments', True, (220, 220, 230))
            screen.blit(title, (width // 2 - title.get_width() // 2, int(height * 0.25)))
            screen.blit(opt1, (width // 2 - opt1.get_width() // 2, int(height * 0.4)))
            screen.blit(opt2, (width // 2 - opt2.get_width() // 2, int(height * 0.47)))
            hint = opt_font.render('Press 1 or 2 | Esc to quit', True, (160, 160, 170))
            screen.blit(hint, (width // 2 - hint.get_width() // 2, int(height * 0.54)))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return 'standard'
                    if event.key == pygame.K_2:
                        return 'research'
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
            clock.tick(30)

    mode = draw_mode_menu_local()

    selected = None
    while selected is None:
        draw_menu(mode)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                # Map keys to selections based on mode
                if mode == 'standard':
                    if event.key == pygame.K_1:
                        selected = 'BasicSimulation'
                    if event.key == pygame.K_2:
                        selected = 'GreedySimulation'
                    if event.key == pygame.K_3:
                        selected = 'MutationSimulation'
                else:  # research
                    if event.key == pygame.K_1:
                        selected = 'Incremental Food (Basic)'
                    if event.key == pygame.K_2:
                        selected = 'Incremental Food (Greedy)'
                    if event.key == pygame.K_3:
                        selected = 'Incremental Energy (Basic)'
                    if event.key == pygame.K_4:
                        selected = 'Incremental Energy (Greedy)'
        clock.tick(30)
    # after selecting simulation type, ask whether food should scale with population
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
    # if an incremental-food or incremental-energy sim was selected, skip scale prompt and ask for a starting fixed food
    if selected in ('Incremental Food (Basic)', 'Incremental Food (Greedy)', 'Incremental Energy (Basic)', 'Incremental Energy (Greedy)'):
        # ask for starting food amount (default 5)
        fixed_food_amount = prompt_fixed_amount(initial=5)
        scale_food = False
    else:
        # show the scale menu and handle key events until the user picks Y/N
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
                    # Accept 'y' or '1' for yes; 'n' or '2' for no
                    if event.key == pygame.K_y or event.key == pygame.K_1:
                        scale_food = True
                        break
                    if event.key == pygame.K_n or event.key == pygame.K_2:
                        scale_food = False
                        break
            clock.tick(30)

    if scale_food is False and selected not in ('Incremental Food (Basic)', 'Incremental Food (Greedy)'):
        # ask for fixed food amount (default 5)
        fixed_food_amount = prompt_fixed_amount(initial=5)

    # ask whether verbose logging should be enabled (default off)
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

    def draw_mutation_toggle_menu(initial_speed: bool = True, initial_size: bool = True, initial_intelligence: bool = True) -> dict:
        """Interactive menu to toggle mutation types on/off for MutationSimulation.

        Returns a dict like {'speed': bool, 'size': bool, 'intelligence': bool}.
        """
        speed_on = bool(initial_speed)
        size_on = bool(initial_size)
        intelligence_on = bool(initial_intelligence)
        while True:
            screen.fill(BACKGROUND_COLOR)
            width, height = screen.get_size()
            pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, width, height), width=2)
            title_size = max(14, int(height * 0.05))
            option_size = max(12, int(height * 0.04))
            hint_size = max(10, int(height * 0.03))
            title_font = pygame.font.Font(pygame.font.get_default_font(), title_size)
            option_font = pygame.font.Font(pygame.font.get_default_font(), option_size)
            hint_font = pygame.font.Font(pygame.font.get_default_font(), hint_size)

            title = title_font.render('Mutation toggles', True, (240, 240, 245))
            speed_label = f"Speed mutation: {'ON' if speed_on else 'OFF'} (±{int(MUTATION_SPEED_DELTA * 100)}%)"
            size_label = f"Size mutation: {'ON' if size_on else 'OFF'} (±{int(MUTATION_SIZE_DELTA * 100)}%)"
            intelligence_label = f"Intelligence mutation: {'ON' if intelligence_on else 'OFF'} (±{int(MUTATION_INTELLIGENCE_DELTA * 100)}%)"
            opt_speed = option_font.render('S) ' + speed_label, True, (220, 220, 230))
            opt_size = option_font.render('Z) ' + size_label, True, (220, 220, 230))
            opt_intelligence = option_font.render('I) ' + intelligence_label, True, (220, 220, 230))
            hint = hint_font.render('Press S/Z/I to toggle | Enter to continue | Esc to cancel', True, (160, 160, 170))

            screen.blit(title, (width // 2 - title.get_width() // 2, int(height * 0.3)))
            screen.blit(opt_speed, (width // 2 - opt_speed.get_width() // 2, int(height * 0.4)))
            screen.blit(opt_size, (width // 2 - opt_size.get_width() // 2, int(height * 0.47)))
            screen.blit(opt_intelligence, (width // 2 - opt_intelligence.get_width() // 2, int(height * 0.54)))
            screen.blit(hint, (width // 2 - hint.get_width() // 2, int(height * 0.63)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return {'speed': speed_on, 'size': size_on, 'intelligence': intelligence_on}
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return {'speed': speed_on, 'size': size_on, 'intelligence': intelligence_on}
                    if event.key == pygame.K_s:
                        speed_on = not speed_on
                    if event.key == pygame.K_z:
                        size_on = not size_on
                    if event.key == pygame.K_i:
                        intelligence_on = not intelligence_on
            clock.tick(30)

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

    # If mutation simulation is selected, allow toggling individual mutations
    mutation_settings = {'speed': True, 'size': True, 'intelligence': True}
    if selected == 'MutationSimulation':
        mutation_settings = draw_mutation_toggle_menu()

    pygame.display.set_caption(f'Ecosystem Simulator – {selected}')
    simulation_id = 1
    current_speed_steps = 1
    while True:
        # for incremental-food sims we will run a sequence of simulations (50 runs)
        if selected in ('Incremental Food (Basic)', 'Incremental Food (Greedy)'):
            # starting food is fixed_food_amount
            start_food = fixed_food_amount if isinstance(fixed_food_amount, int) else 5
            runs = DATA_SIM_RUNS
            # determine CSV path base name
            if selected == 'Incremental Food (Basic)':
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
            # infinite sequence of runs; each run lasts exactly 50 days. User may terminate the program when done.
            while True:
                sim = sim_factory(WORLD_WIDTH, WORLD_HEIGHT)
                # force non-scaling and fixed food
                setattr(sim, 'food_scaling', False)
                setattr(sim, 'fixed_food_count', int(current_food))
                setattr(sim, 'verbose', bool(verbose_choice))
                sim.speed_steps = max(1, current_speed_steps)
                pygame.display.set_caption(f'Ecosystem Simulator – {selected} (run {run_idx}/{runs} food={current_food})')

                # each run lasts exactly 50 days. We still allow early extinction but continue counting days.
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

                    # allow user to manually stop an individual day/run via sim.manual_stop (handled by simulate_day)
                    if getattr(sim, 'manual_stop', False):
                        break

                # at end of 50-day run (or earlier if manual_stop), show final frame until dismissed
                def draw_incremental_food_results() -> None:
                    screen.fill(BACKGROUND_COLOR)
                    pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, sim.width, sim.height), width=2)
                    for creature in sim.creatures:
                        creature.draw(screen)
                    for food in sim.foods:
                        food.draw(screen)
                    render_population_graph(screen, day_rows)

                write_recent_csv(simulation_id, day_rows)
                wait_for_results_dismiss(draw_incremental_food_results)

                # after the run, compute average population (average start_creatures per day)
                if day_rows:
                    avg_pop = sum(r[1] for r in day_rows) / len(day_rows)
                else:
                    avg_pop = 0
                # append to avg CSV
                with open(avg_csv_path, 'a', newline='') as f:
                    w = csv.writer(f)
                    w.writerow([int(current_food), float(avg_pop)])

                # increment food for next run and loop (user will terminate when they've seen enough)
                current_food += 1
                simulation_id += 1
                run_idx += 1

            # (never reached) continue
        # energy-based incremental sims: vary creature max energy per run and record average population
        if selected in ('Incremental Energy (Basic)', 'Incremental Energy (Greedy)'):
            start_energy = DATA_SIM_ENERGY_START
            energy_increment = DATA_SIM_ENERGY_INCREMENT
            runs = DATA_SIM_RUNS
            if selected == 'Incremental Energy (Basic)':
                avg_csv_name = 'basic_average_population_vs_energy.csv'
                sim_factory = BasicSimulation
            else:
                avg_csv_name = 'greedy_average_population_vs_energy.csv'
                sim_factory = GreedySimulation

            log_dir = os.path.join(os.getcwd(), 'log')
            os.makedirs(log_dir, exist_ok=True)
            avg_csv_path = os.path.join(log_dir, avg_csv_name)
            if not os.path.exists(avg_csv_path):
                with open(avg_csv_path, 'w', newline='') as f:
                    w = csv.writer(f)
                    w.writerow(['energy', 'average_population'])

            current_energy = start_energy
            run_idx = 1
            while True:
                sim = sim_factory(WORLD_WIDTH, WORLD_HEIGHT)
                # force fixed food behavior (user provided fixed_food_amount)
                setattr(sim, 'food_scaling', False)
                setattr(sim, 'fixed_food_count', int(fixed_food_amount) if isinstance(fixed_food_amount, int) else 0)
                setattr(sim, 'verbose', bool(verbose_choice))
                sim.speed_steps = max(1, current_speed_steps)

                # Override creature max energy provider for this instance
                sim.get_creature_max_energy = (lambda e=current_energy: int(e))
                # Also set each starting creature's current energy
                for c in sim.creatures:
                    c.energy = int(current_energy)

                pygame.display.set_caption(f'Ecosystem Simulator – {selected} (run {run_idx}/{runs} energy={current_energy})')

                # Run exactly 50 days per run
                day_rows = []
                for day in range(1, 50 + 1):
                    sim.day = day

                    start_creatures, food_spawned, survivors, died = sim.simulate_day(screen, clock)
                    current_speed_steps = sim.speed_steps
                    sim.log_day(simulation_id, day, start_creatures, food_spawned, survivors, died)
                    end_creatures = survivors
                    day_rows.append((day, start_creatures, food_spawned, survivors, died, end_creatures))

                    sim.reproduce_survivors()

                    if getattr(sim, 'manual_stop', False):
                        break

                def draw_incremental_energy_results() -> None:
                    screen.fill(BACKGROUND_COLOR)
                    pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, sim.width, sim.height), width=2)
                    for creature in sim.creatures:
                        creature.draw(screen)
                    for food in sim.foods:
                        food.draw(screen)
                    render_population_graph(screen, day_rows)

                write_recent_csv(simulation_id, day_rows)
                wait_for_results_dismiss(draw_incremental_energy_results)

                # compute average population for the run
                if day_rows:
                    avg_pop = sum(r[1] for r in day_rows) / len(day_rows)
                else:
                    avg_pop = 0
                with open(avg_csv_path, 'a', newline='') as f:
                    w = csv.writer(f)
                    w.writerow([int(current_energy), float(avg_pop)])

                current_energy += energy_increment
                simulation_id += 1
                run_idx += 1

            # (never reached)
        # prepare per-simulation auxiliary storage
        speed_rows = []
        size_rows = []
        intelligence_rows = []

        if selected == 'BasicSimulation':
            sim = BasicSimulation(WORLD_WIDTH, WORLD_HEIGHT)
        elif selected == 'GreedySimulation':
            sim = GreedySimulation(WORLD_WIDTH, WORLD_HEIGHT)
        elif selected == 'MutationSimulation':
            sim = MutationSimulation(
                WORLD_WIDTH,
                WORLD_HEIGHT,
                mutation_speed_enabled=mutation_settings.get('speed', True),
                mutation_size_enabled=mutation_settings.get('size', True),
                mutation_intelligence_enabled=mutation_settings.get('intelligence', True),
            )
            # prepare storage for average-trait-per-day measurements
            speed_rows = []
            size_rows = []
            intelligence_rows = []
        else:
            sim = BasicSimulation(WORLD_WIDTH, WORLD_HEIGHT)

        # apply food-scaling options selected in the menu
        # default: scaling enabled
        setattr(sim, 'food_scaling', True if scale_food is None else bool(scale_food))
        setattr(sim, 'fixed_food_count', fixed_food_amount if fixed_food_amount is not None else None)
        # apply verbose option
        setattr(sim, 'verbose', bool(verbose_choice))

        sim.speed_steps = max(1, current_speed_steps)
        pygame.display.set_caption(f'Ecosystem Simulator – {selected} (x{sim.speed_steps})')

        day = 0
        # collect per-day stats for graphing and recent CSV. Keep all days; graph will show full dataset.
        day_rows = []  # list of (day, start, food, survivors, died, end)
        while True:
            if len(sim.creatures) == 0:
                break
            day += 1
            sim.day = day
            # For mutation simulation, measure average traits at start of day
            if selected == 'MutationSimulation':
                try:
                    avg_speed = 0.0
                    avg_size = 0.0
                    avg_intelligence = 0.0
                    if sim.creatures:
                        avg_speed = sum(float(getattr(c, 'traits', {}).get('speed', 1.0)) for c in sim.creatures) / len(sim.creatures)
                        avg_size = sum(float(getattr(c, 'traits', {}).get('size', 1.0)) for c in sim.creatures) / len(sim.creatures)
                        avg_intelligence = sum(float(getattr(c, 'traits', {}).get('intelligence', 1.0)) for c in sim.creatures) / len(sim.creatures)
                    else:
                        avg_speed = 0.0
                        avg_size = 0.0
                        avg_intelligence = 0.0
                except Exception:
                    avg_speed = 0.0
                    avg_size = 0.0
                    avg_intelligence = 0.0
                speed_rows.append((day, avg_speed))
                size_rows.append((day, avg_size))
                intelligence_rows.append((day, avg_intelligence))

            start_creatures, food_spawned, survivors, died = sim.simulate_day(screen, clock)
            current_speed_steps = sim.speed_steps
            sim.log_day(simulation_id, day, start_creatures, food_spawned, survivors, died)
            end_creatures = survivors
            # Always record day rows (we'll show the most recent N in the graph)
            day_rows.append((day, start_creatures, food_spawned, survivors, died, end_creatures))

            # Stop conditions: extinction or manual stop
            if survivors == 0 or getattr(sim, 'manual_stop', False):
                mpath = None
                if selected == 'MutationSimulation':
                    # write combined CSV for mutation simulation
                    log_dir = os.path.join(os.getcwd(), 'log')
                    os.makedirs(log_dir, exist_ok=True)
                    speed_rows_to_write = speed_rows
                    size_rows_to_write = size_rows
                    intelligence_rows_to_write = intelligence_rows

                    # determine which columns to include based on enabled mutations
                    speed_enabled = mutation_settings.get('speed', True)
                    size_enabled = mutation_settings.get('size', True)
                    intelligence_enabled = mutation_settings.get('intelligence', True)

                    mpath = os.path.join(log_dir, 'mutation_simulation_traits.csv')
                    with open(mpath, 'w', newline='') as f:
                        w = csv.writer(f)
                        # build header dynamically
                        header = ['day']
                        if speed_enabled:
                            header.append('average_speed')
                        if size_enabled:
                            header.append('average_size')
                        if intelligence_enabled:
                            header.append('average_intelligence')
                        w.writerow(header)

                        # write data rows
                        max_days = max(len(speed_rows_to_write), len(size_rows_to_write), len(intelligence_rows_to_write), 0)
                        for idx in range(max_days):
                            row: list = [idx + 1]  # day starts at 1
                            if speed_enabled and idx < len(speed_rows_to_write):
                                row.append(speed_rows_to_write[idx][1])
                            if size_enabled and idx < len(size_rows_to_write):
                                row.append(size_rows_to_write[idx][1])
                            if intelligence_enabled and idx < len(intelligence_rows_to_write):
                                row.append(intelligence_rows_to_write[idx][1])
                            w.writerow(row)

                def draw_final_results() -> None:
                    screen.fill(BACKGROUND_COLOR)
                    pygame.draw.rect(screen, EDGE_COLOR, pygame.Rect(0, 0, sim.width, sim.height), width=2)
                    for creature in sim.creatures:
                        creature.draw(screen)
                    for food in sim.foods:
                        food.draw(screen)
                    if selected == 'MutationSimulation' and mpath is not None:
                        render_mutation_traits_graphs(screen, mpath)
                    else:
                        # Render only the most recent 20 days for clarity
                        render_population_graph(screen, day_rows[-20:])

                # Write/update recent CSV (last 10 simulations x up to 20 days)
                write_recent_csv(simulation_id, day_rows)
                wait_for_results_dismiss(draw_final_results)
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

    # load existing rows
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
    # append this simulation's rows (cap to 20 already ensured by caller)
    for (day, start_c, food, surv, died, end_c) in day_rows:
        existing.append((simulation_id, day, start_c, food, surv, died, end_c))

    # keep only last 10 simulation ids
    sim_ids = sorted({sid for (sid, *_rest) in existing}, reverse=True)
    keep_ids = set(sim_ids[:10])
    filtered = [r for r in existing if r[0] in keep_ids]
    # sort by sim_id then day
    filtered.sort(key=lambda r: (r[0], r[1]))

    # write back
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
    width = screen.get_width()
    height = screen.get_height()
    # calculate margins to make graph 75% of original size but centered
    original_margin = 40
    original_graph_width = width - 2 * original_margin
    original_graph_height = height - 2 * original_margin
    new_graph_width = int(0.75 * original_graph_width)
    new_graph_height = int(0.75 * original_graph_height)
    margin_x = (width - new_graph_width) // 2
    margin_y = (height - new_graph_height) // 2
    graph_rect = pygame.Rect(margin_x, margin_y, new_graph_width, new_graph_height)
    # axes
    axis_color = (180, 180, 190)
    pygame.draw.rect(screen, EDGE_COLOR, graph_rect, width=1)

    if not day_rows:
        return
    days = [row[0] for row in day_rows]
    pops = [row[1] for row in day_rows]  # start_creatures per day
    min_day = min(days)
    max_day = max(days)
    max_pop = max(max(pops), 1)
    # add 5% headroom above max for easier viewing
    display_max_pop = max_pop * SIM_GRAPH_Y_MARGIN
    # scale and draw line
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
    # draw axes ticks/labels (minimal)
    font = pygame.font.SysFont(None, 18)
    label = font.render('Population vs Day (start of day)', True, (200, 200, 210))
    screen.blit(label, (graph_rect.left, graph_rect.top - 22))
    # day labels min and max
    d_min_label = font.render(str(min_day), True, (160, 160, 170))
    d_max_label = font.render(str(max_day), True, (160, 160, 170))
    screen.blit(d_min_label, (graph_rect.left - 5, graph_rect.bottom + 4))
    screen.blit(d_max_label, (graph_rect.right - d_max_label.get_width(), graph_rect.bottom + 4))
    # x-axis labels: 0 at bottom and max_pop at top; show intermediate ticks
    y0 = font.render('0', True, (160, 160, 170))
    y_mid_val = int(max_pop / 2)
    y_mid = font.render(str(y_mid_val), True, (160, 160, 170))
    mp = font.render(str(max_pop), True, (160, 160, 170))
    screen.blit(y0, (graph_rect.left - 18, graph_rect.bottom - 8))
    screen.blit(y_mid, (graph_rect.left - 28, int(graph_rect.top + graph_rect.height / 2) - 8))
    screen.blit(mp, (graph_rect.left - 30, graph_rect.top - 8))
    # Draw Y ticks (exclude endpoints — labels already present at top/bottom)
    pygame.draw.line(screen, axis_color, (graph_rect.left - 6, int(graph_rect.top + graph_rect.height / 2)), (graph_rect.left, int(graph_rect.top + graph_rect.height / 2)), 1)

    # intermediate x ticks (up to 5 ticks)
    tick_count = min(5, max(2, max_day - min_day + 1))
    for i in range(tick_count):
        tx = graph_rect.left + i / max(1, tick_count - 1) * graph_rect.width
        # Don't draw tick marks at the endpoints — keep labels only
        if i not in (0, tick_count - 1):
            pygame.draw.line(screen, axis_color, (int(tx), graph_rect.bottom), (int(tx), graph_rect.bottom + 6), 1)
        # Label every tick (including endpoints)
        label_day = int(min_day + i / max(1, tick_count - 1) * (max_day - min_day))
        lbl = font.render(str(label_day), True, (160, 160, 170))
        screen.blit(lbl, (int(tx) - lbl.get_width() // 2, graph_rect.bottom + 6))


def render_speed_graph(screen: pygame.Surface, day_rows: list, label_text: str = 'Average Speed vs Day (start of day)', metric_name: str = 'speed') -> None:
    """Render a graph of an averaged trait vs day.

    Expects day_rows as list of tuples where the second element is the average value (float).
    label_text controls the title; metric_name controls the overall-average label.
    """
    width = screen.get_width()
    height = screen.get_height()
    original_margin = 40
    original_graph_width = width - 2 * original_margin
    original_graph_height = height - 2 * original_margin
    new_graph_width = int(0.75 * original_graph_width)
    new_graph_height = int(0.75 * original_graph_height)
    margin_x = (width - new_graph_width) // 2
    margin_y = (height - new_graph_height) // 2
    graph_rect = pygame.Rect(margin_x, margin_y, new_graph_width, new_graph_height)

    pygame.draw.rect(screen, EDGE_COLOR, graph_rect, width=1)
    if not day_rows:
        return
    days = [row[0] for row in day_rows]
    speeds = [row[1] for row in day_rows]
    min_day = min(days)
    max_day = max(days)
    max_speed = max(max(speeds), 1.0)
    display_max_speed = max_speed * SIM_GRAPH_Y_MARGIN

    # Build pixel positions for raw data points
    points = []
    n = len(speeds)
    for (d, s) in zip(days, speeds):
        if max_day == min_day:
            x = graph_rect.left + graph_rect.width / 2
        else:
            x = graph_rect.left + (d - min_day) / max(1, (max_day - min_day)) * graph_rect.width
        y = graph_rect.bottom - (s / display_max_speed) * graph_rect.height
        points.append((int(x), int(y)))

    # Adaptive smoothing window: larger for longer series to reduce volatility
    # window is at least 3, grows to ~n/10, capped at 51
    window = max(3, min(51, max(3, n // 10)))
    if n < window:
        window = max(1, n)
    half = window // 2

    # Centered moving average smoothing
    smoothed = []
    for i in range(n):
        start = max(0, i - half)
        end = min(n, i + half + 1)
        avg = sum(speeds[start:end]) / float(end - start)
        smoothed.append(avg)

    # To create a clean (but now sparser) trend curve, aggregate the smoothed series
    # into a modest number of segments and draw lines between segment means.
    # Reducing max_segments reduces visual clutter and makes the trend easier to read.
    max_segments = 20  # was 60, reduce to draw fewer piecewise segments
    segments = min(max_segments, max(1, n))
    seg_size = max(1, n // segments)
    agg_days = []
    agg_vals = []
    i = 0
    while i < n:
        chunk = range(i, min(n, i + seg_size))
        chunk_days = [days[j] for j in chunk]
        chunk_vals = [smoothed[j] for j in chunk]
        if chunk_days:
            agg_days.append(sum(chunk_days) / len(chunk_days))
            agg_vals.append(sum(chunk_vals) / len(chunk_vals))
        i += seg_size

    # Build pixel positions for aggregated trend points
    agg_points = []
    for (d, s) in zip(agg_days, agg_vals):
        if max_day == min_day:
            x = graph_rect.left + graph_rect.width / 2
        else:
            x = graph_rect.left + (d - min_day) / max(1, (max_day - min_day)) * graph_rect.width
        y = graph_rect.bottom - (s / display_max_speed) * graph_rect.height
        agg_points.append((int(x), int(y)))

    # Draw raw points faintly (small grey dots) so trend stands out
    raw_color = (180, 180, 190)
    for p in points:
        pygame.draw.circle(screen, raw_color, p, 2)

    # Draw aggregated piecewise trend: many short line segments (thin, darker)
    # Use blue for the piecewise segments so it contrasts with the smoothed curve.
    agg_color = (60, 120, 200)  # blue
    if len(agg_points) >= 2:
        pygame.draw.lines(screen, agg_color, False, agg_points, 2)
    elif len(agg_points) == 1:
        pygame.draw.circle(screen, agg_color, agg_points[0], 3)

    # Also draw a heavier smoothed line through a down-sampled set of smoothed points
    # to avoid drawing one line per day (which looks noisy for long runs).
    smooth_sample_max = 40
    sample_step = max(1, n // smooth_sample_max)
    sampled_days = days[::sample_step]
    sampled_smoothed = smoothed[::sample_step]
    # Ensure the final datapoint is included so the curve reaches the run end
    if sampled_days and sampled_days[-1] != days[-1]:
        sampled_days.append(days[-1])
        sampled_smoothed.append(smoothed[-1])

    smooth_points = []
    for (d, s) in zip(sampled_days, sampled_smoothed):
        if max_day == min_day:
            x = graph_rect.left + graph_rect.width / 2
        else:
            x = graph_rect.left + (d - min_day) / max(1, (max_day - min_day)) * graph_rect.width
        y = graph_rect.bottom - (s / display_max_speed) * graph_rect.height
        smooth_points.append((int(x), int(y)))
    # Draw the down-sampled smoothed curve in red so it stands out as the primary trend.
    smooth_color = (200, 60, 60)  # red
    if len(smooth_points) >= 2:
        pygame.draw.lines(screen, smooth_color, False, smooth_points, 3)
    elif len(smooth_points) == 1:
        pygame.draw.circle(screen, smooth_color, smooth_points[0], 4)

    font = pygame.font.SysFont(None, 18)
    label = font.render(label_text, True, (200, 200, 210))
    screen.blit(label, (graph_rect.left, graph_rect.top - 22))

    # day labels
    d_min_label = font.render(str(min_day), True, (160, 160, 170))
    d_max_label = font.render(str(max_day), True, (160, 160, 170))
    screen.blit(d_min_label, (graph_rect.left - 5, graph_rect.bottom + 4))
    screen.blit(d_max_label, (graph_rect.right - d_max_label.get_width(), graph_rect.bottom + 4))

    def format_metric_value(value: float) -> str:
        if value >= 10:
            return str(int(round(value)))
        if value >= 1:
            return f'{value:.1f}'
        return f'{value:.2f}'

    # y labels: 0, mid, max
    y0 = font.render('0', True, (160, 160, 170))
    y_mid_val = max_speed / 2
    y_mid = font.render(format_metric_value(y_mid_val), True, (160, 160, 170))
    y_max = font.render(format_metric_value(max_speed), True, (160, 160, 170))
    screen.blit(y0, (graph_rect.left - 18, graph_rect.bottom - 8))
    screen.blit(y_mid, (graph_rect.left - 28, int(graph_rect.top + graph_rect.height / 2) - 8))
    screen.blit(y_max, (graph_rect.left - 30, graph_rect.top - 8))

    axis_color = (180, 180, 190)
    # draw middle tick only for Y
    pygame.draw.line(screen, axis_color, (graph_rect.left - 6, int(graph_rect.top + graph_rect.height / 2)), (graph_rect.left, int(graph_rect.top + graph_rect.height / 2)), 1)
    # draw X ticks
    tick_count = min(5, max(2, max_day - min_day + 1))
    for i in range(tick_count):
        tx = graph_rect.left + i / max(1, tick_count - 1) * graph_rect.width
        if i not in (0, tick_count - 1):
            pygame.draw.line(screen, axis_color, (int(tx), graph_rect.bottom), (int(tx), graph_rect.bottom + 6), 1)
        label_day = int(min_day + i / max(1, tick_count - 1) * (max_day - min_day))
        lbl = font.render(str(label_day), True, (160, 160, 170))
        screen.blit(lbl, (int(tx) - lbl.get_width() // 2, graph_rect.bottom + 6))

    # compute overall average speed across the whole series and display it outside the graph
    # Compute overall average using only the last 90% of recorded values to allow stabilization
    overall_avg = 0.0
    try:
        if speeds:
            n = len(speeds)
            start_idx = int(n * 0.1)
            tail = speeds[start_idx:]
            if not tail:
                tail = speeds
            overall_avg = sum(tail) / float(len(tail))
    except Exception:
        overall_avg = 0.0
    avg_text = font.render(f'Overall avg {metric_name}: {overall_avg:.2f}', True, (220, 220, 210))
    # place at top-right corner but keep within window bounds
    tx = min(graph_rect.right + 8, screen.get_width() - avg_text.get_width() - 8)
    ty = max(8, graph_rect.top - 20)
    screen.blit(avg_text, (tx, ty))


def render_mutation_traits_graphs(screen: pygame.Surface, csv_path: str) -> None:
    """Render one or more mutation-trait graphs based on CSV columns.

    CSV format: day, [average_speed], [average_size], [average_intelligence]
    where each trait column is optional depending on the enabled mutations.
    """
    if not os.path.exists(csv_path):
        width, height = screen.get_size()
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(None, 20)
        msg = font.render('CSV not found: ' + os.path.basename(csv_path), True, (200, 200, 210))
        screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 10))
        return

    # Read CSV and detect columns
    days = []
    speed_data = []
    size_data = []
    intelligence_data = []
    has_speed = False
    has_size = False
    has_intelligence = False
    
    with open(csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header:
            has_speed = 'average_speed' in header
            has_size = 'average_size' in header
            has_intelligence = 'average_intelligence' in header
            speed_col = header.index('average_speed') if has_speed else -1
            size_col = header.index('average_size') if has_size else -1
            intelligence_col = header.index('average_intelligence') if has_intelligence else -1
            
            for r in reader:
                try:
                    day = int(r[0])
                    days.append(day)
                    if has_speed and speed_col < len(r):
                        speed_data.append(float(r[speed_col]))
                    if has_size and size_col < len(r):
                        size_data.append(float(r[size_col]))
                    if has_intelligence and intelligence_col < len(r):
                        intelligence_data.append(float(r[intelligence_col]))
                except Exception:
                    continue
    
    if not days:
        return
    
    # Normalize days to start from 1
    if days:
        min_day = min(days)
        days = [d - min_day + 1 for d in days]
    
    # Build day_rows structures for each trait
    speed_rows = [(d, s) for d, s in zip(days, speed_data)] if has_speed else []
    size_rows = [(d, s) for d, s in zip(days, size_data)] if has_size else []
    intelligence_rows = [(d, s) for d, s in zip(days, intelligence_data)] if has_intelligence else []
    
    graph_specs = []
    if has_speed:
        graph_specs.append((speed_rows, 'Average Speed vs Day (start of day)', 'speed'))
    if has_size:
        graph_specs.append((size_rows, 'Average Size vs Day (start of day)', 'size'))
    if has_intelligence:
        graph_specs.append((intelligence_rows, 'Average Intelligence vs Day (start of day)', 'intelligence'))

    if not graph_specs:
        return
    if len(graph_specs) == 1:
        rows, label_text, metric_name = graph_specs[0]
        render_speed_graph(screen, rows, label_text=label_text, metric_name=metric_name)
        return

    width = screen.get_width()
    height = screen.get_height()
    section_height = height // len(graph_specs)
    for idx, (rows, label_text, metric_name) in enumerate(graph_specs):
        top = idx * section_height
        current_height = section_height if idx < len(graph_specs) - 1 else height - top
        section_surface = pygame.Surface((width, current_height))
        section_surface.fill(BACKGROUND_COLOR)
        render_speed_graph(section_surface, rows, label_text=label_text, metric_name=metric_name)
        screen.blit(section_surface, (0, top))


def render_csv_graph(screen: pygame.Surface, csv_path: str) -> None:
    # read csv of two columns
    if not os.path.exists(csv_path):
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

    # build day_rows-like structure where x is food (treated as day index) and y as population
    day_rows = [(int(x), int(y), 0, 0, 0, 0) for x, y in zip(xs, ys)]

    # we will map food values to sequential positions and use y as population.
    width = screen.get_width()
    height = screen.get_height()
    # prep rect same as render_population_graph
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
    # choose title based on file name (energy CSVs should be labeled 'Energy')
    base_name = os.path.basename(csv_path).lower()
    if 'energy' in base_name:
        title_text = 'Average Population vs Energy'
    else:
        title_text = 'Average Population vs Food'
    label = font.render(title_text, True, (200, 200, 210))
    screen.blit(label, (graph_rect.left, graph_rect.top - 22))

    max_y = max(ys)
    # avoid division by zero if max_y is 0
    display_max_y = max(max_y, 1.0) * 1.05

    # build pixel positions for each data point
    points_info = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        px = graph_rect.left + (i / max(1, len(xs) - 1)) * graph_rect.width
        py = graph_rect.bottom - (y / display_max_y) * graph_rect.height
        points_info.append({'i': i, 'x': x, 'y': y, 'px': int(px), 'py': int(py)})

    # If this is an energy CSV, treat very-low values as outliers: don't connect them into the main line
    base_name = os.path.basename(csv_path).lower()
    is_energy_csv = 'energy' in base_name
    outlier_threshold = None
    if is_energy_csv:
        # threshold: 10% of max_y or at least 1
        outlier_threshold = max(1.0, max_y * 0.10)

    # Create connected segments of non-outlier points for the trend line
    segments = []
    current_seg = []
    outlier_points = []
    for p in points_info:
        yval = p['y']
        if is_energy_csv and yval < outlier_threshold:
            outlier_points.append(p)
            # break any current segment
            if current_seg:
                segments.append(current_seg)
                current_seg = []
        else:
            current_seg.append((p['px'], p['py']))
    if current_seg:
        segments.append(current_seg)

    # draw trend line segments
    line_color = (120, 180, 220)
    for seg in segments:
        if len(seg) >= 2:
            pygame.draw.lines(screen, line_color, False, seg, 2)
        elif len(seg) == 1:
            pygame.draw.circle(screen, line_color, seg[0], 3)

    # draw outlier markers (as red small circles) so they are visible but don't dominate the trend
    if outlier_points:
        for p in outlier_points:
            pygame.draw.circle(screen, (220, 80, 80), (p['px'], p['py']), 3)

    # labels and ticks
    axis_color = (180, 180, 190)
    if xs:
        left_label = font.render(str(int(xs[0])), True, (160, 160, 170))
        right_label = font.render(str(int(xs[-1])), True, (160, 160, 170))
        screen.blit(left_label, (graph_rect.left - 10, graph_rect.bottom + 4))
        screen.blit(right_label, (graph_rect.right - right_label.get_width(), graph_rect.bottom + 4))
        # y ticks and labels: 0, mid, max
        y0 = font.render('0', True, (160, 160, 170))
        y_mid_val = int(max_y / 2)
        y_mid = font.render(str(y_mid_val), True, (160, 160, 170))
        y_max = font.render(str(int(max_y)), True, (160, 160, 170))
        screen.blit(y0, (graph_rect.left - 18, graph_rect.bottom - 8))
        screen.blit(y_mid, (graph_rect.left - 28, int(graph_rect.top + graph_rect.height / 2) - 8))
        screen.blit(y_max, (graph_rect.left - 30, graph_rect.top - 8))
        # draw Y tick marks (exclude endpoints — labels already present at top/bottom)
        pygame.draw.line(screen, axis_color, (graph_rect.left - 6, int(graph_rect.top + graph_rect.height / 2)), (graph_rect.left, int(graph_rect.top + graph_rect.height / 2)), 1)
        # draw X ticks (up to 7 ticks depending on food count)
        tick_count = min(7, max(2, len(xs)))
        for i in range(tick_count):
            tx = graph_rect.left + i / max(1, tick_count - 1) * graph_rect.width
            # Don't draw tick marks at the endpoints — keep labels only
            if i not in (0, tick_count - 1):
                pygame.draw.line(screen, axis_color, (int(tx), graph_rect.bottom), (int(tx), graph_rect.bottom + 6), 1)
            idx = int(i / max(1, tick_count - 1) * (len(xs) - 1))
            label_food = xs[idx]
            lbl = font.render(str(int(label_food)), True, (160, 160, 170))
            screen.blit(lbl, (int(tx) - lbl.get_width() // 2, graph_rect.bottom + 6))


def draw_preliminary_menu() -> str:
    # returns 'run' or 'view'
    raise NotImplementedError("draw_preliminary_menu must be called with screen and clock")

def view_graphs_flow() -> None:
    raise NotImplementedError("view_graphs_flow must be called with screen and clock")

if __name__ == '__main__':
    run_simulation()