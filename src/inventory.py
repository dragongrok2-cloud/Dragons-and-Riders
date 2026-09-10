"""
Система инвентаря для персонажей и драконов
С поддержкой качества предметов
"""

from typing import Dict, List, Optional
from enum import Enum
import random


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    SPECIAL = "special"
    DRAGON_GEAR = "dragon_gear"


class ItemQuality(Enum):
    COMMON = "common"          # Обычный
    UNCOMMON = "uncommon"      # Необычный
    RARE = "rare"              # Редкий
    EPIC = "epic"              # Эпический
    LEGENDARY = "legendary"    # Легендарный

    @property
    def display_name(self) -> str:
        names = {
            "common": "Обычный",
            "uncommon": "Необычный",
            "rare": "Редкий",
            "epic": "Эпический",
            "legendary": "Легендарный"
        }
        return names.get(self.value, self.value)

    @property
    def color_tag(self) -> str:
        """Для красивого отображения"""
        tags = {
            "common": "⬜",
            "uncommon": "🟩",
            "rare": "🟦",
            "epic": "🟪",
            "legendary": "🟧"
        }
        return tags.get(self.value, "⬜")

    @property
    def multiplier(self) -> float:
        """Множитель характеристик"""
        multipliers = {
            "common": 1.0,
            "uncommon": 1.25,
            "rare": 1.5,
            "epic": 1.85,
            "legendary": 2.3
        }
        return multipliers.get(self.value, 1.0)

    @property
    def value_multiplier(self) -> float:
        multipliers = {
            "common": 1.0,
            "uncommon": 1.5,
            "rare": 2.5,
            "epic": 4.0,
            "legendary": 7.0
        }
        return multipliers.get(self.value, 1.0)


# Шансы выпадения качества (можно использовать при генерации лута)
QUALITY_WEIGHTS = {
    ItemQuality.COMMON: 50,
    ItemQuality.UNCOMMON: 30,
    ItemQuality.RARE: 13,
    ItemQuality.EPIC: 5,
    ItemQuality.LEGENDARY: 2,
}


def roll_quality() -> ItemQuality:
    """Случайное качество по весам"""
    qualities = list(QUALITY_WEIGHTS.keys())
    weights = list(QUALITY_WEIGHTS.values())
    return random.choices(qualities, weights=weights, k=1)[0]


class Item:
    def __init__(self, id: str, name: str, item_type: ItemType, description: str = "",
                 attack_bonus: int = 0, defense_bonus: int = 0, health_bonus: int = 0,
                 value: int = 0, stackable: bool = False, max_stack: int = 1,
                 quality: ItemQuality = ItemQuality.COMMON,
                 base_attack: int = None, base_defense: int = None, base_health: int = None,
                 base_value: int = None):
        self.id = id
        self.name = name
        self.item_type = item_type
        self.description = description
        self.quality = quality
        self.stackable = stackable
        self.max_stack = max_stack

        # Базовые значения (до применения качества)
        self.base_attack = base_attack if base_attack is not None else attack_bonus
        self.base_defense = base_defense if base_defense is not None else defense_bonus
        self.base_health = base_health if base_health is not None else health_bonus
        self.base_value = base_value if base_value is not None else value

        # Применяем множители качества
        self._apply_quality()

    def _apply_quality(self):
        mult = self.quality.multiplier
        self.attack_bonus = int(self.base_attack * mult)
        self.defense_bonus = int(self.base_defense * mult)
        self.health_bonus = int(self.base_health * mult)
        self.value = int(self.base_value * self.quality.value_multiplier)

    def set_quality(self, quality: ItemQuality):
        """Изменить качество и пересчитать бонусы"""
        self.quality = quality
        self._apply_quality()

    def upgrade_quality(self) -> bool:
        """Повысить качество на один уровень"""
        order = [
            ItemQuality.COMMON,
            ItemQuality.UNCOMMON,
            ItemQuality.RARE,
            ItemQuality.EPIC,
            ItemQuality.LEGENDARY
        ]
        try:
            idx = order.index(self.quality)
            if idx < len(order) - 1:
                self.set_quality(order[idx + 1])
                print(f"✨ Качество повышено до: {self.quality.display_name}!")
                return True
            else:
                print(f"❌ {self.name} уже легендарного качества")
                return False
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "item_type": self.item_type.value,
            "description": self.description,
            "quality": self.quality.value,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_health": self.base_health,
            "base_value": self.base_value,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "health_bonus": self.health_bonus,
            "value": self.value,
            "stackable": self.stackable,
            "max_stack": self.max_stack
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        quality = ItemQuality(data.get("quality", "common"))
        item = cls(
            id=data["id"],
            name=data["name"],
            item_type=ItemType(data["item_type"]),
            description=data.get("description", ""),
            quality=quality,
            base_attack=data.get("base_attack", data.get("attack_bonus", 0)),
            base_defense=data.get("base_defense", data.get("defense_bonus", 0)),
            base_health=data.get("base_health", data.get("health_bonus", 0)),
            base_value=data.get("base_value", data.get("value", 0)),
            stackable=data.get("stackable", False),
            max_stack=data.get("max_stack", 1)
        )
        return item

    def __str__(self):
        bonuses = []
        if self.attack_bonus:
            bonuses.append(f"АТК+{self.attack_bonus}")
        if self.defense_bonus:
            bonuses.append(f"ЗАЩ+{self.defense_bonus}")
        if self.health_bonus:
            bonuses.append(f"HP+{self.health_bonus}")
        bonus_str = f" ({', '.join(bonuses)})" if bonuses else ""
        return f"{self.quality.color_tag} [{self.quality.display_name}] {self.name}{bonus_str}"


