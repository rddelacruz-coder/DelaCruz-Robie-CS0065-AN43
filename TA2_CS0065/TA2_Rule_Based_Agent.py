"""Rule-based vacuum agent for the two-room environment (Rooms A and B)."""


def get_room_state(room_name):
    """Ask for a room's starting condition and accept Dirty or Clean."""
    while True:
        answer = input(f"Initial state of Room {room_name} (dirty/clean): ").strip().lower()
        if answer in ("dirty", "clean"):
            return answer
        print("Please enter 'dirty' or 'clean'.")


def is_dirty(environment, room):
    """Return True when the specified room is dirty."""
    return environment[room] == "dirty"


def clean_room(environment, room):
    """Change a room's state to clean."""
    environment[room] = "clean"


class VacuumAgent:
    """A rule-based agent that cleans its current room or moves to the other."""

    def __init__(self, starting_room="A"):
        self.location = starting_room

    def move(self):
        """Switch between Room A and Room B."""
        self.location = "B" if self.location == "A" else "A"

    def perceive_and_act(self, environment):
        """Apply the rules and return a description of the action taken."""
        if is_dirty(environment, self.location):
            clean_room(environment, self.location)
            return f"Cleaned Room {self.location}"

        old_location = self.location
        self.move()
        return f"Moved from Room {old_location} to Room {self.location}"


def main():
    print("=== Rule-Based Vacuum Agent ===")
    print("Set the initial condition of each room, then run the simulation.\n")

    environment = {
        "A": get_room_state("A"),
        "B": get_room_state("B"),
    }

    while True:
        try:
            steps = int(input("How many simulation steps should run? ").strip())
            if steps < 0:
                print("Please enter 0 or a positive whole number.")
                continue
            break
        except ValueError:
            print("Please enter a whole number, such as 5.")

    agent = VacuumAgent(starting_room="A")
    print("\nStarting environment:", environment)
    print(f"Agent starts in Room {agent.location}.\n")

    for step in range(1, steps + 1):
        action = agent.perceive_and_act(environment)
        print(f"Step {step}:")
        print(f"  Agent location: Room {agent.location}")
        print(f"  Action: {action}")
        print(f"  Environment: {environment}\n")

    print("Simulation complete.")
    print("Final environment:", environment)
    print(f"Final agent location: Room {agent.location}")


if __name__ == "__main__":
    main()
