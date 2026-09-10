"""
Класс дракона
"""

from inventory import Inventory
from skills import SkillSet, DRAGON_SKILLS
from equipment import Equipment


class Dragon:
    ELEMENTS = ["fire", "ice", "lightning", "earth", "shadow", "wind"]

    def __init__(self, name: str, element: str = "fire", level: int = 1, health: int = 150, attack: int = 20):
        self.name = name
        self.element = element if element in self.ELEMENTS else "fire"
        self.level = level
        self.base_health = health
        self.base_attack = attack
        self.health = health
        self.max_health = health
        self.attack = attack
        self.stamina = 100
        self.max_stamina = 100
        self.rider = None

        # Инвентарь, навыки и экипировка
        self.inventory = Inventory(capacity=10)
        self.skills = SkillSet()
        self.equipment = Equipment(owner_type="dragon")

        # Стартовые навыки
        self.skills.add_skill(DRAGON_SKILLS["fire_breath"])
        self.skills.add_skill(DRAGON_SKILLS["wing_slash"])
        self.skills.add_skill(DRAGON_SKILLS["scale_armor"])

    def _recalculate_stats(self):
        """Пересчёт характеристик с учётом экипировки"""
        bonuses = self.equipment.get_total_bonuses()
        self.attack = self.base_attack + bonuses["attack"]
        old_max = self.max_health
        self.max_health = self.base_health + bonuses["health"]
        if old_max > 0:
            ratio = self.health / old_max
            self.health = int(self.max_health * ratio)

    def equip_item(self, item_id: str) -> bool:
        """Экипировать предмет из инвентаря"""
        item = self.inventory.get_item(item_id)
        if not item:
            print(f"❌ Предмет {item_id} не найден в инвентаре дракона")
            return False

        if not self.equipment.can_equip(item):
            print(f"❌ Нельзя экипировать {item.name} на дракона")
            return False

        previous = self.equipment.equip(item)
        if previous:
            self.inventory.add_item(previous)

        self.inventory.remove_item(item_id, 1)
        self._recalculate_stats()
        return True

    def unequip_item(self, slot: str) -> bool:
        item = self.equipment.unequip(slot)
        if item:
            self.inventory.add_item(item)
            self._recalculate_stats()
            return True
        return False

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
        self.base_health += 30
        self.base_attack += 7
        self.max_stamina += 15
        self.stamina = self.max_stamina
        self._recalculate_stats()
        self.health = self.max_health
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
            "base_health": self.base_health,
            "base_attack": self.base_attack,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "inventory": self.inventory.to_dict(),
            "skills": self.skills.to_dict(),
            "equipment": self.equipment.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dragon":
        dragon = cls(
            name=data["name"],
            element=data["element"],
            level=data["level"],
            health=data.get("base_health", data.get("health", 150)),
            attack=data.get("base_attack", data.get("attack", 20))
        )
        dragon.base_health = data.get("base_health", dragon.base_health)
        dragon.base_attack = data.get("base_attack", dragon.base_attack)
        dragon.health = data["health"]
        dragon.max_health = data["max_health"]
        dragon.attack = data["attack"]
        dragon.stamina = data.get("stamina", 100)
        dragon.max_stamina = data.get("max_stamina", 100)
        dragon.inventory = Inventory.from_dict(data.get("inventory", {}))
        dragon.skills = SkillSet.from_dict(data.get("skills", {}))
        if "equipment" in data:
            dragon.equipment = Equipment.from_dict(data["equipment"])
        dragon._recalculate_stats()
        return dragon

    def __str__(self):
        return (f"🐉 {self.name} ({self.element}) | Ур. {self.level} | "
                f"HP: {self.health}/{self.max_health} | "
                f"Выносливость: {self.stamina}/{self.max_stamina} | "
                f"АТК: {self.attack}")