class Inventory:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        # Ключ теперь учитывает качество: f"{item_id}_{quality}"
        self.items: Dict[str, dict] = {}  # unique_key -> {"item": Item, "quantity": int}

    def _make_key(self, item: Item) -> str:
        """Уникальный ключ с учётом качества (для нестакающихся)"""
        if item.stackable:
            return item.id  # стакающиеся предметы одного id и качества можно объединять
        return f"{item.id}_{item.quality.value}"

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """Добавить предмет в инвентарь"""
        key = self._make_key(item)

        if len(self.items) >= self.capacity and key not in self.items:
            print(f"❌ Инвентарь полон! Не удалось добавить {item.name}")
            return False

        if key in self.items:
            if item.stackable:
                current = self.items[key]["quantity"]
                new_qty = min(current + quantity, item.max_stack)
                added = new_qty - current
                self.items[key]["quantity"] = new_qty
                print(f"✅ Добавлено {item} x{added}")
                return True
            else:
                print(f"❌ {item.name} нельзя стакать")
                return False
        else:
            self.items[key] = {"item": item, "quantity": quantity}
            print(f"✅ Добавлено: {item} x{quantity}")
            return True

    def remove_item(self, item_id: str, quantity: int = 1, quality: ItemQuality = None) -> bool:
        """
        Удалить предмет.
        Если quality указан — ищем точное совпадение.
        Если нет — берём первый найденный с этим id.
        """
        key = None
        if quality:
            # Ищем точный ключ
            for k, data in self.items.items():
                if data["item"].id == item_id and data["item"].quality == quality:
                    key = k
                    break
        else:
            for k, data in self.items.items():
                if data["item"].id == item_id:
                    key = k
                    break

        if not key:
            return False

        current = self.items[key]["quantity"]
        if current <= quantity:
            del self.items[key]
        else:
            self.items[key]["quantity"] -= quantity
        return True

    def has_item(self, item_id: str, quantity: int = 1, quality: ItemQuality = None) -> bool:
        total = 0
        for data in self.items.values():
            if data["item"].id == item_id:
                if quality is None or data["item"].quality == quality:
                    total += data["quantity"]
        return total >= quantity

    def get_item(self, item_id: str, quality: ItemQuality = None) -> Optional[Item]:
        for data in self.items.values():
            if data["item"].id == item_id:
                if quality is None or data["item"].quality == quality:
                    return data["item"]
        return None

    def list_items(self) -> List[str]:
        result = []
        for data in self.items.values():
            item = data["item"]
            qty = data["quantity"]
            result.append(f"{item} x{qty}" if qty > 1 else str(item))
        return result

    def to_dict(self) -> dict:
        return {
            "capacity": self.capacity,
            "items": {
                key: {
                    "item": data["item"].to_dict(),
                    "quantity": data["quantity"]
                }
                for key, data in self.items.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Inventory":
        inv = cls(capacity=data.get("capacity", 20))
        for key, item_data in data.get("items", {}).items():
            item = Item.from_dict(item_data["item"])
            inv.items[key] = {"item": item, "quantity": item_data["quantity"]}
        return inv

    def __str__(self):
        if not self.items:
            return "Инвентарь пуст"
        lines = [f"Инвентарь ({len(self.items)}/{self.capacity}):"]
        for line in self.list_items():
            lines.append(f"  • {line}")
        return "\n".join(lines)


# Примеры предметов (по умолчанию обычного качества)
SAMPLE_ITEMS = {
    "iron_sword": Item("iron_sword", "Железный меч", ItemType.WEAPON, "Прочный железный меч",
                       attack_bonus=8, value=50),
    "leather_armor": Item("leather_armor", "Кожаный доспех", ItemType.ARMOR, "Лёгкая защита",
                          defense_bonus=5, value=40),
    "health_potion": Item("health_potion", "Зелье здоровья", ItemType.CONSUMABLE,
                          "Восстанавливает 50 HP", health_bonus=50, value=25,
                          stackable=True, max_stack=10),
    "dragon_scale": Item("dragon_scale", "Чешуя дракона", ItemType.MATERIAL,
                         "Редкий материал", value=100, stackable=True, max_stack=50),
    "fire_saddle": Item("fire_saddle", "Огненное седло", ItemType.DRAGON_GEAR,
                        "Увеличивает атаку дракона", attack_bonus=10, value=200),
    "storm_amulet": Item("storm_amulet", "Амулет бури", ItemType.SPECIAL,
                         "Усиливает стихийные атаки", attack_bonus=5, defense_bonus=3, value=150),
}


def create_item_with_quality(base_item: Item, quality: ItemQuality = None) -> Item:
    """Создать копию предмета с указанным (или случайным) качеством"""
    if quality is None:
        quality = roll_quality()
    return Item(
        id=base_item.id,
        name=base_item.name,
        item_type=base_item.item_type,
        description=base_item.description,
        quality=quality,
        base_attack=base_item.base_attack,
        base_defense=base_item.base_defense,
        base_health=base_item.base_health,
        base_value=base_item.base_value,
        stackable=base_item.stackable,
        max_stack=base_item.max_stack
    )
