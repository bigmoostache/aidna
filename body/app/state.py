"""Body state management with energy system."""


class BodyState:
    """Manages the body's vital state including energy."""

    def __init__(self):
        self.energy: float = 100.0  # Starting energy
        self.age: int = 0  # Ticks since birth
        self.alive: bool = True

    def consume_energy(self, amount: float) -> bool:
        """Consume energy. Returns False if dead."""
        if not self.alive:
            return False
        self.energy -= amount
        if self.energy <= 0:
            self.energy = 0
            self.alive = False
            return False
        return True

    def gain_energy(self, amount: float) -> None:
        """Add energy (capped at 200)."""
        if self.alive:
            self.energy = min(200.0, self.energy + amount)

    def tick(self) -> None:
        """Increment age."""
        self.age += 1

    def to_dict(self) -> dict:
        """Return state as dictionary."""
        return {
            "energy": self.energy,
            "age": self.age,
            "alive": self.alive,
        }

    def reset(self) -> None:
        """Reset state for new run."""
        self.energy = 100.0
        self.age = 0
        self.alive = True


# Singleton state instance
state = BodyState()
