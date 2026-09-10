"""
Класс наездника (персонажа)
"""

class Rider:
    def __init__(self, name: str, level: int = 1, health: int = 100, attack: int = 10, defense: int = 5):
        self.name = name
        self.level = level
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.experience = 0
        self.dragon = None  # Привязанный дракон

    def take_damage(self, damage: int):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        return self.health > 0

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack += 5
        self.defense += 3
        print(f"✨ {self.name} повысил уровень до {self.level}!")

    def __str__(self):
        return f"👤 {self.name} | Ур. {self.level} | HP: {self.health}/{self.max_health} | АТК: {self.attack} | ЗАЩ: {self.defense}"
