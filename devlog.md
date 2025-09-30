# Dev Log

## Information

I started this developer log so I could document my progress on this project over time and help myself evaluate my strengths and weaknesses. However, I also thought it could be useful to anyone who wanted to follow along this project, whether that be in real time or in the future.

## Entries

### 09/30/2025
Today I started the project. I went and rewatched the youtube video which inspired this project to begin with, to understand the rationale behind how he was choosing parameters for his simulation, but when it came to selecting my own parameters, I knew I wanted to come up with new ones rather than reusing his. This is for the sake of research and possibly locating phenomenon, which is why I took on this project to begin with.

Today's work entailed creating the main menu, as well as setting up the simulations. I started off by writing all my code in one simulation.py file, and then as I realized I wanted to expand to different simulation types, I renamed the file to basic_simulation.py and refactored as much reusable code from there into a new simulation.py file as I could. This helps a lot because it meant I wouldn't have to write giant files each time I wanted to invent a new type of simulation.

I also created graphs in between simulations to help visualize the population as a function of time (days). This was nice, but since I haven't tweaked too many inputs for my simulation I haven't noticed any unexpected phenomenon. Perhaps the more complex simulations I'm planning will ellicit something?

The csv files I set up for data collection/logging are great, but not super helpful, and they don't contain a whole lot of metrics either. I think next I will set up more data collection in the files, and create a limited history of simulations to view multiple graphs at once (widespread data analysis).

I should also list out some of the mutations I plan to add in the future since I'm already thinking about them:
* Speed Mutations - moving faster compared to other creatures
* Intelligence Mutations - having a sense of food location
    * Three ways to restrict the power of this:
        * Range - like a radar, still requiring them to get close
        * Error - like a cone, indicating a range of directions
        * Possibly a mix of the two above?
* Size Mutations - being bigger makes it easier to eat

As for fundamental simulation changes I plan to observe for the purpose of data collection:
* Greed Rewarding
    * Benefits for eating more than 2 food
    * Basically even more greedy version of greedy_simulation
    * No longer random - how does the data change?
* Pandemics
    * Caused by:
        * Eating food
            * No way to avoid
            * How the pandemic starts
        * Touching other creatures
        * Other ways?
    * May ellicit risk comparison
* Other ideas?
    * I'll likely update this list in subsequent entries as I come up with ideas

I'm excited to see what comes of this project next. I'm very eager to get into the data analysis part of this and start observing interesting behaviors.