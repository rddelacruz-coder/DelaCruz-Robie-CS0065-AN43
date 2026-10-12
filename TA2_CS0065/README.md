# Rule-Based Vacuum Agent

A small Python simulation for a two-room environment. The agent checks the room it is in and follows simple rules to clean dirty rooms or move between clean rooms. This project was created for the CS0065 Intelligent Systems Technical Assessment 2.

## What the program does

- Lets the user set the initial state of Rooms A and B as `dirty` or `clean`.
- Starts the vacuum agent in Room A.
- Runs for the number of steps entered by the user.
- Prints the agent's location, action, and the state of both rooms after each step.
- Displays the final room states and the agent's final location.
- Checks user input and asks again if a room state or step count is invalid.

## Agent rules

1. If the agent's current room is dirty, it cleans that room.
2. If the current room is clean, it moves to the other room.

The agent stays in a room for the step in which it cleans it. On its next step, it sees that the room is clean and moves. If both rooms start clean, it moves between them for all requested steps.

## Requirements

- Python 3.x
- No additional packages are required.

## Run the program

1. Download or clone this repository.
2. Open a terminal in the folder containing `TA2_Rule_Based_Agent.py`.
3. Run the script:

   **Windows**

   ```bash
   py TA2_Rule_Based_Agent.py
   ```

   If the `py` command is unavailable, try:

   ```bash
   python TA2_Rule_Based_Agent.py
   ```

   **macOS or Linux**

   ```bash
   python3 TA2_Rule_Based_Agent.py
   ```

4. Enter each room's initial state (`dirty` or `clean`), then enter a whole number of simulation steps.

## Example run

Example inputs: Room A is dirty, Room B is dirty, and the simulation runs for 5 steps.

```text
Initial state of Room A (dirty/clean): dirty
Initial state of Room B (dirty/clean): dirty
How many simulation steps should run? 5

Starting environment: {'A': 'dirty', 'B': 'dirty'}
Agent starts in Room A.

Step 1:
  Agent location: Room A
  Action: Cleaned Room A
  Environment: {'A': 'clean', 'B': 'dirty'}

Step 2:
  Agent location: Room B
  Action: Moved from Room A to Room B
  Environment: {'A': 'clean', 'B': 'dirty'}

Step 3:
  Agent location: Room B
  Action: Cleaned Room B
  Environment: {'A': 'clean', 'B': 'clean'}

Step 4:
  Agent location: Room A
  Action: Moved from Room B to Room A
  Environment: {'A': 'clean', 'B': 'clean'}

Step 5:
  Agent location: Room B
  Action: Moved from Room A to Room B
  Environment: {'A': 'clean', 'B': 'clean'}

Simulation complete.
Final environment: {'A': 'clean', 'B': 'clean'}
Final agent location: Room B
```

## Main code components

- `get_room_state()` asks for and validates the starting state of a room.
- `is_dirty()` checks whether a room is dirty.
- `clean_room()` changes a room's state to clean.
- `VacuumAgent` stores the current location and implements the move and perceive-and-act methods.
- `main()` gets the inputs, runs the simulation, and prints each step.

## Analysis

- **Rules:** Clean the current room if it is dirty; otherwise move to the other room.
- **Cleaning or moving:** The agent checks its current room's state once per step and takes the action defined by the rules.
- **Both rooms initially clean:** The agent moves between Rooms A and B until the selected step count is reached.
- **More than two rooms:** Store the rooms in an ordered list or dictionary and move to the next room after the current one, returning to the first room after the last.

## Project files

```text
.
├── README.md
└── TA2_Rule_Based_Agent.py
└── TA2_DELACRUZ.pdf
```

## Scope

This version implements the required two-room activity. The assessment's optional third-room and text-grid tasks are not included.
