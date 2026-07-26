# rules_engine/chassis_data.py

KINGDOMS = ["Mammals", "Reptiles & Amphibians", "Avians", "Aquatics", "Insects & Arthropods", "Plants & Myconids"]

SUB_TYPES = ["T0 (Origin)", "T1 (Balancer)", "T2 (Heavy)", "T3 (Predator)", "T4 (Specialist)"]

# Format: BASE_STATS[Kingdom][Sub-Type] = {stat: value}
BASE_STATS = {
    "Mammals": {
        "T0 (Origin)": {"might":3, "endurance":4, "finesse":5, "reflex":2, "vitality":3, "fortitude":1, "knowledge":5, "logic":1, "awareness":2, "intuition":3, "charm":4, "willpower":3},
        "T1 (Balancer)": {"might":3, "endurance":3, "finesse":4, "reflex":3, "vitality":3, "fortitude":2, "knowledge":4, "logic":2, "awareness":3, "intuition":3, "charm":3, "willpower":3},
        "T2 (Heavy)": {"might":4, "endurance":4, "finesse":4, "reflex":2, "vitality":2, "fortitude":2, "knowledge":4, "logic":2, "awareness":2, "intuition":2, "charm":4, "willpower":4},
        "T3 (Predator)": {"might":4, "endurance":5, "finesse":5, "reflex":1, "vitality":2, "fortitude":1, "knowledge":5, "logic":1, "awareness":1, "intuition":2, "charm":5, "willpower":4},
        "T4 (Specialist)": {"might":2, "endurance":4, "finesse":5, "reflex":4, "vitality":2, "fortitude":1, "knowledge":5, "logic":1, "awareness":4, "intuition":2, "charm":4, "willpower":2}
    },
    "Reptiles & Amphibians": {
        "T0 (Origin)": {"might":3, "endurance":2, "finesse":1, "reflex":4, "vitality":3, "fortitude":5, "knowledge":3, "logic":5, "awareness":1, "intuition":4, "charm":3, "willpower":2},
        "T1 (Balancer)": {"might":3, "endurance":3, "finesse":2, "reflex":3, "vitality":3, "fortitude":4, "knowledge":3, "logic":4, "awareness":2, "intuition":3, "charm":3, "willpower":3},
        "T2 (Heavy)": {"might":4, "endurance":2, "finesse":2, "reflex":4, "vitality":2, "fortitude":4, "knowledge":2, "logic":4, "awareness":2, "intuition":4, "charm":4, "willpower":2},
        "T3 (Predator)": {"might":4, "endurance":1, "finesse":1, "reflex":5, "vitality":2, "fortitude":5, "knowledge":2, "logic":5, "awareness":1, "intuition":5, "charm":4, "willpower":1},
        "T4 (Specialist)": {"might":2, "endurance":4, "finesse":1, "reflex":4, "vitality":2, "fortitude":5, "knowledge":2, "logic":5, "awareness":1, "intuition":4, "charm":2, "willpower":4}
    },
    "Avians": {
        "T0 (Origin)": {"might":1, "endurance":3, "finesse":3, "reflex":5, "vitality":4, "fortitude":2, "knowledge":4, "logic":2, "awareness":5, "intuition":1, "charm":3, "willpower":3},
        "T1 (Balancer)": {"might":2, "endurance":3, "finesse":3, "reflex":4, "vitality":3, "fortitude":3, "knowledge":3, "logic":3, "awareness":4, "intuition":2, "charm":3, "willpower":3},
        "T2 (Heavy)": {"might":2, "endurance":4, "finesse":2, "reflex":4, "vitality":4, "fortitude":2, "knowledge":4, "logic":2, "awareness":4, "intuition":2, "charm":4, "willpower":2},
        "T3 (Predator)": {"might":1, "endurance":2, "finesse":4, "reflex":5, "vitality":5, "fortitude":1, "knowledge":5, "logic":1, "awareness":5, "intuition":1, "charm":2, "willpower":4},
        "T4 (Specialist)": {"might":1, "endurance":2, "finesse":2, "reflex":5, "vitality":4, "fortitude":4, "knowledge":4, "logic":4, "awareness":5, "intuition":1, "charm":2, "willpower":2}
    },
    "Aquatics": {
        "T0 (Origin)": {"might":2, "endurance":5, "finesse":4, "reflex":3, "vitality":1, "fortitude":3, "knowledge":2, "logic":3, "awareness":4, "intuition":3, "charm":1, "willpower":5},
        "T1 (Balancer)": {"might":3, "endurance":4, "finesse":3, "reflex":3, "vitality":2, "fortitude":3, "knowledge":3, "logic":3, "awareness":3, "intuition":3, "charm":2, "willpower":4},
        "T2 (Heavy)": {"might":2, "endurance":4, "finesse":4, "reflex":2, "vitality":2, "fortitude":4, "knowledge":2, "logic":4, "awareness":4, "intuition":2, "charm":2, "willpower":4},
        "T3 (Predator)": {"might":1, "endurance":5, "finesse":5, "reflex":4, "vitality":1, "fortitude":2, "knowledge":1, "logic":2, "awareness":5, "intuition":4, "charm":1, "willpower":5},
        "T4 (Specialist)": {"might":4, "endurance":5, "finesse":4, "reflex":2, "vitality":1, "fortitude":2, "knowledge":4, "logic":2, "awareness":4, "intuition":2, "charm":1, "willpower":5}
    },
    "Insects & Arthropods": {
        "T0 (Origin)": {"might":5, "endurance":1, "finesse":3, "reflex":3, "vitality":2, "fortitude":4, "knowledge":3, "logic":4, "awareness":3, "intuition":5, "charm":2, "willpower":1},
        "T1 (Balancer)": {"might":4, "endurance":2, "finesse":3, "reflex":3, "vitality":3, "fortitude":3, "knowledge":3, "logic":3, "awareness":3, "intuition":4, "charm":3, "willpower":2},
        "T2 (Heavy)": {"might":4, "endurance":2, "finesse":4, "reflex":2, "vitality":2, "fortitude":4, "knowledge":2, "logic":4, "awareness":4, "intuition":4, "charm":2, "willpower":2},
        "T3 (Predator)": {"might":5, "endurance":1, "finesse":2, "reflex":4, "vitality":1, "fortitude":5, "knowledge":2, "logic":5, "awareness":4, "intuition":5, "charm":1, "willpower":1},
        "T4 (Specialist)": {"might":5, "endurance":1, "finesse":2, "reflex":2, "vitality":4, "fortitude":4, "knowledge":2, "logic":4, "awareness":2, "intuition":5, "charm":4, "willpower":1}
    },
    "Plants & Myconids": {
        "T0 (Origin)": {"might":4, "endurance":3, "finesse":2, "reflex":1, "vitality":5, "fortitude":3, "knowledge":1, "logic":3, "awareness":3, "intuition":2, "charm":5, "willpower":4},
        "T1 (Balancer)": {"might":3, "endurance":3, "finesse":3, "reflex":2, "vitality":4, "fortitude":3, "knowledge":2, "logic":3, "awareness":3, "intuition":3, "charm":4, "willpower":3},
        "T2 (Heavy)": {"might":4, "endurance":4, "finesse":2, "reflex":2, "vitality":4, "fortitude":2, "knowledge":2, "logic":2, "awareness":4, "intuition":2, "charm":4, "willpower":4},
        "T3 (Predator)": {"might":5, "endurance":2, "finesse":1, "reflex":1, "vitality":5, "fortitude":4, "knowledge":1, "logic":2, "awareness":4, "intuition":1, "charm":5, "willpower":5},
        "T4 (Specialist)": {"might":4, "endurance":2, "finesse":4, "reflex":1, "vitality":5, "fortitude":2, "knowledge":1, "logic":2, "awareness":2, "intuition":4, "charm":5, "willpower":4}
    }
}

