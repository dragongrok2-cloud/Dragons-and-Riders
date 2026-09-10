"""
Система крафта предметов
"""

from typing import Dict, List, Optional
from inventory import Item, ItemType, Inventory, SAMPLE_ITEMS


class Recipe:
    def __init__(self, id: str, name: str, result_item: Item, ingredients: Dict[str, int],
                 description: str = "", required_level: int = 1):
        """
        ingredients: {item_id: quantity}
        """
        self.id = id
        self.name = name
        self.result_item = result_item
        self.ingredients = ingredients  # item_id -> количество
        self.description = description
        self.required_level = required_level

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
            if inventory.has_item(item_id):
                current = inventory.items[item_id]["quantity"]
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
            "required_level": self.required_level
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

        # Улучшенный меч
        steel_sword = Item(
            "steel_sword", "Стальной меч", ItemType.WEAPON,
            "Улучшенный клинок из стали", attack_bonus=15, value=120
        )
        self.add_recipe(Recipe(
            id="craft_steel_sword",
            name="Стальной меч",
            result_item=steel_sword,
            ingredients={
                "iron_sword": 1,
                "dragon_scale": 2
            },
            description="Усилить железный меч чешуёй дракона",
            required_level=2
        ))

        # Улучшенный доспех
        scale_armor = Item(
            "scale_armor", "Чешуйчатый доспех", ItemType.ARMOR,
            "Доспех из драконьей чешуи", defense_bonus=12, health_bonus=20, value=180
        )
        self.add_recipe(Recipe(
            id="craft_scale_armor",
            name="Чешуйчатый доспех",
            result_item=scale_armor,
            ingredients={
                "leather_armor": 1,
                "dragon_scale": 5
            },
            description="Создать прочный доспех из чешуи",
            required_level=3
        ))

        # Большое зелье здоровья
        greater_potion = Item(
            "greater_health_potion", "Большое зелье здоровья", ItemType.CONSUMABLE,
            "Восстанавливает 120 HP", health_bonus=120, value=60,
            stackable=True, max_stack=5
        )
        self.add_recipe(Recipe(
            id="craft_greater_potion",
            name="Большое зелье здоровья",
            result_item=greater_potion,
            ingredients={
                "health_potion": 3
            },
            description="Объединить три обычных зелья",
            required_level=1
        ))

        # Улучшенное седло
        storm_saddle = Item(
            "storm_saddle", "Штормовое седло", ItemType.DRAGON_GEAR,
            "Мощное седло, усиливающее дракона", attack_bonus=18, defense_bonus=5, value=350
        )
        self.add_recipe(Recipe(
            id="craft_storm_saddle",
            name="Штормовое седло",
            result_item=storm_saddle,
            ingredients={
                "fire_saddle": 1,
                "dragon_scale": 3,
                "storm_amulet": 1
            },
            description="Создать легендарное седло",
            required_level=5
        ))

        # Амулет силы
        power_amulet = Item(
            "power_amulet", "Амулет силы", ItemType.SPECIAL,
            "Значительно увеличивает атаку", attack_bonus=12, value=220
        )
        self.add_recipe(Recipe(
            id="craft_power_amulet",
            name="Амулет силы",
            result_item=power_amulet,
            ingredients={
                "storm_amulet": 1,
                "dragon_scale": 4
            },
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
        """
        Попытаться скрафтить предмет.
        Возвращает созданный Item при успехе, иначе None.
        """
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

        # Добавляем результат
        result = recipe.result_item
        # Создаём новый экземпляр, чтобы не мутировать оригинал
        crafted = Item(
            id=result.id,
            name=result.name,
            item_type=result.item_type,
            description=result.description,
            attack_bonus=result.attack_bonus,
            defense_bonus=result.defense_bonus,
            health_bonus=result.health_bonus,
            value=result.value,
            stackable=result.stackable,
            max_stack=result.max_stack
        )

        success = inventory.add_item(crafted)
        if success:
            print(f"🔨 Успешно создано: {crafted.name}!")
            return crafted
        else:
            print(f"❌ Не удалось добавить {crafted.name} в инвентарь (возможно, он полон)")
            # Возвращаем ингредиенты обратно было бы хорошо, но для простоты пока так
            return None

    def print_recipes(self, player_level: int = 99):
        print("\n📜 Доступные рецепты:")
        for recipe in self.list_recipes(player_level):
            print(f"  • {recipe}")
