from typing import Dict, List

CATEGORY_TITLES: Dict[str, str] = {
    "worship":      "🎤 Worship",
    "kids":         "👶 Kids",
    "youth":        "🔥 Youth | Teens",
    "media":        "🎥 Media",
    "welcome":      "🤝 Welcome Team",
    "hospitality":  "🥗 Hospitality",
    "discover":     "✨ Discover Your Calling",
}

CATEGORY_HEADLINES: Dict[str, str] = {
    "discover": (
        "Иногда бывает непросто понять, где именно служить и какое направление выбрать. "
        "Но не переживайте — вы не одни! Наши лидеры с радостью помогут вам открыть ваши дары "
        "и найти то служение, где вы сможете приносить наибольшую радость и пользу."
    ),
    "worship":     "Будь частью команды, которая ведёт людей в Божье присутствие!",
    "kids":        "Вложи своё сердце в будущее поколение!",
    "youth":       "Помогай молодым раскрывать свой потенциал и строить жизнь с Богом!",
    "media":       "Твори, вдохновляй и делись Божьим словом через современные медиа!",
    "welcome":     "Стань тем, кто встречает людей с теплом и любовью!",
    "hospitality": "Служи людям через простые, но очень важные вещи — еду, кофе и уют.",
}

# Для discover нет отделов — сразу показываем кнопку "Подать заявку"
DEPARTMENTS_BY_CATEGORY: Dict[str, List[str]] = {
    "worship": ["Singers", "Musicians"],
    "kids": ["Sunday school", "ICan (special kids)"],
    "youth": ["Chosen Gen", "Teens (Slavic)"],
    "media": ["Audio", "Live stream video", "Lights", "Production / Social", "Photography", "Graphic Design"],
    "welcome": ["Welcome Center", "Red Carpet", "Info Booth", "Ushers"],
    "hospitality": ["Coffee shop", "Kitchen"],
}

DEPT_DESCRIPTIONS_BY_CATEGORY: Dict[str, Dict[str, str]] = {
    # discover без отделов — описание выше
    "worship": {
        "Singers": "используй свой голос, чтобы вдохновлять и поклоняться.",
        "Musicians": "твои ноты и аккорды оживляют атмосферу хвалы.",
    },
    "kids": {
        "Sunday school": "помоги детям познавать Библию с радостью.",
        "ICan (special kids)": "будь светом и поддержкой для особенных детей.",
    },
    "youth": {
        "Chosen Gen": "поддержи новое поколение в вере и лидерстве.",
        "Teens (Slavic)": "будь рядом с подростками, помогая им идти Божьим путём.",
    },
    "media": {
        "Audio": "создай качественный звук для поклонения и проповеди.",
        "Live stream video": "помоги транслировать служение людям по всему миру.",
        "Lights": "добавь атмосферы и красоты через свет.",
        "Production / Social": "делись событиями церкви и вдохновляй онлайн.",
        "Photography": "запечатли живые моменты Божьей работы.",
        "Graphic Design": "используй творчество, чтобы донести послание.",
    },
    "welcome": {
        "Welcome Center": "будь первой улыбкой для гостей церкви.",
        "Red Carpet": "подари каждому ощущение праздника.",
        "Info Booth": "помоги найти ответы и почувствовать себя дома.",
        "Ushers": "создай атмосферу порядка и заботы во время служения.",
    },
    "hospitality": {
        "Coffee shop": "сделай чашку кофе местом общения и радости.",
        "Kitchen": "готовь с любовью и корми, как для семьи.",
    },
}


def build_category_description_text(category_key: str) -> str:
    title = CATEGORY_TITLES.get(category_key, "—")
    head = CATEGORY_HEADLINES.get(category_key, "")
    return f"{title}\n{head}"


def build_dept_description_text(category_key: str, department: str) -> str:
    cat_title = CATEGORY_TITLES.get(category_key, "—")
    head = CATEGORY_HEADLINES.get(category_key, "")
    desc = DEPT_DESCRIPTIONS_BY_CATEGORY.get(category_key, {}).get(department, "")
    top = f"{cat_title}\n{head}" if head else cat_title
    middle = f"• <b>{department}</b> — {desc}" if desc else f"• <b>{department}</b>"
    return f"{top}\n\n{middle}\n\nГотов(а) присоединиться? Нажми кнопку ниже 👇"

