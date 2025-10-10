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

# Greedy simulation parameters
GREEDY_CONSTANT = 1.1      # multiplier for food spawning in greedy simulation
GREEDY_UNCERTAINTY = 0.3  # fraction of food to spawn with some randomness

START_CREATURES = {'basic_simulation': 2, 'greedy_simulation': 3}