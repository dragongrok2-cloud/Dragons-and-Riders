"""
Класс дракона
"""

from inventory import Inventory
from skills import SkillSet, DRAGON_SKILLS


class Dragon:
    ELEMENTS = ["fire", "ice", "lightning", "earth", "shadow", "wind"]

    def __init__(self, name: str, element: str = "fire", level: int = 1, health: int = 150, attack: int = 20):
        self.name = name
        self.element = element if element in self.ELEMENTS else "fire"
        self.level = level
        self.health = health
        self.max_health = health
        self.attack = attack
        self.stamina = 100
        self.max_stamina = 100
        self.rider = None

        # Инвентарь (снаряжение дракона) и навыки
        self.inventory = Inventory(capacity=10)  # У драконов меньше слотов
        self.skills = SkillSet()

        # Стартовые навыки
        self.skills.add_skill(DRAGON_SKILLS["fire_breath"])
        self.skills.add_skill(DRAGON_SKILLS["wing_slash"])
        self.skills.add_skill(DRAGON_SKILLS["scale_armor"])

    def breathe_attack(self) -> int:
        """Огненное/стихийное дыхание"""
        base = self.attack * 1.5
        return int(base)

    def take_damage(self, damage: int):
        self.health = max(0, self.health - damage)
        return damage

    def is_alive(self) -> bool:
        return self.health > 0

    def restore_stamina(self, amount: int):
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def level_up(self):
        self.level += 1
        self.max_health += 30
        self.health = self.max_health
        self.max_stamina += 15
        self.stamina = self.max_stamina
        self.attack += 7
        print(f"🐉 {self.name} повысил уровень до {self.level}!")

        if self.level >= 4 and "dragon_roar" not in self.skills.skills:
            self.skills.add_skill(DRAGON_SKILLS["dragon_roar"])
        if self.level >= 7 and "inferno" not in self.skills.skills:
            self.skills.add_skill(DRAGON_SKILLS["inferno"])

    def use_skill(self, skill_id: str):
        skill = self.skills.get_skill(skill_id)
        if not skill:
            print(f"❌ Навык {skill_id} не найден")
            return False

        if not skill.can_use(self.level, self.stamina):
            print(f"❌ Нельзя использовать {skill.name} сейчас")
            return False

        self.stamina -= skill.cost
        skill.use()
        print(f"🔥 {self.name} использует «{skill.name}»!")
        return True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "element": self.element,
            "level": self.level,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "inventory": self.inventory.to_dict(),
            "skills": self.skills.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dragon":
        dragon = cls(
            name=data["name"],
            element=data["element"],
            level=data["level"],
            health=data["health"],
            attack=data["attack"]
        )
        dragon.max_health = data["max_health"]
        dragon.stamina = data.get("stamina", 100)
        dragon.max_stamina = data.get("max_stamina", 100)
        dragon.inventory = Inventory.from_dict(data.get("inventory", {}))
        dragon.skills = SkillSet.from_dict(data.get("skills", {}))
        return dragon

    def __str__(self):
        return (f"🐉 {self.name} ({self.element}) | Ур. {self.level} | "
                f"HP: {self.health}/{self.max_health} | "
                f"Выносливость: {self.stamina}/{self.max_stamina} | "
                f"АТК: {self.attack}")
