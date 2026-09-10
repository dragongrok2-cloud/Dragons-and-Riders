"""
Dragons and Riders - Main entry point
Экшн-РПГ с драконами и кланами
"""

from character import Rider
from dragon import Dragon
from clan import Clan
from combat import Combat


def main():
    print("🐉 Добро пожаловать в Dragons and Riders!")
    print("Мир драконов ждёт тебя...\n")

    # Создаём игрока
    player = Rider(name="Аэрион", level=1, health=100, attack=15, defense=10)
    player_dragon = Dragon(name="Игнис", element="fire", level=1, health=150, attack=25)

    # Создаём врага
    enemy = Rider(name="Тёмный Всадник", level=1, health=90, attack=18, defense=8)
    enemy_dragon = Dragon(name="Тенекрыл", element="shadow", level=1, health=140, attack=22)

    # Создаём клан
    clan = Clan(name="Пламенные Крылья")
    clan.add_member(player)

    print(f"Ты — {player.name}, наездник дракона {player_dragon.name}")
    print(f"Твой клан: {clan.name}\n")

    # Пример боя
    print("⚔️ Внезапно на тебя нападает враг!")
    combat = Combat(player, player_dragon, enemy, enemy_dragon)
    combat.start()


if __name__ == "__main__":
    main()
