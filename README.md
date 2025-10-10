# Simple 2D Ecosystem

## READ: Developer Log

This project is a personal research project of mine involving lots of data collection and analysis. To see the motivations, goals, and progress of the project, please read the developer log: [devlog.md](devlog.md).

## Overview
This is a simple 2D ecosystem simulation where creatures with random movements evolve over time to survive and thrive in their environment. The simulation includes features such as:

- Creatures that move, eat, reproduce, and die based on their energy levels.
- Food that spawns randomly in the environment.
- A graphical interface using Pygame to visualize the simulation.
- Data logging to track the population and other statistics over time.
- Configurable parameters for mutation rates, food spawning, and more.
- A menu system to control the simulation speed, toggle logging, and other settings.
- Mutation and evolution of creature traits over generations.
- so much more!

The project is built using Python and Pygame, and it is designed to be easily extendable for further experimentation and research.

## Requirements

For requirements, please see [requirements.txt](requirements.txt).

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Ruxton07/living-on-the-edge.git
   cd living-on-the-edge
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the simulation with:
```bash
python src/main.py
```

The main menu should be fairly intuitive. Use the arrow keys to navigate and Enter to select options. You can adjust simulation speed, toggle logging, and more.

## Configuration
You can adjust various parameters in [constants.py](src/constants.py) to experiment with different behaviors and outcomes. Key parameters include mutation rates, food spawn rates, and more.

## Logging and Data
The simulation logs data to CSV files in the `log` directory. You can analyze this data using tools like pandas or Excel to gain insights into the evolution of the creatures over time. However, there is also a graph viewing feature built into the simulation accessible from the main menu.

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under a modified version of Mozilla Public License Version 2.0 with additional terms. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
This project was inspired by Primer and his work on evolutionary simulations. Check out his YouTube channel for more information: [Primer](https://www.youtube.com/@PrimerBlobs).

## Contact
For questions or suggestions, please open an issue on GitHub or contact me directly at rt.kellar@gmail.com.