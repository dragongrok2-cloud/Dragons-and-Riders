"""
Класс наездника (персонажа)
"""

from inventory import Inventory, SAMPLE_ITEMS
from skills import SkillSet, RIDER_SKILLS


class Rider:
    def __init__(self, name: str, level: int = 1, health: int = 100, attack: int = 10, defense: int = 5):
        self.name = name
        self.level = level
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.experience = 0
        self.mana = 50
        self.max_mana = 50
        self.dragon = None  # Привязанный дракон

        # Инвентарь и навыки
        self.inventory = Inventory(capacity=25)
        self.skills = SkillSet()

        # Стартовые навыки
        self.skills.add_skill(RIDER_SKILLS["power_strike"])
        self.skills.add_skill(RIDER_SKILLS["iron_will"])

    def take_damage(self, damage: int):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def restore_mana(self, amount: int):
        self.mana = min(self.max_mana, self.mana + amount)

    def is_alive(self) -> bool:
        return self.health > 0

    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.max_mana += 10
        self.mana = self.max_mana
        self.attack += 5
        self.defense += 3
        print(f"✨ {self.name} повысил уровень до {self.level}!")

        # Разблокировка новых навыков
        if self.level >= 2 and "second_wind" not in self.skills.skills:
            self.skills.add_skill(RIDER_SKILLS["second_wind"])
        if self.level >= 3 and "battle_cry" not in self.skills.skills:
            self.skills.add_skill(RIDER_SKILLS["battle_cry"])

    def use_skill(self, skill_id: str, target=None):
        skill = self.skills.get_skill(skill_id)
        if not skill:
            print(f"❌ Навык {skill_id} не найден")
            return False

        if not skill.can_use(self.level, self.mana):
            print(f"❌ Нельзя использовать {skill.name} сейчас")
            return False

        self.mana -= skill.cost
        skill.use()
        print(f"⚡ {self.name} использует «{skill.name}»!")
        return True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "experience": self.experience,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "inventory": self.inventory.to_dict(),
            "skills": self.skills.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Rider":
        rider = cls(
            name=data["name"],
            level=data["level"],
            health=data["health"],
            attack=data["attack"],
            defense=data["defense"]
        )
        rider.max_health = data["max_health"]
        rider.experience = data.get("experience", 0)
        rider.mana = data.get("mana", 50)
        rider.max_mana = data.get("max_mana", 50)
        rider.inventory = Inventory.from_dict(data.get("inventory", {}))
        rider.skills = SkillSet.from_dict(data.get("skills", {}))
        return rider

    def __str__(self):
        return (f"👤 {self.name} | Ур. {self.level} | "
                f"HP: {self.health}/{self.max_health} | "
                f"Мана: {self.mana}/{self.max_mana} | "
                f"АТК: {self.attack} | ЗАЩ: {self.defense}")
