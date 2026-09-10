"""
Система сохранения и загрузки игры
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime


SAVE_DIR = "saves"


class SaveSystem:
    def __init__(self, save_dir: str = SAVE_DIR):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def _get_save_path(self, slot: int) -> str:
        return os.path.join(self.save_dir, f"save_slot_{slot}.json")

    def save_game(self, data: Dict[str, Any], slot: int = 1) -> bool:
        """
        Сохранить игру в указанный слот.
        data должен содержать сериализуемые данные персонажа, дракона и т.д.
        """
        try:
            save_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "slot": slot,
                "data": data
            }

            path = self._get_save_path(slot)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            print(f"💾 Игра успешно сохранена в слот {slot}!")
            return True

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False

    def load_game(self, slot: int = 1) -> Optional[Dict[str, Any]]:
        """Загрузить игру из указанного слота"""
        path = self._get_save_path(slot)

        if not os.path.exists(path):
            print(f"❌ Сохранение в слоте {slot} не найдено")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            print(f"📂 Игра загружена из слота {slot} (сохранено: {save_data.get('timestamp', 'неизвестно')})")
            return save_data.get("data")

        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return None

    def list_saves(self) -> list:
        """Показать все доступные сохранения"""
        saves = []
        for i in range(1, 6):  # 5 слотов
            path = self._get_save_path(i)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    saves.append({
                        "slot": i,
                        "timestamp": data.get("timestamp"),
                        "exists": True
                    })
                except:
                    saves.append({"slot": i, "timestamp": None, "exists": True})
            else:
                saves.append({"slot": i, "timestamp": None, "exists": False})
        return saves

    def delete_save(self, slot: int) -> bool:
        path = self._get_save_path(slot)
        if os.path.exists(path):
            os.remove(path)
            print(f"🗑️ Сохранение в слоте {slot} удалено")
            return True
        print(f"❌ Сохранение в слоте {slot} не найдено")
        return False

    def print_saves(self):
        print("\n📋 Список сохранений:")
        for save in self.list_saves():
            if save["exists"]:
                print(f"  Слот {save['slot']}: {save['timestamp']}")
            else:
                print(f"  Слот {save['slot']}: пусто")
