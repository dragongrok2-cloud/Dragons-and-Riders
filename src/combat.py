"""
Система боя
"""

from character import Rider
from dragon import Dragon


class Combat:
    def __init__(self, rider1: Rider, dragon1: Dragon, rider2: Rider, dragon2: Dragon):
        self.rider1 = rider1
        self.dragon1 = dragon1
        self.rider2 = rider2
        self.dragon2 = dragon2

    def start(self):
        print("\n⚔️ === БОЙ НАЧИНАЕТСЯ === ⚔️\n")
        print(f"{self.rider1.name} + {self.dragon1.name}  VS  {self.rider2.name} + {self.dragon2.name}\n")

        round_num = 1
        while self.rider1.is_alive() and self.dragon1.is_alive() and self.rider2.is_alive() and self.dragon2.is_alive():
            print(f"--- Раунд {round_num} ---")

            # Атака игрока
            dmg = self.dragon1.breathe_attack()
            actual = self.dragon2.take_damage(dmg)
            print(f"🔥 {self.dragon1.name} дышит огнём! Нанесено {actual} урона {self.dragon2.name}")

            if not self.dragon2.is_alive():
                print(f"💀 {self.dragon2.name} повержен!")
                break

            # Атака врага
            dmg = self.dragon2.breathe_attack()
            actual = self.dragon1.take_damage(dmg)
            print(f"🌑 {self.dragon2.name} контратакует! Нанесено {actual} урона {self.dragon1.name}")

            if not self.dragon1.is_alive():
                print(f"💀 {self.dragon1.name} повержен!")
                break

            print()
            round_num += 1

            if round_num > 10:  # Защита от бесконечного боя
                print("Бой затянулся... Ничья!")
                break

        print("\n🏁 Бой завершён!")
        if self.dragon1.is_alive():
            print(f"🏆 Победа за {self.rider1.name} и {self.dragon1.name}!")
        else:
            print(f"☠️ Поражение... {self.rider2.name} победил.")
