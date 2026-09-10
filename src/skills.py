"""
Система навыков для персонажей и драконов
"""

from typing import Dict, List, Optional
from enum import Enum


class SkillType(Enum):
    ACTIVE = "active"       # Активный навык (нужно использовать)
    PASSIVE = "passive"     # Пассивный (всегда работает)
    ULTIMATE = "ultimate"   # Ультимативный


class SkillTarget(Enum):
    SELF = "self"
    ENEMY = "enemy"
    ALLY = "ally"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"


class Skill:
    def __init__(self, id: str, name: str, description: str,
                 skill_type: SkillType, target: SkillTarget,
                 power: int = 0, cost: int = 0, cooldown: int = 0,
                 level_required: int = 1, element: str = None):
        self.id = id
        self.name = name
        self.description = description
        self.skill_type = skill_type
        self.target = target
        self.power = power              # Сила навыка
        self.cost = cost                # Стоимость (мана/выносливость)
        self.cooldown = cooldown        # Перезарядка в ходах
        self.level_required = level_required
        self.element = element          # Стихия (для драконов)
        self.current_cooldown = 0

    def can_use(self, user_level: int, current_resource: int) -> bool:
        if user_level < self.level_required:
            return False
        if self.current_cooldown > 0:
            return False
        if current_resource < self.cost:
            return False
        return True

    def use(self):
        """Применить навык (запускает кулдаун)"""
        self.current_cooldown = self.cooldown

    def tick_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "skill_type": self.skill_type.value,
            "target": self.target.value,
            "power": self.power,
            "cost": self.cost,
            "cooldown": self.cooldown,
            "level_required": self.level_required,
            "element": self.element,
            "current_cooldown": self.current_cooldown
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Skill":
        skill = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            skill_type=SkillType(data["skill_type"]),
            target=SkillTarget(data["target"]),
            power=data.get("power", 0),
            cost=data.get("cost", 0),
            cooldown=data.get("cooldown", 0),
            level_required=data.get("level_required", 1),
            element=data.get("element")
        )
        skill.current_cooldown = data.get("current_cooldown", 0)
        return skill

    def __str__(self):
        cd = f" [КД: {self.current_cooldown}]" if self.current_cooldown > 0 else ""
        return f"{self.name} (Сила: {self.power}, Стоимость: {self.cost}){cd}"


class SkillSet:
    """Набор навыков персонажа или дракона"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}

    def add_skill(self, skill: Skill):
        self.skills[skill.id] = skill
        print(f"✨ Изучен навык: {skill.name}")

    def remove_skill(self, skill_id: str):
        if skill_id in self.skills:
            del self.skills[skill_id]

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)

    def get_available_skills(self, user_level: int, resource: int) -> List[Skill]:
        return [s for s in self.skills.values() if s.can_use(user_level, resource)]

    def tick_all_cooldowns(self):
        for skill in self.skills.values():
            skill.tick_cooldown()

    def to_dict(self) -> dict:
        return {
            "skills": {sid: skill.to_dict() for sid, skill in self.skills.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SkillSet":
        skillset = cls()
        for sid, skill_data in data.get("skills", {}).items():
            skillset.skills[sid] = Skill.from_dict(skill_data)
        return skillset

    def __str__(self):
        if not self.skills:
            return "Навыки отсутствуют"
        lines = ["Навыки:"]
        for skill in self.skills.values():
            lines.append(f"  • {skill}")
        return "\n".join(lines)


# Примеры навыков для наездников
RIDER_SKILLS = {
    "power_strike": Skill(
        "power_strike", "Мощный удар", "Сильная атака ближнего боя",
        SkillType.ACTIVE, SkillTarget.ENEMY, power=30, cost=15, cooldown=2, level_required=1
    ),
    "battle_cry": Skill(
        "battle_cry", "Боевой клич", "Повышает атаку союзников",
        SkillType.ACTIVE, SkillTarget.ALL_ALLIES, power=10, cost=20, cooldown=4, level_required=3
    ),
    "second_wind": Skill(
        "second_wind", "Второе дыхание", "Восстанавливает здоровье",
        SkillType.ACTIVE, SkillTarget.SELF, power=40, cost=25, cooldown=5, level_required=2
    ),
    "iron_will": Skill(
        "iron_will", "Железная воля", "Пассивно увеличивает защиту",
        SkillType.PASSIVE, SkillTarget.SELF, power=5, level_required=1
    ),
}

# Примеры навыков для драконов
DRAGON_SKILLS = {
    "fire_breath": Skill(
        "fire_breath", "Огненное дыхание", "Классическая огненная атака",
        SkillType.ACTIVE, SkillTarget.ENEMY, power=40, cost=20, cooldown=2,
        level_required=1, element="fire"
    ),
    "wing_slash": Skill(
        "wing_slash", "Удар крылом", "Быстрая атака крыльями",
        SkillType.ACTIVE, SkillTarget.ENEMY, power=25, cost=10, cooldown=1, level_required=1
    ),
    "dragon_roar": Skill(
        "dragon_roar", "Рёв дракона", "Оглушает врагов и снижает их защиту",
        SkillType.ACTIVE, SkillTarget.ALL_ENEMIES, power=15, cost=30, cooldown=5, level_required=4
    ),
    "scale_armor": Skill(
        "scale_armor", "Чешуйчатая броня", "Пассивно увеличивает защиту",
        SkillType.PASSIVE, SkillTarget.SELF, power=8, level_required=1
    ),
    "inferno": Skill(
        "inferno", "Инферно", "Мощная ультимативная атака огнём",
        SkillType.ULTIMATE, SkillTarget.ALL_ENEMIES, power=80, cost=50, cooldown=8,
        level_required=7, element="fire"
    ),
}
