"""
Система экипировки для наездников и драконов
"""

from typing import Dict, Optional
from inventory import Item, ItemType


class EquipmentSlot:
    """Слоты экипировки"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    # Для драконов
    SADDLE = "saddle"
    ARMOR_DRAGON = "dragon_armor"
    ACCESSORY_DRAGON = "dragon_accessory"


class Equipment:
    """Управление экипированными предметами"""

    def __init__(self, owner_type: str = "rider"):
        """
        owner_type: 'rider' или 'dragon'
        """
        self.owner_type = owner_type
        self.slots: Dict[str, Optional[Item]] = {}

        if owner_type == "rider":
            self.slots = {
                EquipmentSlot.WEAPON: None,
                EquipmentSlot.ARMOR: None,
                EquipmentSlot.ACCESSORY: None,
            }
        else:  # dragon
            self.slots = {
                EquipmentSlot.SADDLE: None,
                EquipmentSlot.ARMOR_DRAGON: None,
                EquipmentSlot.ACCESSORY_DRAGON: None,
            }

    def can_equip(self, item: Item) -> bool:
        """Проверяет, можно ли экипировать предмет"""
        if self.owner_type == "rider":
            if item.item_type == ItemType.WEAPON:
                return True
            if item.item_type == ItemType.ARMOR:
                return True
            if item.item_type == ItemType.SPECIAL:
                return True
        else:  # dragon
            if item.item_type == ItemType.DRAGON_GEAR:
                return True
            if item.item_type == ItemType.SPECIAL:
                return True
        return False

    def get_slot_for_item(self, item: Item) -> Optional[str]:
        """Определяет слот для предмета"""
        if self.owner_type == "rider":
            if item.item_type == ItemType.WEAPON:
                return EquipmentSlot.WEAPON
            if item.item_type == ItemType.ARMOR:
                return EquipmentSlot.ARMOR
            if item.item_type == ItemType.SPECIAL:
                return EquipmentSlot.ACCESSORY
        else:
            if item.item_type == ItemType.DRAGON_GEAR:
                # Пока все dragon_gear идут в седло, можно расширить
                if "седло" in item.name.lower() or "saddle" in item.id.lower():
                    return EquipmentSlot.SADDLE
                return EquipmentSlot.ARMOR_DRAGON
            if item.item_type == ItemType.SPECIAL:
                return EquipmentSlot.ACCESSORY_DRAGON
        return None

    def equip(self, item: Item) -> Optional[Item]:
        """
        Экипировать предмет.
        Возвращает предыдущий предмет в слоте (если был), иначе None.
        """
        if not self.can_equip(item):
            print(f"❌ Нельзя экипировать {item.name}")
            return None

        slot = self.get_slot_for_item(item)
        if not slot:
            print(f"❌ Не найден слот для {item.name}")
            return None

        previous = self.slots.get(slot)
        self.slots[slot] = item
        print(f"🛡️ Экипировано: {item.name} → слот [{slot}]")
        return previous

    def unequip(self, slot: str) -> Optional[Item]:
        """Снять предмет из слота"""
        if slot not in self.slots:
            print(f"❌ Слот {slot} не существует")
            return None

        item = self.slots[slot]
        if item is None:
            print(f"❌ Слот {slot} уже пуст")
            return None

        self.slots[slot] = None
        print(f"📤 Снято: {item.name}")
        return item

    def get_total_bonuses(self) -> dict:
        """Суммарные бонусы от всей экипировки"""
        bonuses = {
            "attack": 0,
            "defense": 0,
            "health": 0
        }
        for item in self.slots.values():
            if item:
                bonuses["attack"] += item.attack_bonus
                bonuses["defense"] += item.defense_bonus
                bonuses["health"] += item.health_bonus
        return bonuses

    def get_equipped_items(self) -> Dict[str, Optional[Item]]:
        return self.slots.copy()

    def to_dict(self) -> dict:
        return {
            "owner_type": self.owner_type,
            "slots": {
                slot: item.to_dict() if item else None
                for slot, item in self.slots.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Equipment":
        eq = cls(owner_type=data.get("owner_type", "rider"))
        for slot, item_data in data.get("slots", {}).items():
            if item_data:
                eq.slots[slot] = Item.from_dict(item_data)
            else:
                eq.slots[slot] = None
        return eq

    def __str__(self):
        lines = [f"Экипировка ({self.owner_type}):"]
        for slot, item in self.slots.items():
            if item:
                lines.append(f"  [{slot}] {item}")
            else:
                lines.append(f"  [{slot}] — пусто —")
        bonuses = self.get_total_bonuses()
        lines.append(f"  Бонусы: АТК+{bonuses['attack']}, ЗАЩ+{bonuses['defense']}, HP+{bonuses['health']}")
        return "\n".join(lines)
