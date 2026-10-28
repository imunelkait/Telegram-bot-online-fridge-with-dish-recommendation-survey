# -*- coding: utf-8 -*-
"""База блюд для бота «Онлайн-холодильник».

Каждое блюдо описывается словарём:
    name        — название;
    ingredients — список ингредиентов (в нижнем регистре, в единственном числе);
    category    — предпочтения: meat / fish / grains / veggies / soup / sweet / any;
    diets       — подходящие диеты: none / pp / veg / keto / dairy_free / gluten_free;
    difficulty  — сложность: easy / medium / hard;
    time        — примерное время приготовления (минуты);
    skills      — требуемые умения: beginner / cook / pro.
"""

DISHES = [
    # ---------- МЯСО ----------
    {
        "name": "Жаркое из говядины с картошкой",
        "ingredients": ["говядина", "картофель", "лук", "морковь", "масло"],
        "category": "meat", "diets": ["none", "gluten_free"],
        "difficulty": "medium", "time": 90, "skills": "cook",
    },
    {
        "name": "Куриная грудка на сковороде с гречкой",
        "ingredients": ["курица", "гречка", "масло", "соль", "специи"],
        "category": "meat", "diets": ["pp", "dairy_free", "gluten_free"],
        "difficulty": "easy", "time": 40, "skills": "beginner",
    },
    {
        "name": "Плов с курицей",
        "ingredients": ["курица", "рис", "морковь", "лук", "масло", "специи"],
        "category": "meat", "diets": ["none", "dairy_free"],
        "difficulty": "medium", "time": 80, "skills": "cook",
    },
    {
        "name": "Гуляш из свинины с макаронами",
        "ingredients": ["свинина", "макароны", "лук", "морковь", "томатная паста", "масло"],
        "category": "meat", "diets": ["none"],
        "difficulty": "medium", "time": 70, "skills": "cook",
    },
    {
        "name": "Отбивная из курицы",
        "ingredients": ["курица", "яйцо", "мука", "масло", "соль"],
        "category": "meat", "diets": ["none"],
        "difficulty": "easy", "time": 30, "skills": "beginner",
    },
    {
        "name": "Фрикадельки в томатном соусе",
        "ingredients": ["говядина", "лук", "яйцо", "хлеб", "томатная паста", "масло"],
        "category": "meat", "diets": ["none"],
        "difficulty": "medium", "time": 60, "skills": "cook",
    },
    {
        "name": "Стейк из говядины на сковороде",
        "ingredients": ["говядина", "масло", "соль", "перец"],
        "category": "meat", "diets": ["keto", "gluten_free", "dairy_free"],
        "difficulty": "hard", "time": 25, "skills": "pro",
    },
    {
        "name": "Индейка тушёная с овощами",
        "ingredients": ["индейка", "кабачок", "перец", "помидор", "лук", "масло"],
        "category": "meat", "diets": ["pp", "keto", "dairy_free", "gluten_free"],
        "difficulty": "medium", "time": 60, "skills": "cook",
    },

    # ---------- РЫБА ----------
    {
        "name": "Запечённая рыба с лимоном",
        "ingredients": ["рыба", "лимон", "масло", "соль", "специи"],
        "category": "fish", "diets": ["pp", "keto", "dairy_free", "gluten_free"],
        "difficulty": "easy", "time": 35, "skills": "beginner",
    },
    {
        "name": "Рыба под овощной шубой",
        "ingredients": ["рыба", "морковь", "лук", "помидор", "масло"],
        "category": "fish", "diets": ["pp", "dairy_free"],
        "difficulty": "medium", "time": 50, "skills": "cook",
    },
    {
        "name": "Сельдь под шубой",
        "ingredients": ["сельдь", "картофель", "свёкла", "морковь", "майонез", "яйцо"],
        "category": "fish", "diets": ["none"],
        "difficulty": "medium", "time": 60, "skills": "cook",
    },
    {
        "name": "Котлеты рыбные",
        "ingredients": ["рыба", "хлеб", "лук", "яйцо", "масло"],
        "category": "fish", "diets": ["none"],
        "difficulty": "medium", "time": 45, "skills": "cook",
    },

    # ---------- КРУПЫ / ГАРНИРЫ ----------
    {
        "name": "Гречка с грибами и луком",
        "ingredients": ["гречка", "грибы", "лук", "масло", "соль"],
        "category": "grains", "diets": ["veg", "vegan", "dairy_free"],
        "difficulty": "easy", "time": 35, "skills": "beginner",
    },
    {
        "name": "Рис с овощами (плов постный)",
        "ingredients": ["рис", "морковь", "лук", "чеснок", "масло", "специи"],
        "category": "grains", "diets": ["veg", "vegan", "dairy_free"],
        "difficulty": "easy", "time": 40, "skills": "beginner",
    },
    {
        "name": "Овсяная каша на воде с яблоком",
        "ingredients": ["овсянка", "яблоко", "сахар", "корица"],
        "category": "grains", "diets": ["veg", "vegan", "pp", "dairy_free"],
        "difficulty": "easy", "time": 15, "skills": "beginner",
    },
    {
        "name": "Макароны по-флотски",
        "ingredients": ["макароны", "говядина", "лук", "масло"],
        "category": "grains", "diets": ["none"],
        "difficulty": "easy", "time": 40, "skills": "beginner",
    },
    {
        "name": "Ленивые голубцы с рисом и капустой",
        "ingredients": ["капуста", "рис", "говядина", "морковь", "лук", "томатная паста"],
        "category": "grains", "diets": ["none"],
        "difficulty": "medium", "time": 70, "skills": "cook",
    },

    # ---------- ОВОЩИ ----------
    {
        "name": "Винегрет",
        "ingredients": ["свёкла", "картофель", "морковь", "огурец солёный", "горошек", "масло"],
        "category": "veggies", "diets": ["veg", "vegan", "pp", "dairy_free", "gluten_free"],
        "difficulty": "easy", "time": 40, "skills": "beginner",
    },
    {
        "name": "Овощное рагу с кабачками",
        "ingredients": ["кабачок", "картофель", "помидор", "перец", "лук", "масло"],
        "category": "veggies", "diets": ["veg", "vegan", "pp", "dairy_free"],
        "difficulty": "easy", "time": 45, "skills": "beginner",
    },
    {
        "name": "Греческий салат",
        "ingredients": ["помидор", "огурец", "перец", "лук", "сыр", "масло", "оливки"],
        "category": "veggies", "diets": ["veg", "keto", "gluten_free"],
        "difficulty": "easy", "time": 15, "skills": "beginner",
    },
    {
        "name": "Голубцы с мясом",
        "ingredients": ["капуста", "говядина", "рис", "морковь", "лук", "томатная паста", "сметана"],
        "category": "veggies", "diets": ["none"],
        "difficulty": "hard", "time": 120, "skills": "pro",
    },
    {
        "name": "Картошка тушёная с грибами",
        "ingredients": ["картофель", "грибы", "лук", "масло", "сметана"],
        "category": "veggies", "diets": ["veg"],
        "difficulty": "easy", "time": 45, "skills": "beginner",
    },
    {
        "name": "Цукини в кляре",
        "ingredients": ["кабачок", "яйцо", "мука", "масло", "соль"],
        "category": "veggies", "diets": ["veg"],
        "difficulty": "easy", "time": 25, "skills": "beginner",
    },
    {
        "name": "Борщ вегетарианский",
        "ingredients": ["свёкла", "капуста", "картофель", "морковь", "лук", "томатная паста"],
        "category": "soup", "diets": ["veg", "vegan", "pp", "dairy_free"],
        "difficulty": "medium", "time": 80, "skills": "cook",
    },

    # ---------- СУПЫ ----------
    {
        "name": "Борщ с говядиной",
        "ingredients": ["говядина", "свёкла", "капуста", "картофель", "морковь", "лук", "томатная паста", "сметана"],
        "category": "soup", "diets": ["none"],
        "difficulty": "hard", "time": 120, "skills": "pro",
    },
    {
        "name": "Куриный суп с лапшой",
        "ingredients": ["курица", "лапша", "картофель", "морковь", "лук"],
        "category": "soup", "diets": ["none", "pp"],
        "difficulty": "easy", "time": 60, "skills": "beginner",
    },
    {
        "name": "Солянка сборная",
        "ingredients": ["колбаса", "сосиски", "огурец солёный", "лук", "томатная паста", "лимон", "масло"],
        "category": "soup", "diets": ["none"],
        "difficulty": "medium", "time": 70, "skills": "cook",
    },
    {
        "name": "Уха из рыбы",
        "ingredients": ["рыба", "картофель", "морковь", "лук", "пшено"],
        "category": "soup", "diets": ["pp", "dairy_free", "gluten_free"],
        "difficulty": "medium", "time": 60, "skills": "cook",
    },
    {
        "name": "Гороховый суп с копчёностями",
        "ingredients": ["горох", "картофель", "морковь", "лук", "копчёности"],
        "category": "soup", "diets": ["none"],
        "difficulty": "medium", "time": 90, "skills": "cook",
    },

    # ---------- ЯЙЦА / БЫСТРОЕ ----------
    {
        "name": "Яичница с помидорами",
        "ingredients": ["яйцо", "помидор", "масло", "соль"],
        "category": "any", "diets": ["veg", "keto", "gluten_free"],
        "difficulty": "easy", "time": 10, "skills": "beginner",
    },
    {
        "name": "Омлет с сыром",
        "ingredients": ["яйцо", "молоко", "сыр", "масло"],
        "category": "any", "diets": ["veg", "keto"],
        "difficulty": "easy", "time": 10, "skills": "beginner",
    },
    {
        "name": "Сырники",
        "ingredients": ["творог", "яйцо", "мука", "сахар", "масло", "сметана"],
        "category": "sweet", "diets": ["veg"],
        "difficulty": "easy", "time": 30, "skills": "beginner",
    },
    {
        "name": "Блинчики с творогом",
        "ingredients": ["мука", "молоко", "яйцо", "творог", "сахар", "масло"],
        "category": "sweet", "diets": ["veg"],
        "difficulty": "medium", "time": 60, "skills": "cook",
    },

    # ---------- СЛАДКОЕ ----------
    {
        "name": "Шарлотка с яблоками",
        "ingredients": ["яблоко", "мука", "яйцо", "сахар", "корица"],
        "category": "sweet", "diets": ["veg"],
        "difficulty": "easy", "time": 50, "skills": "beginner",
    },
    {
        "name": "Творожная запеканка",
        "ingredients": ["творог", "яйцо", "манка", "сахар", "изюм", "сметана"],
        "category": "sweet", "diets": ["veg", "pp"],
        "difficulty": "medium", "time": 60, "skills": "cook",
    },
    {
        "name": "Компот из сухофруктов",
        "ingredients": ["сухофрукты", "сахар"],
        "category": "sweet", "diets": ["veg", "vegan", "pp", "dairy_free", "gluten_free"],
        "difficulty": "easy", "time": 30, "skills": "beginner",
    },
]

# Категории предпочтений для кнопок
CATEGORIES = {
    "meat": "🥩 Мясо",
    "fish": "🐟 Рыба",
    "grains": "🌾 Крупы/гарниры",
    "veggies": "🥕 Овощи",
    "soup": "🍲 Суп",
    "sweet": "🍰 Сладкое",
    "any": "🤷 Любая",
}

DIETS = {
    "none": "Без ограничений",
    "pp": "Правильное питание",
    "veg": "Вегетарианская",
    "vegan": "Веганская",
    "keto": "Кето",
    "dairy_free": "Без молочного",
    "gluten_free": "Без глютена",
}

DIFFICULTIES = {
    "easy": "🟢 Просто (до 30 мин, новичок)",
    "medium": "🟡 Средне (30–90 мин, есть опыт)",
    "hard": "🔴 Сложно (90+ мин, уверенный навык)",
}

SKILL_BY_DIFFICULTY = {"easy": "beginner", "medium": "cook", "hard": "pro"}
