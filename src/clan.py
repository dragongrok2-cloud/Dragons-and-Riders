"""
Система кланов
"""

from typing import List
from character import Rider


class Clan:
    def __init__(self, name: str):
        self.name = name
        self.members: List[Rider] = []
        self.level = 1
        self.reputation = 0

    def add_member(self, rider: Rider):
        if rider not in self.members:
            self.members.append(rider)
            print(f"🛡️ {rider.name} вступил в клан «{self.name}»!")

    def remove_member(self, rider: Rider):
        if rider in self.members:
            self.members.remove(rider)

    def get_member_count(self) -> int:
        return len(self.members)

    def __str__(self):
        return f"🏰 Клан «{self.name}» | Уровень: {self.level} | Участников: {self.get_member_count()} | Репутация: {self.reputation}"