ORIGINS = {
    "Mammals": {
        "T2 (Heavy)": ["Horses", "Zebras", "Donkeys", "Cattle/Sheep", "Hippos", "Bears"],
        "T3 (Predator)": ["Deer/Elk", "Wolves", "Coyotes", "Foxes", "Big Cats", "Otters"],
        "T4 (Specialist)": ["Rats", "Mice", "Beavers", "Porcupines", "Flying Squirrels", "Bats"],
        "T1 (Balancer)": ["Monkeys", "Sloths", "Red Pandas", "Raccoons", "Opossums", "Pangolins"],
        "T0 (Origin)": ["Mammal-Standard"]
    },
    "Reptiles & Amphibians": {
        "T2 (Heavy)": ["Stone-Scales", "Crocodiles", "Alligators", "Komodos", "Toad Barons", "Resonance-Basilisks"],
        "T3 (Predator)": ["Serpentes", "Pit-Vipers", "Monitors", "Aquatic Frogs", "Salamander-Lizards", "Crystal-Serpents"],
        "T4 (Specialist)": ["Geckoes", "Gliding Skinks", "Ranidae", "Tree Frogs", "Shovel-Snouts", "Glass-Skinks"],
        "T1 (Balancer)": ["Frilled-Lizards", "Newt-Kin", "Mud Frogs", "Echo-Toads", "Desert Iguanas", "Chameleons"],
        "T0 (Origin)": ["Reptile-Standard"]
    },
    "Avians": {
        "T2 (Heavy)": ["Penguins", "Chickens", "Ostriches/Emus", "Cassowaries", "Turkeys", "Geese"],
        "T3 (Predator)": ["Owls", "Eagles", "Hawks", "Falcons", "Vultures/Condors", "Ospreys"],
        "T4 (Specialist)": ["Finches/Sparrows", "Hummingbirds", "Nightingales", "Mockingbirds", "Lyrebirds", "Magpies"],
        "T1 (Balancer)": ["Ducks", "Ravens/Crows", "Swans", "Parrots/Macaws", "Pigeons/Doves", "Gulls/Albatross"],
        "T0 (Origin)": ["Avian-Standard"]
    },
    "Aquatics": {
        "T2 (Heavy)": ["Walruses", "Orcas", "Giant Crabs", "Lobsters", "Elephant Seals", "Manatees"],
        "T3 (Predator)": ["Great White Sharks", "Hammerhead Sharks", "Barracudas", "Moray Eels", "Tiger Sharks", "Marlin/Swordfish"],
        "T4 (Specialist)": ["Seahorses", "Anglerfish", "Lionfish", "Mantis Shrimp", "Pufferfish", "Flounder/Flatfish"],
        "T1 (Balancer)": ["Koi/Carp", "Salmon/Trout", "Seals/Sea Lions", "Dolphins", "Manta Rays", "Catfish"],
        "T0 (Origin)": ["Aquatic-Standard"]
    },
    "Insects & Arthropods": {
        "T2 (Heavy)": ["Goliath/Rhino Beetles", "Pill Bugs", "Cockroaches", "Stag Beetles", "Soldier Ants", "Ironclad Beetles"],
        "T3 (Predator)": ["Praying Mantises", "Wasps", "Hornets", "Tarantulas", "Assassin Bugs", "Centipedes"],
        "T4 (Specialist)": ["Honey Bees", "Orb-Weaver Spiders", "Caterpillars", "Trapdoor Spiders", "Mosquitoes", "Fleas"],
        "T1 (Balancer)": ["Butterflies", "Moths", "Grasshoppers", "Leafcutter Ants", "Fireflies", "Stick Insects"],
        "T0 (Origin)": ["Insect-Standard"]
    },
    "Plants & Myconids": {
        "T2 (Heavy)": ["Oaks", "Redwoods", "Willows", "Mangroves", "Pines", "Baobabs"],
        "T3 (Predator)": ["Strangler Figs", "Kudzu", "Blood-Briars", "Ivy/Creepers", "Pitcher-Vines", "Morning Glories"],
        "T4 (Specialist)": ["Truffles", "Death Caps", "Ink Caps", "Bioluminescent Mycena", "Puffballs", "Cordyceps"],
        "T1 (Balancer)": ["Roses", "Lotus", "Nightshades", "Orchids", "Sunflowers", "Tumbleweeds"],
        "T0 (Origin)": ["Plant-Standard"]
    }
}

