# ---------- Config ----------
WORLD_WIDTH = 500
WORLD_HEIGHT = 500

BACKGROUND_COLOR = (20, 20, 24)
EDGE_COLOR = (90, 90, 100)
CREATURE_COLOR = (61, 178, 255)
FOOD_COLOR = (80, 200, 120)
DEAD_COLOR = (220, 60, 60)

# Radii
CREATURE_RADIUS = 12
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

# Starting number of creatures per simulation type (default to 5 for all sims)
START_CREATURES = {'basic_simulation': 5, 'greedy_simulation': 5, 'mutation_simulation': 5}

# Mutation configuration
# Fractional +/- change applied to speed on replication (e.g. 0.05 = ±5%)
MUTATION_SPEED_DELTA = 0.10
# Fractional +/- change applied to size (area multiplier) on replication
# Size represents area multiplier; radius scales with sqrt(size). Energy drain scales linearly with size.
MUTATION_SIZE_DELTA = 0.10
# Fractional +/- change applied to intelligence on replication
MUTATION_INTELLIGENCE_DELTA = 0.10

# Intelligence tuning
# Higher intelligence gives a creature a better chance of steering toward nearby food.
INTELLIGENCE_BASE_RANGE = 140
INTELLIGENCE_BASE_ERROR_DEGREES = 55
INTELLIGENCE_TURN_RATE = 0.30
INTELLIGENCE_ENERGY_COST = 0.25