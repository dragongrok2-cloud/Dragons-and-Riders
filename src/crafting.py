"""
Система крафта предметов
С поддержкой качества
"""

from typing import Dict, List, Optional
from inventory import Item, ItemType, Inventory, SAMPLE_ITEMS, ItemQuality, create_item_with_quality, roll_quality
import random


class Recipe:
    def __init__(self, id: str, name: str, result_item: Item, ingredients: Dict[str, int],
                 description: str = "", required_level: int = 1,
                 result_quality: ItemQuality = None):
        """
        ingredients: {item_id: quantity}
        result_quality: если None — качество определяется случайно или от материалов
        """
        self.id = id
        self.name = name
        self.result_item = result_item
        self.ingredients = ingredients
        self.description = description
        self.required_level = required_level
        self.result_quality = result_quality

    def can_craft(self, inventory: Inventory, player_level: int) -> bool:
        if player_level < self.required_level:
            return False
        for item_id, qty in self.ingredients.items():
            if not inventory.has_item(item_id, qty):
                return False
        return True

    def get_missing_ingredients(self, inventory: Inventory) -> Dict[str, int]:
        missing = {}
        for item_id, qty in self.ingredients.items():
            current = 0
            for data in inventory.items.values():
                if data["item"].id == item_id:
                    current += data["quantity"]
            if current < qty:
                missing[item_id] = qty - current
        return missing

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "result_item": self.result_item.to_dict(),
            "ingredients": self.ingredients,
            "description": self.description,
            "required_level": self.required_level,
            "result_quality": self.result_quality.value if self.result_quality else None
        }

    def __str__(self):
        ings = ", ".join([f"{item_id} x{qty}" for item_id, qty in self.ingredients.items()])
        return f"{self.name} → {self.result_item.name} (нужно: {ings})"


class CraftingSystem:
    def __init__(self):
        self.recipes: Dict[str, Recipe] = {}
        self._register_default_recipes()

    def _register_default_recipes(self):
        """Регистрируем базовые рецепты"""

        steel_sword = Item(
            "steel_sword", "Стальной меч", ItemType.WEAPON,
            "Улучшенный клинок из стали", attack_bonus=15, value=120
        )
        self.add_recipe(Recipe(
            id="craft_steel_sword",
            name="Стальной меч",
            result_item=steel_sword,
            ingredients={"iron_sword": 1, "dragon_scale": 2},
            description="Усилить железный меч чешуёй дракона",
            required_level=2
        ))

        scale_armor = Item(
            "scale_armor", "Чешуйчатый доспех", ItemType.ARMOR,
            "Доспех из драконьей чешуи", defense_bonus=12, health_bonus=20, value=180
        )
        self.add_recipe(Recipe(
            id="craft_scale_armor",
            name="Чешуйчатый доспех",
            result_item=scale_armor,
            ingredients={"leather_armor": 1, "dragon_scale": 5},
            description="Создать прочный доспех из чешуи",
            required_level=3
        ))

        greater_potion = Item(
            "greater_health_potion", "Большое зелье здоровья", ItemType.CONSUMABLE,
            "Восстанавливает 120 HP", health_bonus=120, value=60,
            stackable=True, max_stack=5
        )
        self.add_recipe(Recipe(
            id="craft_greater_potion",
            name="Большое зелье здоровья",
            result_item=greater_potion,
            ingredients={"health_potion": 3},
            description="Объединить три обычных зелья",
            required_level=1
        ))

        storm_saddle = Item(
            "storm_saddle", "Штормовое седло", ItemType.DRAGON_GEAR,
            "Мощное седло, усиливающее дракона", attack_bonus=18, defense_bonus=5, value=350
        )
        self.add_recipe(Recipe(
            id="craft_storm_saddle",
            name="Штормовое седло",
            result_item=storm_saddle,
            ingredients={"fire_saddle": 1, "dragon_scale": 3, "storm_amulet": 1},
            description="Создать легендарное седло",
            required_level=5,
            result_quality=ItemQuality.RARE  # Гарантированно редкое
        ))

        power_amulet = Item(
            "power_amulet", "Амулет силы", ItemType.SPECIAL,
            "Значительно увеличивает атаку", attack_bonus=12, value=220
        )
        self.add_recipe(Recipe(
            id="craft_power_amulet",
            name="Амулет силы",
            result_item=power_amulet,
            ingredients={"storm_amulet": 1, "dragon_scale": 4},
            description="Усилить амулет чешуёй дракона",
            required_level=4
        ))

    def add_recipe(self, recipe: Recipe):
        self.recipes[recipe.id] = recipe

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        return self.recipes.get(recipe_id)

    def list_recipes(self, player_level: int = 99) -> List[Recipe]:
        return [r for r in self.recipes.values() if r.required_level <= player_level]

    def craft(self, recipe_id: str, inventory: Inventory, player_level: int) -> Optional[Item]:
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            print(f"❌ Рецепт {recipe_id} не найден")
            return None

        if player_level < recipe.required_level:
            print(f"❌ Нужен уровень {recipe.required_level} для крафта «{recipe.name}»")
            return None

        if not recipe.can_craft(inventory, player_level):
            missing = recipe.get_missing_ingredients(inventory)
            missing_str = ", ".join([f"{k} x{v}" for k, v in missing.items()])
            print(f"❌ Не хватает материалов: {missing_str}")
            return None

        # Списываем ингредиенты
        for item_id, qty in recipe.ingredients.items():
            inventory.remove_item(item_id, qty)

        # Определяем качество результата
        if recipe.result_quality:
            quality = recipe.result_quality
        else:
            # Небольшой шанс повышенного качества при крафте
            quality = roll_quality()
            # Крафт даёт небольшой бонус к качеству
            if random.random() < 0.25 and quality != ItemQuality.LEGENDARY:
                order = list(ItemQuality)
                idx = order.index(quality)
                if idx < len(order) - 1:
                    quality = order[idx + 1]

        result = recipe.result_item
        crafted = Item(
            id=result.id,
            name=result.name,
            item_type=result.item_type,
            description=result.description,
            quality=quality,
            base_attack=result.base_attack,
            base_defense=result.base_defense,
            base_health=result.base_health,
            base_value=result.base_value,
            stackable=result.stackable,
            max_stack=result.max_stack
        )

        success = inventory.add_item(crafted)
        if success:
            print(f"🔨 Успешно создано: {crafted}!")
            return crafted
        else:
            print(f"❌ Не удалось добавить {crafted.name} в инвентарь (возможно, он полон)")
            return None

    def upgrade_item_quality(self, inventory: Inventory, item_id: str,
                             material_id: str = "dragon_scale", material_cost: int = 3) -> bool:
        """
        Повысить качество предмета за материалы.
        """
        item = inventory.get_item(item_id)
        if not item:
            print(f"❌ Предмет {item_id} не найден")
            return False

        if item.quality == ItemQuality.LEGENDARY:
            print(f"❌ {item.name} уже легендарного качества")
            return False

        if not inventory.has_item(material_id, material_cost):
            print(f"❌ Не хватает {material_id} x{material_cost}")
            return False

        # Списываем материалы
        inventory.remove_item(material_id, material_cost)

        # Повышаем качество
        old_quality = item.quality.display_name
        success = item.upgrade_quality()
        if success:
            print(f"✨ {item.name}: {old_quality} → {item.quality.display_name}")
            print(f"   Новые характеристики: {item}")
            return True
        return False

    def print_recipes(self, player_level: int = 99):
        print("\n📜 Доступные рецепты:")
        for recipe in self.list_recipes(player_level):
            print(f"  • {recipe}")
