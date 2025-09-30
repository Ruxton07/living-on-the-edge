# Simple 2D Ecosystem

## Overview

This is a simulation of creatures and food on a 2D plane using pygame.

### Each of the following depend on the simulation type:
- **World**: X by Y with border as "edge"
- **Creatures**: blue circles, move around, limited energy
- **Food**: green circles, spawn each day
- **Rules**: If a creature eats, energy resets and it must return to the edge to survive. Day ends when all creatures are dead or survivors.
- **Reproduction**: Survivors may split into two new creatures placed on the edge at the start of next day.
- **Logs**: CSV at `./log/day_stats.csv` and `./log/recent_stats.csv` with some run stats

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Press the window close button to exit early.