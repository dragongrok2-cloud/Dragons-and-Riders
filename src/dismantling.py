"""
Система разбора предметов на материалы
"""

from typing import Dict, List, Optional, Tuple
from inventory import Item, ItemType, ItemQuality, Inventory, SAMPLE_ITEMS
import random


# Базовые материалы, которые можно получить при разборе
DISMANTLE_MATERIALS = {
    "dragon_scale": SAMPLE_ITEMS["dragon_scale"],
}

# Сколько базового материала даёт предмет в зависимости от типа
BASE_YIELD = {
    ItemType.WEAPON: {"dragon_scale": 1},
    ItemType.ARMOR: {"dragon_scale": 1},
    ItemType.SPECIAL: {"dragon_scale": 2},
    ItemType.DRAGON_GEAR: {"dragon_scale": 2},
    ItemType.CONSUMABLE: {},  # Зелья обычно не разбирают
    ItemType.MATERIAL: {},    # Материалы нельзя разобрать
}

# Множитель выхода материалов от качества
QUALITY_YIELD_MULTIPLIER = {
    ItemQuality.COMMON: 1.0,
    ItemQuality.UNCOMMON: 1.3,
    ItemQuality.RARE: 1.7,
    ItemQuality.EPIC: 2.3,
    ItemQuality.LEGENDARY: 3.5,
}

# Бонус от зачарований (каждый уровень зачарования даёт доп. материалы)
ENCHANT_BONUS_PER_LEVEL = 0.4


class DismantlingSystem:
    """Система разбора предметов на материалы"""

    def __init__(self):
        self.material_templates = DISMANTLE_MATERIALS

    def can_dismantle(self, item: Item) -> bool:
        """Можно ли разобрать этот предмет"""
        if item.item_type in (ItemType.CONSUMABLE, ItemType.MATERIAL):
            return False
        if item.stackable and item.item_type == ItemType.CONSUMABLE:
            return False
        return True

    def calculate_yield(self, item: Item) -> Dict[str, int]:
        """
        Рассчитать, сколько материалов получится при разборе.
        Возвращает {material_id: quantity}
        """
        if not self.can_dismantle(item):
            return {}

        base = BASE_YIELD.get(item.item_type, {}).copy()
        if not base:
            return {}

        quality_mult = QUALITY_YIELD_MULTIPLIER.get(item.quality, 1.0)

        # Бонус от зачарований
        enchant_levels = 0
        if hasattr(item, "enchantments") and item.enchantments:
            enchant_levels = sum(ae.level for ae in item.enchantments)

        enchant_mult = 1.0 + (enchant_levels * ENCHANT_BONUS_PER_LEVEL)

        result = {}
        for mat_id, base_qty in base.items():
            # Базовый выход × качество × зачарования
            qty = base_qty * quality_mult * enchant_mult

            # Небольшой случайный разброс ±20%
            variance = random.uniform(0.8, 1.2)
            final_qty = max(1, int(qty * variance))

            result[mat_id] = final_qty

        return result

    def preview(self, item: Item) -> str:
        """Показать, что можно получить при разборе"""
        if not self.can_dismantle(item):
            return f"❌ {item.name} нельзя разобрать"

        yields = self.calculate_yield(item)
        if not yields:
            return f"❌ При разборе {item.name} ничего не получится"

        parts = [f"{mat_id} x{qty}" for mat_id, qty in yields.items()]
        return f"🔧 При разборе «{item.name}» получите: {', '.join(parts)}"

    def dismantle(self, inventory: Inventory, item_id: str,
                  quality: ItemQuality = None) -> Optional[Dict[str, int]]:
        """
        Разобрать предмет.
        Возвращает словарь полученных материалов или None при неудаче.
        """
        item = inventory.get_item(item_id, quality)
        if not item:
            print(f"❌ Предмет {item_id} не найден в инвентаре")
            return None

        if not self.can_dismantle(item):
            print(f"❌ {item.name} нельзя разобрать")
            return None

        yields = self.calculate_yield(item)
        if not yields:
            print(f"❌ При разборе {item.name} ничего не получилось")
            return None

        # Удаляем предмет
        success = inventory.remove_item(item_id, 1, quality=item.quality)
        if not success:
            print(f"❌ Не удалось удалить {item.name}")
            return None

        # Добавляем материалы
        print(f"🔧 Разбираем: {item}")
        obtained = {}
        for mat_id, qty in yields.items():
            template = self.material_templates.get(mat_id)
            if template:
                # Создаём новый экземпляр материала
                from inventory import Item as ItemCls
                material = ItemCls(
                    id=template.id,
                    name=template.name,
                    item_type=template.item_type,
                    description=template.description,
                    value=template.base_value,
                    stackable=template.stackable,
                    max_stack=template.max_stack,
                    base_value=template.base_value
                )
                inventory.add_item(material, quantity=qty)
                obtained[mat_id] = qty
            else:
                print(f"⚠️ Неизвестный материал: {mat_id}")

        total = sum(obtained.values())
        print(f"✅ Получено материалов: {total}")
        return obtained

    def dismantle_all_of_type(self, inventory: Inventory, item_type: ItemType) -> Dict[str, int]:
        """Разобрать все предметы определённого типа"""
        to_dismantle = []
        for data in list(inventory.items.values()):
            item = data["item"]
            if item.item_type == item_type and self.can_dismantle(item):
                to_dismantle.append((item.id, item.quality))

        total_obtained: Dict[str, int] = {}
        for item_id, quality in to_dismantle:
            result = self.dismantle(inventory, item_id, quality)
            if result:
                for mat_id, qty in result.items():
                    total_obtained[mat_id] = total_obtained.get(mat_id, 0) + qty

        return total_obtained
