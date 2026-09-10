"""
Класс наездника (персонажа)
"""

from inventory import Inventory, SAMPLE_ITEMS, Item
from skills import SkillSet, RIDER_SKILLS
from equipment import Equipment


class Rider:
    def __init__(self, name: str, level: int = 1, health: int = 100, attack: int = 10, defense: int = 5):
        self.name = name
        self.level = level
        self.base_health = health
        self.base_attack = attack
        self.base_defense = defense
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.experience = 0
        self.mana = 50
        self.max_mana = 50
        self.dragon = None  # Привязанный дракон

        # Инвентарь, навыки и экипировка
        self.inventory = Inventory(capacity=25)
        self.skills = SkillSet()
        self.equipment = Equipment(owner_type="rider")

        # Стартовые навыки
        self.skills.add_skill(RIDER_SKILLS["power_strike"])
        self.skills.add_skill(RIDER_SKILLS["iron_will"])

    def _recalculate_stats(self):
        """Пересчёт характеристик с учётом экипировки"""
        bonuses = self.equipment.get_total_bonuses()
        self.attack = self.base_attack + bonuses["attack"]
        self.defense = self.base_defense + bonuses["defense"]
        old_max = self.max_health
        self.max_health = self.base_health + bonuses["health"]
        # Корректируем текущее HP пропорционально, если max изменился
        if old_max > 0:
            ratio = self.health / old_max
            self.health = int(self.max_health * ratio)

    def equip_item(self, item_id: str) -> bool:
        """Экипировать предмет из инвентаря"""
        item = self.inventory.get_item(item_id)
        if not item:
            print(f"❌ Предмет {item_id} не найден в инвентаре")
            return False

        if not self.equipment.can_equip(item):
            print(f"❌ Нельзя экипировать {item.name}")
            return False

        # Снимаем предыдущий предмет в слоте (если есть) и возвращаем в инвентарь
        previous = self.equipment.equip(item)
        if previous:
            self.inventory.add_item(previous)

        # Убираем экипируемый предмет из инвентаря
        self.inventory.remove_item(item_id, 1)
        self._recalculate_stats()
        return True

    def unequip_item(self, slot: str) -> bool:
        """Снять предмет и вернуть в инвентарь"""
        item = self.equipment.unequip(slot)
        if item:
            self.inventory.add_item(item)
            self._recalculate_stats()
            return True
        return False

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
        self.base_health += 20
        self.base_attack += 5
        self.base_defense += 3
        self.max_mana += 10
        self.mana = self.max_mana
        self._recalculate_stats()
        self.health = self.max_health
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
            "base_health": self.base_health,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "experience": self.experience,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "inventory": self.inventory.to_dict(),
            "skills": self.skills.to_dict(),
            "equipment": self.equipment.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Rider":
        rider = cls(
            name=data["name"],
            level=data["level"],
            health=data.get("base_health", data.get("health", 100)),
            attack=data.get("base_attack", data.get("attack", 10)),
            defense=data.get("base_defense", data.get("defense", 5))
        )
        rider.base_health = data.get("base_health", rider.base_health)
        rider.base_attack = data.get("base_attack", rider.base_attack)
        rider.base_defense = data.get("base_defense", rider.base_defense)
        rider.health = data["health"]
        rider.max_health = data["max_health"]
        rider.attack = data["attack"]
        rider.defense = data["defense"]
        rider.experience = data.get("experience", 0)
        rider.mana = data.get("mana", 50)
        rider.max_mana = data.get("max_mana", 50)
        rider.inventory = Inventory.from_dict(data.get("inventory", {}))
        rider.skills = SkillSet.from_dict(data.get("skills", {}))
        if "equipment" in data:
            rider.equipment = Equipment.from_dict(data["equipment"])
        rider._recalculate_stats()
        return rider

    def __str__(self):
        return (f"👤 {self.name} | Ур. {self.level} | "
                f"HP: {self.health}/{self.max_health} | "
                f"Мана: {self.mana}/{self.max_mana} | "
                f"АТК: {self.attack} | ЗАЩ: {self.defense}")
