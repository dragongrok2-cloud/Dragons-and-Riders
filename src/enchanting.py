"""
Система зачарования предметов
"""

from typing import Dict, List, Optional
from enum import Enum
from inventory import Item, ItemType, ItemQuality, Inventory
import random


class EnchantType(Enum):
    ATTACK = "attack"              # + к атаке
    DEFENSE = "defense"            # + к защите
    HEALTH = "health"              # + к здоровью
    CRITICAL = "critical"          # шанс критического удара
    LIFE_STEAL = "life_steal"      # вампиризм
    ELEMENTAL = "elemental"        # стихийный урон
    STAMINA = "stamina"            # + к выносливости (для драконов)
    MANA = "mana"                  # + к мане (для наездников)


class Enchantment:
    def __init__(self, id: str, name: str, enchant_type: EnchantType,
                 power: int, description: str = "",
                 max_level: int = 5, compatible_types: List[ItemType] = None):
        self.id = id
        self.name = name
        self.enchant_type = enchant_type
        self.power = power                  # Базовая сила за уровень
        self.description = description
        self.max_level = max_level
        self.compatible_types = compatible_types or [
            ItemType.WEAPON, ItemType.ARMOR, ItemType.SPECIAL, ItemType.DRAGON_GEAR
        ]

    def get_bonus(self, level: int) -> int:
        return self.power * level

    def can_apply_to(self, item: Item) -> bool:
        return item.item_type in self.compatible_types

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "enchant_type": self.enchant_type.value,
            "power": self.power,
            "description": self.description,
            "max_level": self.max_level,
            "compatible_types": [t.value for t in self.compatible_types]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Enchantment":
        return cls(
            id=data["id"],
            name=data["name"],
            enchant_type=EnchantType(data["enchant_type"]),
            power=data["power"],
            description=data.get("description", ""),
            max_level=data.get("max_level", 5),
            compatible_types=[ItemType(t) for t in data.get("compatible_types", [])]
        )

    def __str__(self):
        return f"{self.name} (+{self.power}/ур.)"


# Базовые зачарования
ENCHANTMENTS = {
    "sharpness": Enchantment(
        "sharpness", "Острота", EnchantType.ATTACK, power=3,
        description="Увеличивает атаку",
        compatible_types=[ItemType.WEAPON, ItemType.DRAGON_GEAR]
    ),
    "protection": Enchantment(
        "protection", "Защита", EnchantType.DEFENSE, power=2,
        description="Увеличивает защиту",
        compatible_types=[ItemType.ARMOR, ItemType.DRAGON_GEAR, ItemType.SPECIAL]
    ),
    "vitality": Enchantment(
        "vitality", "Живучесть", EnchantType.HEALTH, power=8,
        description="Увеличивает максимальное здоровье",
        compatible_types=[ItemType.ARMOR, ItemType.SPECIAL, ItemType.DRAGON_GEAR]
    ),
    "crit_chance": Enchantment(
        "crit_chance", "Критический удар", EnchantType.CRITICAL, power=5,
        description="Шанс нанести критический урон (%)",
        compatible_types=[ItemType.WEAPON, ItemType.DRAGON_GEAR]
    ),
    "vampirism": Enchantment(
        "vampirism", "Вампиризм", EnchantType.LIFE_STEAL, power=3,
        description="Восстанавливает HP от нанесённого урона (%)",
        compatible_types=[ItemType.WEAPON, ItemType.SPECIAL]
    ),
    "flame": Enchantment(
        "flame", "Пламя", EnchantType.ELEMENTAL, power=4,
        description="Добавляет огненный урон",
        compatible_types=[ItemType.WEAPON, ItemType.DRAGON_GEAR]
    ),
    "mana_flow": Enchantment(
        "mana_flow", "Поток маны", EnchantType.MANA, power=5,
        description="Увеличивает максимальную ману",
        compatible_types=[ItemType.SPECIAL, ItemType.ARMOR]
    ),
    "endurance": Enchantment(
        "endurance", "Выносливость", EnchantType.STAMINA, power=6,
        description="Увеличивает выносливость дракона",
        compatible_types=[ItemType.DRAGON_GEAR]
    ),
}


