"""
Система инвентаря для персонажей и драконов
"""

from typing import Dict, List, Optional
from enum import Enum


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    SPECIAL = "special"
    DRAGON_GEAR = "dragon_gear"  # Снаряжение для дракона


class Item:
    def __init__(self, id: str, name: str, item_type: ItemType, description: str = "",
                 attack_bonus: int = 0, defense_bonus: int = 0, health_bonus: int = 0,
                 value: int = 0, stackable: bool = False, max_stack: int = 1):
        self.id = id
        self.name = name
        self.item_type = item_type
        self.description = description
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.health_bonus = health_bonus
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "item_type": self.item_type.value,
            "description": self.description,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "health_bonus": self.health_bonus,
            "value": self.value,
            "stackable": self.stackable,
            "max_stack": self.max_stack
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            id=data["id"],
            name=data["name"],
            item_type=ItemType(data["item_type"]),
            description=data.get("description", ""),
            attack_bonus=data.get("attack_bonus", 0),
            defense_bonus=data.get("defense_bonus", 0),
            health_bonus=data.get("health_bonus", 0),
            value=data.get("value", 0),
            stackable=data.get("stackable", False),
            max_stack=data.get("max_stack", 1)
        )

    def __str__(self):
        bonuses = []
        if self.attack_bonus:
            bonuses.append(f"АТК+{self.attack_bonus}")
        if self.defense_bonus:
            bonuses.append(f"ЗАЩ+{self.defense_bonus}")
        if self.health_bonus:
            bonuses.append(f"HP+{self.health_bonus}")
        bonus_str = f" ({', '.join(bonuses)})" if bonuses else ""
        return f"{self.name}{bonus_str}"


class Inventory:
    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.items: Dict[str, dict] = {}  # item_id -> {"item": Item, "quantity": int}

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """Добавить предмет в инвентарь"""
        if len(self.items) >= self.capacity and item.id not in self.items:
            print(f"❌ Инвентарь полон! Не удалось добавить {item.name}")
            return False

        if item.id in self.items:
            if item.stackable:
                current = self.items[item.id]["quantity"]
                new_qty = min(current + quantity, item.max_stack)
                self.items[item.id]["quantity"] = new_qty
                print(f"✅ Добавлено {item.name} x{new_qty - current}")
                return True
            else:
                print(f"❌ {item.name} нельзя стакать")
                return False
        else:
            self.items[item.id] = {"item": item, "quantity": quantity}
            print(f"✅ Добавлено: {item.name} x{quantity}")
            return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        if item_id not in self.items:
            return False

        current = self.items[item_id]["quantity"]
        if current <= quantity:
            del self.items[item_id]
        else:
            self.items[item_id]["quantity"] -= quantity
        return True

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        if item_id not in self.items:
            return False
        return self.items[item_id]["quantity"] >= quantity

    def get_item(self, item_id: str) -> Optional[Item]:
        if item_id in self.items:
            return self.items[item_id]["item"]
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
                item_id: {
                    "item": data["item"].to_dict(),
                    "quantity": data["quantity"]
                }
                for item_id, data in self.items.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Inventory":
        inv = cls(capacity=data.get("capacity", 20))
        for item_id, item_data in data.get("items", {}).items():
            item = Item.from_dict(item_data["item"])
            inv.items[item_id] = {"item": item, "quantity": item_data["quantity"]}
        return inv

    def __str__(self):
        if not self.items:
            return "Инвентарь пуст"
        lines = [f"Инвентарь ({len(self.items)}/{self.capacity}):"]
        for line in self.list_items():
            lines.append(f"  • {line}")
        return "\n".join(lines)


# Примеры предметов
SAMPLE_ITEMS = {
    "iron_sword": Item("iron_sword", "Железный меч", ItemType.WEAPON, "Прочный железный меч", attack_bonus=8, value=50),
    "leather_armor": Item("leather_armor", "Кожаный доспех", ItemType.ARMOR, "Лёгкая защита", defense_bonus=5, value=40),
    "health_potion": Item("health_potion", "Зелье здоровья", ItemType.CONSUMABLE, "Восстанавливает 50 HP", health_bonus=50, value=25, stackable=True, max_stack=10),
    "dragon_scale": Item("dragon_scale", "Чешуя дракона", ItemType.MATERIAL, "Редкий материал", value=100, stackable=True, max_stack=50),
    "fire_saddle": Item("fire_saddle", "Огненное седло", ItemType.DRAGON_GEAR, "Увеличивает атаку дракона", attack_bonus=10, value=200),
    "storm_amulet": Item("storm_amulet", "Амулет бури", ItemType.SPECIAL, "Усиливает стихийные атаки", attack_bonus=5, defense_bonus=3, value=150),
}
