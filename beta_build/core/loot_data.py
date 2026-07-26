"""
loot_data.py
Defines the procedural loot drop pools for enemies.
"""

LOOT_TABLES = {
    "scrap_bandit": [
        {"name": "Rusted Pipe", "item_type": "weapon", "stat_type": "might", "armor_mod": 1, "tags": ["blunt", "heavy"]},
        {"name": "Boiled Leather Vest", "item_type": "body", "stat_type": "endurance", "armor_mod": 1, "tags": ["worn"]}
    ],
    "occult_mutant": [
        {"name": "Carved Bone Charm", "item_type": "necklace", "stat_type": "willpower", "armor_mod": 2, "tags": ["occult", "unsettling"]},
        {"name": "Vial of Black Bile", "item_type": "consumable", "stat_type": "none", "armor_mod": 0, "tags": ["toxic", "healing"]}
    ],
    "default": [
        {"name": "Scrap Metal", "item_type": "junk", "stat_type": "none", "armor_mod": 0, "tags": ["scrap"]}
    ]
}