class AppliedEnchantment:
    """Зачарование, наложенное на предмет"""

    def __init__(self, enchantment: Enchantment, level: int = 1):
        self.enchantment = enchantment
        self.level = min(level, enchantment.max_level)

    @property
    def bonus(self) -> int:
        return self.enchantment.get_bonus(self.level)

    def to_dict(self) -> dict:
        return {
            "enchantment": self.enchantment.to_dict(),
            "level": self.level
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppliedEnchantment":
        ench = Enchantment.from_dict(data["enchantment"])
        return cls(ench, data.get("level", 1))

    def __str__(self):
        return f"{self.enchantment.name} {self.level} (+{self.bonus})"


class EnchantingSystem:
    """Система наложения и управления зачарованиями"""

    # Стоимость зачарования в чешуе дракона (за уровень)
    BASE_COST = 2
    # Шанс успеха зависит от качества предмета и уровня зачарования
    SUCCESS_CHANCE = {
        ItemQuality.COMMON: 0.90,
        ItemQuality.UNCOMMON: 0.85,
        ItemQuality.RARE: 0.75,
        ItemQuality.EPIC: 0.60,
        ItemQuality.LEGENDARY: 0.45,
    }

    def __init__(self):
        self.available = ENCHANTMENTS

    def get_enchantment(self, enchant_id: str) -> Optional[Enchantment]:
        return self.available.get(enchant_id)

    def list_enchantments(self, item: Item = None) -> List[Enchantment]:
        if item is None:
            return list(self.available.values())
        return [e for e in self.available.values() if e.can_apply_to(item)]

    def calculate_cost(self, level: int) -> int:
        """Стоимость в чешуе дракона"""
        return self.BASE_COST * level

    def get_success_chance(self, item: Item, level: int) -> float:
        base = self.SUCCESS_CHANCE.get(item.quality, 0.7)
        # Чем выше уровень зачарования — тем сложнее
        penalty = (level - 1) * 0.08
        return max(0.15, base - penalty)

    def enchant_item(self, inventory: Inventory, item_id: str,
                     enchant_id: str, level: int = 1,
                     material_id: str = "dragon_scale") -> bool:
        """
        Наложить зачарование на предмет.
        Требует материалы и имеет шанс неудачи.
        """
        item = inventory.get_item(item_id)
        if not item:
            print(f"❌ Предмет {item_id} не найден в инвентаре")
            return False

        enchant = self.get_enchantment(enchant_id)
        if not enchant:
            print(f"❌ Зачарование {enchant_id} не найдено")
            return False

        if not enchant.can_apply_to(item):
            print(f"❌ «{enchant.name}» нельзя наложить на {item.name}")
            return False

        level = max(1, min(level, enchant.max_level))
        cost = self.calculate_cost(level)

        if not inventory.has_item(material_id, cost):
            print(f"❌ Не хватает материалов: нужно {material_id} x{cost}")
            return False

        # Проверяем, есть ли уже это зачарование
        if not hasattr(item, "enchantments"):
            item.enchantments = []

        existing = None
        for ae in item.enchantments:
            if ae.enchantment.id == enchant_id:
                existing = ae
                break

        if existing and existing.level >= level:
            print(f"❌ На предмете уже есть «{enchant.name}» уровня {existing.level} или выше")
            return False

        # Списываем материалы
        inventory.remove_item(material_id, cost)

        chance = self.get_success_chance(item, level)
        print(f"🔮 Попытка наложить «{enchant.name} {level}» на {item.name}...")
        print(f"   Шанс успеха: {chance*100:.0f}% | Стоимость: {cost} × {material_id}")

        if random.random() > chance:
            print(f"💥 Зачарование провалилось! Материалы потеряны.")
            return False

        # Успех
        if existing:
            existing.level = level
            print(f"✨ Зачарование усилено: {existing}")
        else:
            applied = AppliedEnchantment(enchant, level)
            item.enchantments.append(applied)
            print(f"✨ Успешно наложено: {applied}")

        # Пересчитываем бонусы предмета от зачарований
        self._apply_enchant_bonuses(item)
        print(f"   Итог: {item}")
        return True

    def _apply_enchant_bonuses(self, item: Item):
        """Добавляет бонусы от зачарований к характеристикам предмета"""
        if not hasattr(item, "enchantments") or not item.enchantments:
            return

        # Сбрасываем к базовым + качество, потом добавляем зачарования
        item._apply_quality()

        for ae in item.enchantments:
            if ae.enchantment.enchant_type == EnchantType.ATTACK:
                item.attack_bonus += ae.bonus
            elif ae.enchantment.enchant_type == EnchantType.DEFENSE:
                item.defense_bonus += ae.bonus
            elif ae.enchantment.enchant_type == EnchantType.HEALTH:
                item.health_bonus += ae.bonus
            # CRITICAL, LIFE_STEAL, ELEMENTAL и т.д. хранятся отдельно
            # и используются в бою (можно расширить combat.py позже)

    def remove_enchantment(self, item: Item, enchant_id: str) -> bool:
        if not hasattr(item, "enchantments"):
            return False
        for i, ae in enumerate(item.enchantments):
            if ae.enchantment.id == enchant_id:
                removed = item.enchantments.pop(i)
                self._apply_enchant_bonuses(item)
                print(f"🗑️ Снято зачарование: {removed}")
                return True
        return False

    def get_item_enchantments(self, item: Item) -> List[AppliedEnchantment]:
        if not hasattr(item, "enchantments"):
            return []
        return item.enchantments

    def print_available(self, item: Item = None):
        print("\n📜 Доступные зачарования:")
        for ench in self.list_enchantments(item):
            print(f"  • {ench} — {ench.description}")
