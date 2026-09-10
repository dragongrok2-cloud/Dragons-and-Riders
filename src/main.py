"""
Dragons and Riders - Main entry point
Экшн-РПГ с драконами и кланами
"""

from character import Rider
from dragon import Dragon
from clan import Clan
from combat import Combat
from inventory import SAMPLE_ITEMS
from save_system import SaveSystem
from crafting import CraftingSystem


def main():
    print("🐉 Добро пожаловать в Dragons and Riders!")
    print("Мир драконов ждёт тебя...\n")

    # Создаём игрока
    player = Rider(name="Аэрион", level=3, health=100, attack=15, defense=10)  # Уровень 3 для крафта
    player_dragon = Dragon(name="Игнис", element="fire", level=1, health=150, attack=25)

    # Связываем наездника и дракона
    player.dragon = player_dragon
    player_dragon.rider = player

    # Добавляем предметы в инвентарь
    print("=== Получение стартовых предметов ===")
    player.inventory.add_item(SAMPLE_ITEMS["iron_sword"])
    player.inventory.add_item(SAMPLE_ITEMS["leather_armor"])
    player.inventory.add_item(SAMPLE_ITEMS["health_potion"], quantity=5)
    player.inventory.add_item(SAMPLE_ITEMS["dragon_scale"], quantity=8)
    player.inventory.add_item(SAMPLE_ITEMS["storm_amulet"])
    player_dragon.inventory.add_item(SAMPLE_ITEMS["fire_saddle"])

    print()
    print(player)
    print(player_dragon)
    print()
    print(player.inventory)
    print()

    # === Экипировка ===
    print("=== Экипировка ===")
    player.equip_item("iron_sword")
    player.equip_item("leather_armor")
    player_dragon.equip_item("fire_saddle")

    print()
    print(player)
    print(player.equipment)
    print()
    print(player_dragon)
    print(player_dragon.equipment)
    print()

    # === Крафт ===
    print("=== Система крафта ===")
    crafting = CraftingSystem()
    crafting.print_recipes(player_level=player.level)

    print("\nПробуем скрафтить Большое зелье здоровья...")
    crafting.craft("craft_greater_potion", player.inventory, player.level)

    print("\nПробуем скрафтить Стальной меч...")
    crafting.craft("craft_steel_sword", player.inventory, player.level)

    print("\nПробуем скрафтить Чешуйчатый доспех...")
    crafting.craft("craft_scale_armor", player.inventory, player.level)

    print()
    print(player.inventory)
    print()

    # Экипируем скрафченные предметы
    print("=== Экипируем новые предметы ===")
    player.equip_item("steel_sword")
    player.equip_item("scale_armor")

    print()
    print(player)
    print(player.equipment)
    print()

    # Создаём врага
    enemy = Rider(name="Тёмный Всадник", level=1, health=90, attack=18, defense=8)
    enemy_dragon = Dragon(name="Тенекрыл", element="shadow", level=1, health=140, attack=22)

    # Создаём клан
    clan = Clan(name="Пламенные Крылья")
    clan.add_member(player)

    print(f"Ты — {player.name}, наездник дракона {player_dragon.name}")
    print(f"Твой клан: {clan.name}\n")

    # Пример использования навыка
    print("=== Использование навыка ===")
    player.use_skill("power_strike")
    player_dragon.use_skill("fire_breath")
    print()

    # Пример боя
    print("⚔️ Внезапно на тебя нападает враг!")
    combat = Combat(player, player_dragon, enemy, enemy_dragon)
    combat.start()

    # === Система сохранения ===
    print("\n=== Система сохранения ===")
    save_system = SaveSystem()

    save_data = {
        "player": player.to_dict(),
        "dragon": player_dragon.to_dict(),
        "clan_name": clan.name
    }
    save_system.save_game(save_data, slot=1)
    save_system.print_saves()

    print("\n=== Загрузка сохранения ===")
    loaded = save_system.load_game(slot=1)
    if loaded:
        loaded_player = Rider.from_dict(loaded["player"])
        loaded_dragon = Dragon.from_dict(loaded["dragon"])
        print(f"Загружен персонаж: {loaded_player}")
        print(f"Загружен дракон: {loaded_dragon}")
        print(loaded_player.equipment)


if __name__ == "__main__":
    main()
