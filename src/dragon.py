"""
Класс дракона
"""

class Dragon:
    ELEMENTS = ["fire", "ice", "lightning", "earth", "shadow", "wind"]

    def __init__(self, name: str, element: str = "fire", level: int = 1, health: int = 150, attack: int = 20):
        self.name = name
        self.element = element if element in self.ELEMENTS else "fire"
        self.level = level
        self.health = health
        self.max_health = health
        self.attack = attack
        self.rider = None

    def breathe_attack(self) -> int:
        """Огненное/стихийное дыхание"""
        base = self.attack * 1.5
        # Бонус за стихию можно расширить позже
        return int(base)

    def take_damage(self, damage: int):
        self.health = max(0, self.health - damage)
        return damage

    def is_alive(self) -> bool:
        return self.health > 0

    def __str__(self):
        return f"🐉 {self.name} ({self.element}) | Ур. {self.level} | HP: {self.health}/{self.max_health} | АТК: {self.attack}"
