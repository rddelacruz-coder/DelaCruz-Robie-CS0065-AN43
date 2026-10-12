"""TA1: Random Walk Simulation Using AgentPy.

This version records every agent's path, supports collision avoidance,
prints final positions, and compares two scenarios.
Install dependencies with: pip install agentpy matplotlib
"""

import agentpy as ap
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class RandomWalker(ap.Agent):
    """An agent that moves one square in a random cardinal direction."""

    def setup(self):
        size = self.model.p.grid_size
        self.position = (
            self.model.random.randrange(size),
            self.model.random.randrange(size),
        )
        # Task 1: Keep a history, starting with the initial location.
        self.path = [self.position]


class RandomWalkModel(ap.Model):
    """Random walkers on a bounded square grid."""

    def setup(self):
        self.agents = ap.AgentList(self, self.p.agents, RandomWalker)

    def step(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        # Track occupied squares when collision avoidance is enabled.
        occupied = {agent.position for agent in self.agents}

        # Move agents one at a time so each updated position affects the next.
        for agent in self.agents:
            x, y = agent.position
            possible = []
            for dx, dy in directions:
                new_x = x + dx
                new_y = y + dy

                # Keep every move inside the grid boundaries.
                if not (0 <= new_x < self.p.grid_size):
                    continue
                if not (0 <= new_y < self.p.grid_size):
                    continue

                # Task 2: In avoidance mode, do not move onto another agent.
                if self.p.avoid_collisions and (new_x, new_y) in occupied:
                    continue
                possible.append((new_x, new_y))

            if possible:
                new_position = self.random.choice(possible)
                occupied.discard(agent.position)
                agent.position = new_position
                occupied.add(new_position)

            # Task 1: Save the position after every step, including a wait.
            agent.path.append(agent.position)


def make_model(agents, grid_size, steps, avoid_collisions, seed=42):
    """Create and initialize a model for manual stepping or animation."""
    parameters = {
        "agents": agents,
        "grid_size": grid_size,
        "steps": steps,
        "avoid_collisions": avoid_collisions,
        "seed": seed,
    }
    model = RandomWalkModel(parameters)
    model.setup()
    return model


def print_results(model, title="Simulation results"):
    """Task 3: Print each agent's final position and recorded path."""
    print(f"\n{title}")
    for index, agent in enumerate(model.agents, start=1):
        print(f"Agent {index}: final position {agent.position}")
        print(f"  Path ({len(agent.path)} recorded positions): {agent.path}")

    unique_positions = len({agent.position for agent in model.agents})
    print(f"Unique occupied squares: {unique_positions} of {len(model.agents)} agents")


def animate_model(model):
    """Show the walkers and their paths as the model advances."""
    fig, ax = plt.subplots(figsize=(7, 7))
    grid_size = model.p.grid_size
    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(-0.5, grid_size - 0.5)
    ax.set_xticks(range(grid_size))
    ax.set_yticks(range(grid_size))
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.4)
    ax.set_title("Random Walk Simulation")

    colors = plt.cm.tab10.colors
    points = ax.scatter([], [], s=100)
    path_lines = [ax.plot([], [], color=colors[i % len(colors)], alpha=0.45)[0]
                  for i in range(len(model.agents))]
    points.set_color([colors[i % len(colors)] for i in range(len(model.agents))])

    def update(_frame):
        model.step()
        xs = [agent.position[0] for agent in model.agents]
        ys = [agent.position[1] for agent in model.agents]
        points.set_offsets(list(zip(xs, ys)))
        for line, agent in zip(path_lines, model.agents):
            line.set_data([p[0] for p in agent.path], [p[1] for p in agent.path])
        ax.set_xlabel(f"Step {len(model.agents[0].path) - 1}")
        return [points, *path_lines]

    # The initial positions are shown before the first movement.
    points.set_offsets([agent.position for agent in model.agents])
    for line, agent in zip(path_lines, model.agents):
        line.set_data([agent.position[0]], [agent.position[1]])

    animation = FuncAnimation(
        fig, update, frames=model.p.steps, interval=350,
        blit=False, repeat=False, cache_frame_data=False,
    )
    plt.show()
    return animation  # Keep a reference alive until the window closes.


def compare_scenarios():
    """Task 4: Compare a light-load and a crowded, longer simulation."""
    scenarios = [
        ("Scenario A: 5 agents, 10x10 grid, 20 steps", 5, 10, 20),
        ("Scenario B: 12 agents, 5x5 grid, 50 steps", 12, 5, 50),
    ]
    print("\nScenario comparison (collision avoidance enabled)")
    for name, agents, grid_size, steps in scenarios:
        model = make_model(agents, grid_size, steps, True, seed=42)
        for _ in range(steps):
            model.step()
        unique = len({agent.position for agent in model.agents})
        print(
            f"{name}: {unique}/{agents} distinct final squares; "
            f"{agents} paths recorded with {steps + 1} positions each."
        )


def main():
    print("Random Walk Simulation Using AgentPy")
    try:
        num_agents = int(input("Enter number of agents: "))
        grid_size = int(input("Enter grid size (e.g., 10 for 10x10): "))
        num_steps = int(input("Enter number of steps: "))
    except ValueError:
        print("Please enter whole numbers only.")
        return

    if num_agents < 1 or grid_size < 1 or num_steps < 1:
        print("Agents, grid size, and steps must all be at least 1.")
        return

    model = make_model(num_agents, grid_size, num_steps, False)
    print("\nAnimating the main scenario. Agents may share a square in this run.")
    animate_model(model)
    print_results(model, "Main scenario: final positions and paths")
    compare_scenarios()


if __name__ == "__main__":
    main()