SKILL_TRACKS = {
    # --- MIGHT ---
    "Heavy_Weaponry": {"name": "Heavy Weaponry", "category": "Offense", "stat_bonus": "might", "stat_penalty": "reflexes", "description": "Utilizes massive weapons to crush armor and bone."},
    "Bracing": {"name": "Bracing", "category": "Defense", "stat_bonus": "might", "stat_penalty": "finesse", "description": "Uses sheer physical mass to stop attacks dead in their tracks."},
    "Athletics": {"name": "Athletics", "category": "Utility", "stat_bonus": "might", "stat_penalty": "knowledge", "description": "Feats of raw strength, climbing, and lifting."},
    "School_of_Mass": {"name": "Mass", "category": "Magic", "stat_bonus": "might", "stat_penalty": "finesse", "description": "Manipulation of gravity and physical density."},
    
    # --- REFLEXES ---
    "Ranged_Weaponry": {"name": "Ranged Weaponry", "category": "Offense", "stat_bonus": "reflexes", "stat_penalty": "fortitude", "description": "Mastery of bows, thrown weapons, and quick shots."},
    "Unarmored_Evasion": {"name": "Evasion", "category": "Defense", "stat_bonus": "reflexes", "stat_penalty": "endurance", "description": "Dodging attacks through pure speed and flexibility."},
    "Acrobatics": {"name": "Acrobatics", "category": "Utility", "stat_bonus": "reflexes", "stat_penalty": "logic", "description": "Tumbling, balancing, and performing complex maneuvers."},
    "School_of_Motus": {"name": "Motus", "category": "Magic", "stat_bonus": "reflexes", "stat_penalty": "vitality", "description": "Control over velocity, acceleration, and kinetic energy."},
    
    # --- FINESSE ---
    "Precision_Weaponry": {"name": "Precision Weaponry", "category": "Offense", "stat_bonus": "finesse", "stat_penalty": "might", "description": "Surgical strikes using daggers, rapiers, and firearms."},
    "Parrying": {"name": "Parrying", "category": "Defense", "stat_bonus": "finesse", "stat_penalty": "fortitude", "description": "Deflecting incoming attacks with precision timing."},
    "Sleight_of_Hand": {"name": "Sleight of Hand", "category": "Utility", "stat_bonus": "finesse", "stat_penalty": "willpower", "description": "Picking locks, disarming small traps, and theft."},
    "School_of_Flux": {"name": "Flux", "category": "Magic", "stat_bonus": "finesse", "stat_penalty": "endurance", "description": "Phase shifting, liquids, and alteration."},
    
    # --- ENDURANCE ---
    "Brawling": {"name": "Brawling", "category": "Offense", "stat_bonus": "endurance", "stat_penalty": "finesse", "description": "Unarmed combat built on outlasting the opponent."},
    "Medium_Armor": {"name": "Medium Armor", "category": "Defense", "stat_bonus": "endurance", "stat_penalty": "reflexes", "description": "Mastery of chainmail and thick hides."},
    "Survival": {"name": "Survival", "category": "Utility", "stat_bonus": "endurance", "stat_penalty": "charm", "description": "Enduring harsh environments and foraging."},
    "School_of_Ordo": {"name": "Ordo", "category": "Magic", "stat_bonus": "endurance", "stat_penalty": "intuition", "description": "Stasis, preservation, and nullification of chaos."},
    
    # --- FORTITUDE ---
    "Shield_Bashing": {"name": "Shield Bashing", "category": "Offense", "stat_bonus": "fortitude", "stat_penalty": "reflexes", "description": "Using heavy shields offensively to control space."},
    "Heavy_Armor": {"name": "Ironclad", "category": "Defense", "stat_bonus": "fortitude", "stat_penalty": "awareness", "description": "Mastery of heavy plating and natural carapaces to absorb blows."},
    "Intimidation": {"name": "Intimidation", "category": "Utility", "stat_bonus": "fortitude", "stat_penalty": "charm", "description": "Projecting an aura of undeniable physical threat."},
    "School_of_Lex": {"name": "Lex", "category": "Magic", "stat_bonus": "fortitude", "stat_penalty": "intuition", "description": "The imposition of absolute rules and unbreakable physical barriers."},
    
    # --- VITALITY ---
    "Blood_Sacrifice": {"name": "Blood Sacrifice", "category": "Offense", "stat_bonus": "vitality", "stat_penalty": "logic", "description": "Expending one's own lifeforce to empower strikes."},
    "Regeneration": {"name": "Regeneration", "category": "Defense", "stat_bonus": "vitality", "stat_penalty": "knowledge", "description": "Rapidly closing wounds during the heat of battle."},
    "Biological_Resistance": {"name": "Biological Resistance", "category": "Utility", "stat_bonus": "vitality", "stat_penalty": "awareness", "description": "Natural immunity to poisons, diseases, and toxins."},
    "School_of_Vita": {"name": "Vita", "category": "Magic", "stat_bonus": "vitality", "stat_penalty": "logic", "description": "Biomancy, healing, and flesh-warping."},
    
    # --- LOGIC ---
    "Tactical_Gadgets": {"name": "Tactical Gadgets", "category": "Offense", "stat_bonus": "logic", "stat_penalty": "vitality", "description": "Deploying traps, bombs, and mechanical devices."},
    "Trap_Disarming": {"name": "Trap Disarming", "category": "Defense", "stat_bonus": "logic", "stat_penalty": "might", "description": "Methodical deconstruction of hazards and explosives."},
    "Engineering": {"name": "Engineering", "category": "Utility", "stat_bonus": "logic", "stat_penalty": "charm", "description": "Building, repairing, and analyzing machinery."},
    "School_of_Ratio": {"name": "Ratio", "category": "Magic", "stat_bonus": "logic", "stat_penalty": "intuition", "description": "Geometric constructs and pure calculation."},
    
    # --- KNOWLEDGE ---
    "Rune_Strikes": {"name": "Rune Strikes", "category": "Offense", "stat_bonus": "knowledge", "stat_penalty": "might", "description": "Using ancient inscribed runes to detonate elements."},
    "Counter_Lore": {"name": "Counter Lore", "category": "Defense", "stat_bonus": "knowledge", "stat_penalty": "fortitude", "description": "Identifying and unravelling enemy techniques."},
    "Artifact_Lore": {"name": "Artifact Lore", "category": "Utility", "stat_bonus": "knowledge", "stat_penalty": "endurance", "description": "Identifying artifacts, reading ancient texts, and historical knowledge."},
    "School_of_Nexus": {"name": "Nexus", "category": "Magic", "stat_bonus": "knowledge", "stat_penalty": "awareness", "description": "Portals, summoning, and planar gates."},
    
    # --- AWARENESS ---
    "Sniper": {"name": "Sniper", "category": "Offense", "stat_bonus": "awareness", "stat_penalty": "fortitude", "description": "Exploiting blind spots for massive ambush damage."},
    "Precognitive_Defense": {"name": "Precognitive Defense", "category": "Defense", "stat_bonus": "awareness", "stat_penalty": "vitality", "description": "Sensing ambushes and predicting trajectories."},
    "Tracking": {"name": "Tracking", "category": "Utility", "stat_bonus": "awareness", "stat_penalty": "logic", "description": "Following trails, spotting hidden objects, and acute senses."},
    "School_of_Aura": {"name": "Aura", "category": "Magic", "stat_bonus": "awareness", "stat_penalty": "endurance", "description": "True sight, divination, and energy reading."},
    
    # --- INTUITION ---
    "Improvised_Weapons": {"name": "Improvised Weapons", "category": "Offense", "stat_bonus": "intuition", "stat_penalty": "logic", "description": "Using the environment and unpredictable tactics to strike."},
    "Danger_Sense": {"name": "Danger Sense", "category": "Defense", "stat_bonus": "intuition", "stat_penalty": "knowledge", "description": "A gut feeling that naturally guides you away from harm."},
    "Insight": {"name": "Insight", "category": "Utility", "stat_bonus": "intuition", "stat_penalty": "willpower", "description": "Reading emotions, sensing lies, and street-smarts."},
    "School_of_Omen": {"name": "Omen", "category": "Magic", "stat_bonus": "intuition", "stat_penalty": "logic", "description": "Probability manipulation, fate, and luck."},
    
    # --- WILLPOWER ---
    "Force_of_Will": {"name": "Force of Will", "category": "Offense", "stat_bonus": "willpower", "stat_penalty": "finesse", "description": "Projecting sheer force of personality to stagger foes."},
    "Mental_Resistance": {"name": "Mental Resistance", "category": "Defense", "stat_bonus": "willpower", "stat_penalty": "reflexes", "description": "Resisting fear, mind control, and illusions."},
    "Interrogation": {"name": "Interrogation", "category": "Utility", "stat_bonus": "willpower", "stat_penalty": "charm", "description": "Breaking down suspects and forcing the truth."},
    "School_of_Anumis": {"name": "Anumis", "category": "Magic", "stat_bonus": "willpower", "stat_penalty": "vitality", "description": "Telepathy, mind domination, and psychic force."},
    
    # --- CHARM ---
    "Commands": {"name": "Commands", "category": "Offense", "stat_bonus": "charm", "stat_penalty": "endurance", "description": "Directing companions or intimidating enemies into submission."},
    "Distraction": {"name": "Distraction", "category": "Defense", "stat_bonus": "charm", "stat_penalty": "awareness", "description": "Using feints and banter to throw enemies off-balance."},
    "Negotiation": {"name": "Negotiation", "category": "Utility", "stat_bonus": "charm", "stat_penalty": "fortitude", "description": "Bartering, diplomacy, and persuasion."},
    "School_of_Lux": {"name": "Lux", "category": "Magic", "stat_bonus": "charm", "stat_penalty": "knowledge", "description": "Radiance, illusion, and blinding presence."}
}

TIER_SCALING = {
    1: "Novice: Single target, touch or adjacent range. Minor effect.",
    4: "Adept: Up to 3 targets, 15ft range/arc. Moderate effect.",
    7: "Master: Up to 6 targets, 30ft area of effect, sustained duration.",
    10: "Divine: City-block scope, permanent environmental alteration, massive collateral damage."
}
