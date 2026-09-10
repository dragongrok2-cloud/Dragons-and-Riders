"""
Dragons and Riders - Main entry point
Экшн-РПГ с драконами и кланами
"""

from character import Rider
from dragon import Dragon
from clan import Clan
from combat import Combat
from inventory import SAMPLE_ITEMS, ItemQuality, create_item_with_quality
from save_system import SaveSystem
from crafting import CraftingSystem
from enchanting import EnchantingSystem


def main():
    print("🐉 Добро пожаловать в Dragons and Riders!")
    print("Мир драконов ждёт тебя...\n")

    player = Rider(name="Аэрион", level=3, health=100, attack=15, defense=10)
    player_dragon = Dragon(name="Игнис", element="fire", level=1, health=150, attack=25)

    player.dragon = player_dragon
    player_dragon.rider = player

    print("=== Получение предметов ===")
    player.inventory.add_item(SAMPLE_ITEMS["iron_sword"])
    player.inventory.add_item(create_item_with_quality(SAMPLE_ITEMS["leather_armor"], ItemQuality.UNCOMMON))
    player.inventory.add_item(SAMPLE_ITEMS["health_potion"], quantity=5)
    player.inventory.add_item(SAMPLE_ITEMS["dragon_scale"], quantity=20)
    player.inventory.add_item(create_item_with_quality(SAMPLE_ITEMS["storm_amulet"], ItemQuality.RARE))
    player_dragon.inventory.add_item(create_item_with_quality(SAMPLE_ITEMS["fire_saddle"], ItemQuality.EPIC))

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

    # === Крафт ===
    print("=== Крафт ===")
    crafting = CraftingSystem()
    crafting.craft("craft_steel_sword", player.inventory, player.level)
    print()

    # === Зачарование ===
    print("=== Система зачарования ===")
    enchanter = EnchantingSystem()
    enchanter.print_available()

    print("\nНакладываем «Остроту 2» на стальной меч...")
    enchanter.enchant_item(player.inventory, "steel_sword", "sharpness", level=2)

    print("\nНакладываем «Критический удар 1» на стальной меч...")
    enchanter.enchant_item(player.inventory, "steel_sword", "crit_chance", level=1)

    print("\nНакладываем «Защиту 2» на кожаный доспех...")
    enchanter.enchant_item(player.inventory, "leather_armor", "protection", level=2)

    print("\nНакладываем «Пламя 1» на огненное седло дракона...")
    enchanter.enchant_item(player_dragon.inventory, "fire_saddle", "flame", level=1)

    print()
    print(player.inventory)
    print()
    print(player_dragon.inventory)
    print()

    # Экипируем зачарованный меч
    print("=== Экипируем зачарованный меч ===")
    player.equip_item("steel_sword")

    print()
    print(player)
    print(player.equipment)
    print()

    # Враг и бой
    enemy = Rider(name="Тёмный Всадник", level=1, health=90, attack=18, defense=8)
    enemy_dragon = Dragon(name="Тенекрыл", element="shadow", level=1, health=140, attack=22)

    clan = Clan(name="Пламенные Крылья")
    clan.add_member(player)

    print(f"Ты — {player.name}, наездник дракона {player_dragon.name}")
    print(f"Твой клан: {clan.name}\n")

    print("⚔️ Бой!")
    combat = Combat(player, player_dragon, enemy, enemy_dragon)
    combat.start()

    # Сохранение
    print("\n=== Сохранение ===")
    save_system = SaveSystem()
    save_data = {
        "player": player.to_dict(),
        "dragon": player_dragon.to_dict(),
        "clan_name": clan.name
    }
    save_system.save_game(save_data, slot=1)

    print("\n=== Загрузка ===")
    loaded = save_system.load_game(slot=1)
    if loaded:
        loaded_player = Rider.from_dict(loaded["player"])
        print(f"Загружен: {loaded_player}")
        print(loaded_player.equipment)


if __name__ == "__main__":
    main()
