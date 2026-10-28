# -*- coding: utf-8 -*-
"""Логика подбора блюда по продуктам в холодильнике и предпочтениям пользователя."""

import random
import re

from dishes import DISHES, SKILL_BY_DIFFICULTY

# Синонимы: пользователь может писать как угодно
SYNONYMS = {
    "картошка": "картофель", "картофана": "картофель", "картохa": "картофель",
    "помидоры": "помидор", "огурцы": "огурец", "перец болгарский": "перец",
    "курица": "курица", "курочка": "курица", "филе куриное": "курица",
    "говядина": "говядина", "говядинка": "говядина", "мясо": "говядина",
    "свинина": "свинина", "рыба": "рыба", "сельд": "сельдь", "селедка": "сельдь",
    "яйца": "яйцо", "яичко": "яйцо", "макарошки": "макароны", "паста": "макароны",
    "лапша": "лапша", "греча": "гречка", "гречиха": "гречка",
    "овсянка": "овсянка", "овсяные хлопья": "ovsyanka_alias", "геркулес": "овсянка",
    "масло сливочное": "масло", "подсолнечное масло": "масло", "оливковое масло": "масло",
    "растительное масло": "масло", "масло растительное": "масло",
    "творожок": "творог", "сметанка": "сметана", "сырок": "сыр",
    "кабачки": "кабачок", "патиссоны": "кабачок", "бэби кабачок": "кабачок",
    "грибочки": "грибы", "шампиньоны": "грибы", "белые грибы": "грибы",
    "солёный огурец": "огурец солёный", "корнишон": "огурец солёный",
    "маринованный огурец": "огурец солёный", "огурчик солёный": "огурец солёный",
    "сухофрукты": "сухофрукты", "изюм": "сухофрукты", "чернослив": "сухофрукты",
    "курага": "сухофрукты", "томат": "томатная паста", "кетчуп": "томатная паста",
}


def normalize(text: str) -> str:
    """Чистит строку до «сырых» слов в нижнем регистре."""
    text = text.lower().strip()
    text = re.sub(r"[^a-zа-яё0-9\s\-]", " ", text, flags=re.IGNORECASE | re.UNICODE)
    return re.sub(r"\s+", " ", text)


def parse_products(raw: str) -> list[str]:
    """Разбирает сообщение пользователя со списком продуктов.

    Принимает всё, что перечислено через запятую / перевод строки / точку с
    запятой; приводит к каноническим названиям через словарь синонимов.
    """
    parts = re.split(r"[,;\n\.\!]+| и ", raw.lower())
    products = []
    for p in parts:
        word = normalize(p)
        if not word or len(word) < 2:
            continue
        word = SYNONYMS.get(word, word)
        if word == "ovsyanka_alias":
            word = "овсянка"
        if word and word not in products:
            products.append(word)
    return products


def ingredient_matches(ingredient: str, fridge: list[str]) -> bool:
    """Ингредиент считается доступным, если в холодильнике есть слово,
    содержащее его (или наоборот), либо задан прямой синоним."""
    ing = normalize(ingredient)
    for fp in fridge:
        f = normalize(fp)
        if f == ing or f in ing or ing in f:
            return True
    return False


def score_dish(dish: dict, fridge: list[str]) -> tuple[float, list[str], list[str]]:
    """Возвращает (покрытие в %, найденные ингредиенты, чего не хватает)."""
    have, miss = [], []
    for ing in dish["ingredients"]:
        if ingredient_matches(ing, fridge):
            have.append(ing)
        else:
            miss.append(ing)
    coverage = len(have) / len(dish["ingredients"]) * 100 if dish["ingredients"] else 0
    return coverage, have, miss


def filter_dishes(
    fridge: list[str],
    category: str,
    diet: str,
    difficulty: str,
    min_coverage: float = 60.0,
):
    """Подбирает блюда под параметры. Возвращает список кортежей
    (dish, coverage, have, miss), отсортированный по убыванию покрытия."""
    result = []
    max_time = {"easy": 45, "medium": 100, "hard": 240}[difficulty]
    required_skill = SKILL_BY_DIFFICULTY[difficulty]
    skill_rank = {"beginner": 0, "cook": 1, "pro": 2}

    for dish in DISHES:
        # Категория («any» пользователя подходит ко всему, категория блюда any — тоже)
        if category != "any" and dish["category"] not in (category, "any"):
            continue
        # Диета
        if diet != "none" and diet not in dish["diets"]:
            continue
        # Сложность/умение/время: берём блюда не сложнее запрошенного уровня
        if skill_rank[dish["skills"]] > skill_rank[required_skill]:
            continue
        if dish["time"] > max_time + 30:
            continue
        # Продукты
        coverage, have, miss = score_dish(dish, fridge)
        if coverage < min_coverage:
            continue
        result.append((dish, coverage, have, miss))

    result.sort(key=lambda x: x[1], reverse=True)
    return result


def pick_random(candidates: list) -> dict:
    """Случайное блюдо из кандидатов (взвешенно по покрытию)."""
    weights = [max(c[1], 10) for c in candidates]
    dish = random.choices([c[0] for c in candidates], weights=weights, k=1)[0]
    # находим полный кортеж
    for c in candidates:
        if c[0] is dish:
            return {"dish": c[0], "coverage": c[1], "have": c[2], "miss": c[3]}
    return {"dish": dish, "coverage": 0, "have": [], "miss": dish["ingredients"]}
