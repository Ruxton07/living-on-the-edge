# ---------- Config ----------
WORLD_WIDTH = 500
WORLD_HEIGHT = 500

BACKGROUND_COLOR = (20, 20, 24)
EDGE_COLOR = (90, 90, 100)
CREATURE_COLOR = (61, 178, 255)
FOOD_COLOR = (80, 200, 120)
DEAD_COLOR = (220, 60, 60)

# Radii
CREATURE_RADIUS = 15
FOOD_RADIUS = 5

TICKS_PER_SECOND = 60

# Simulation parameters
CREATURE_MAX_ENERGY = 500  # ticks
CREATURE_STEP_SIZE = 2.5   # pixels per tick
FOOD_ENERGY = 250

# Greedy simulation parameters
GREEDY_CONSTANT = 1.1      # multiplier for food spawning in greedy simulation
GREEDY_UNCERTAINTY = 0.3  # fraction of food to spawn with some randomness

# Graph display margin
SIM_GRAPH_Y_MARGIN = 1.05  # 5% headroom above max for easier viewing

# Number of simulation runs for data collection simulations
DATA_SIM_RUNS = 40
DATA_SIM_ENERGY_START = 200
DATA_SIM_ENERGY_INCREMENT = 5

# Starting number of creatures per simulation type
START_CREATURES = {'basic_simulation': 2, 'greedy_simulation': 3}