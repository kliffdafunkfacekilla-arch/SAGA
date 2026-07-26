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

TIER_SCALING = {
    1: "Novice: Single target, touch or adjacent range. Minor effect.",
    4: "Adept: Up to 3 targets, 15ft range/arc. Moderate effect.",
    7: "Master: Up to 6 targets, 30ft area of effect, sustained duration.",
    10: "Divine: City-block scope, permanent environmental alteration, massive collateral damage."
}

SKILL_TRACKS = {
    # ==========================================
    # BODY STATS (Physical Manifestation)
    # ==========================================
    
    # --- MIGHT ---
    "Might_Offense": {"name": "The Berserker", "category": "Offense", "stat_bonus": "might", "stat_penalty": "reflexes", "description": "Heavy/Crushing weapons. Cleaving through targets and shattering armor."},
    "Might_Defense": {"name": "The Parrier", "category": "Defense", "stat_bonus": "might", "stat_penalty": "finesse", "description": "Deflecting heavy blows by actively striking the enemy's weapon away."},
    "Might_Magic": {"name": "School of Mass", "category": "Magic", "stat_bonus": "might", "stat_penalty": "logic", "description": "Manipulation of gravity, physical density, and kinetic force."},
    "Might_Utility": {"name": "Athletics", "category": "Utility", "stat_bonus": "might", "stat_penalty": "charm", "description": "Feats of raw strength, climbing, lifting, and breaking restraints."},

    # --- REFLEXES ---
    "Reflexes_Offense": {"name": "The Sniper", "category": "Offense", "stat_bonus": "reflexes", "stat_penalty": "fortitude", "description": "Bows/Thrown weapons. Extreme range and mobility-based skirmishing."},
    "Reflexes_Defense": {"name": "The Acrobat", "category": "Defense", "stat_bonus": "reflexes", "stat_penalty": "endurance", "description": "Unarmored Evasion. Dodging attacks completely and repositioning freely."},
    "Reflexes_Magic": {"name": "School of Motus", "category": "Magic", "stat_bonus": "reflexes", "stat_penalty": "willpower", "description": "Control over velocity, acceleration, and kinetic momentum."},
    "Reflexes_Utility": {"name": "Stealth", "category": "Utility", "stat_bonus": "reflexes", "stat_penalty": "might", "description": "Moving silently, hiding in shadows, and physical acrobatics."},

    # --- FINESSE ---
    "Finesse_Offense": {"name": "The Duelist", "category": "Offense", "stat_bonus": "finesse", "stat_penalty": "vitality", "description": "Rapiers/Light Blades. Precision strikes and armor penetration."},
    "Finesse_Defense": {"name": "The Riposte", "category": "Defense", "stat_bonus": "finesse", "stat_penalty": "fortitude", "description": "Counter-attacking. Punishing enemies who miss their strikes."},
    "Finesse_Magic": {"name": "School of Flux", "category": "Magic", "stat_bonus": "finesse", "stat_penalty": "endurance", "description": "Phase shifting, liquid manipulation, and matter alteration."},
    "Finesse_Utility": {"name": "Sleight of Hand", "category": "Utility", "stat_bonus": "finesse", "stat_penalty": "might", "description": "Picking locks, disarming mechanisms, and pickpocketing."},

    # --- ENDURANCE ---
    "Endurance_Offense": {"name": "The Phalanx", "category": "Offense", "stat_bonus": "endurance", "stat_penalty": "finesse", "description": "Shield-bashing, shoving, and utilizing heavy polearms to control space."},
    "Endurance_Defense": {"name": "The Ironclad", "category": "Defense", "stat_bonus": "endurance", "stat_penalty": "reflexes", "description": "Medium Armor mastery. Reducing stamina drain from prolonged fights."},
    "Endurance_Magic": {"name": "School of Ordo", "category": "Magic", "stat_bonus": "endurance", "stat_penalty": "intuition", "description": "Stasis, preservation, and nullification of dynamic forces."},
    "Endurance_Utility": {"name": "Survival", "category": "Utility", "stat_bonus": "endurance", "stat_penalty": "charm", "description": "Foraging, tracking weather, and enduring extreme environmental hazards."},

    # --- FORTITUDE ---
    "Fortitude_Offense": {"name": "The Juggernaut", "category": "Offense", "stat_bonus": "fortitude", "stat_penalty": "reflexes", "description": "Unarmed/Slam attacks. Using raw mass to trample and crush enemies."},
    "Fortitude_Defense": {"name": "The Sentinel", "category": "Defense", "stat_bonus": "fortitude", "stat_penalty": "awareness", "description": "Heavy Armor/Carapace. Passively absorbing massive damage thresholds."},
    "Fortitude_Magic": {"name": "School of Lex", "category": "Magic", "stat_bonus": "fortitude", "stat_penalty": "intuition", "description": "The imposition of absolute rules and unbreakable physical barriers."},
    "Fortitude_Utility": {"name": "Labor", "category": "Utility", "stat_bonus": "fortitude", "stat_penalty": "logic", "description": "Carrying massive loads, ignoring exhaustion, and physical resistance to pain."},

    # --- VITALITY ---
    "Vitality_Offense": {"name": "The Blood-Hunter", "category": "Offense", "stat_bonus": "vitality", "stat_penalty": "knowledge", "description": "Sacrificing one's own HP to inflict massive, savage damage spikes."},
    "Vitality_Defense": {"name": "The Regenerator", "category": "Defense", "stat_bonus": "vitality", "stat_penalty": "logic", "description": "Rapid biological healing. Clearing trauma tokens quickly during combat."},
    "Vitality_Magic": {"name": "School of Vita", "category": "Magic", "stat_bonus": "vitality", "stat_penalty": "willpower", "description": "Biomancy, flesh-warping, and the manipulation of life-force."},
    "Vitality_Utility": {"name": "Husbandry", "category": "Utility", "stat_bonus": "vitality", "stat_penalty": "charm", "description": "Taming, handling, and understanding the mutated beasts of the wastes."},

    # ==========================================
    # MIND STATS (Mental Manifestation)
    # ==========================================

    # --- LOGIC ---
    "Logic_Offense": {"name": "The Tactician", "category": "Offense", "stat_bonus": "logic", "stat_penalty": "intuition", "description": "Traps and Explosives. Setting up calculated kill-zones."},
    "Logic_Defense": {"name": "The Strategist", "category": "Defense", "stat_bonus": "logic", "stat_penalty": "vitality", "description": "Predictive positioning. Using geometry to force disadvantage on attackers."},
    "Logic_Magic": {"name": "School of Ratio", "category": "Magic", "stat_bonus": "logic", "stat_penalty": "charm", "description": "Geometric constructs, pure calculation, and spatial distortion."},
    "Logic_Utility": {"name": "Engineering", "category": "Utility", "stat_bonus": "logic", "stat_penalty": "endurance", "description": "Crafting, repairing machinery, and understanding complex architecture."},

    # --- KNOWLEDGE ---
    "Knowledge_Offense": {"name": "The Alchemist", "category": "Offense", "stat_bonus": "knowledge", "stat_penalty": "vitality", "description": "Toxic Vials and Acids. Inflicting continuous trauma tokens and debuffs."},
    "Knowledge_Defense": {"name": "The Artificer", "category": "Defense", "stat_bonus": "knowledge", "stat_penalty": "reflexes", "description": "Deployable cover. Throwing down temporary barricades or smoke screens."},
    "Knowledge_Magic": {"name": "School of Nexus", "category": "Magic", "stat_bonus": "knowledge", "stat_penalty": "might", "description": "Portals, summoning, and planar gates."},
    "Knowledge_Utility": {"name": "Medicine", "category": "Utility", "stat_bonus": "knowledge", "stat_penalty": "fortitude", "description": "Anatomy, biological stabilization, and crafting remedies."},

    # --- AWARENESS ---
    "Awareness_Offense": {"name": "The Overwatch", "category": "Offense", "stat_bonus": "awareness", "stat_penalty": "willpower", "description": "Ambushes. Gaining massive damage bonuses against unalerted targets."},
    "Awareness_Defense": {"name": "The Precog", "category": "Defense", "stat_bonus": "awareness", "stat_penalty": "endurance", "description": "Unflankable. Cannot be surprised or ambushed by hidden enemies."},
    "Awareness_Magic": {"name": "School of Aura", "category": "Magic", "stat_bonus": "awareness", "stat_penalty": "logic", "description": "True sight, divination, and energy reading."},
    "Awareness_Utility": {"name": "Scouting", "category": "Utility", "stat_bonus": "awareness", "stat_penalty": "charm", "description": "Tracking footprints, noticing hidden compartments, and heightened senses."},

    # --- INTUITION ---
    "Intuition_Offense": {"name": "The Opportunist", "category": "Offense", "stat_bonus": "intuition", "stat_penalty": "logic", "description": "Dirty fighting. Exploiting environmental weaknesses or attacking blinded foes."},
    "Intuition_Defense": {"name": "The Survivor", "category": "Defense", "stat_bonus": "intuition", "stat_penalty": "knowledge", "description": "Luck-based evasion. Narrowly escaping lethal blows through pure instinct."},
    "Intuition_Magic": {"name": "School of Omen", "category": "Magic", "stat_bonus": "intuition", "stat_penalty": "fortitude", "description": "Probability manipulation, fate, and luck weaving."},
    "Intuition_Utility": {"name": "Scavenging", "category": "Utility", "stat_bonus": "intuition", "stat_penalty": "willpower", "description": "Streetwise bartering, finding valuable salvage, and reading people."},

    # --- WILLPOWER ---
    "Willpower_Offense": {"name": "The Vanguard", "category": "Offense", "stat_bonus": "willpower", "stat_penalty": "awareness", "description": "Fear-inducing strikes. Physically damages while crushing enemy Composure."},
    "Willpower_Defense": {"name": "The Resolve", "category": "Defense", "stat_bonus": "willpower", "stat_penalty": "finesse", "description": "Ignoring pain. Fighting at full capacity even while critically wounded."},
    "Willpower_Magic": {"name": "School of Anumis", "category": "Magic", "stat_bonus": "willpower", "stat_penalty": "vitality", "description": "Telepathy, mind domination, and psychic force."},
    "Willpower_Utility": {"name": "Intimidation", "category": "Utility", "stat_bonus": "willpower", "stat_penalty": "charm", "description": "Interrogation, resisting coercion, and breaking an NPC's resolve."},

    # --- CHARM ---
    "Charm_Offense": {"name": "The Warlord", "category": "Offense", "stat_bonus": "charm", "stat_penalty": "willpower", "description": "Companion Directives. Commanding pets or mercenaries in coordinated strikes."},
    "Charm_Defense": {"name": "The Diplomat", "category": "Defense", "stat_bonus": "charm", "stat_penalty": "fortitude", "description": "Misdirection. Forcing an enemy to target a different ally or hesitate."},
    "Charm_Magic": {"name": "School of Lux", "category": "Magic", "stat_bonus": "charm", "stat_penalty": "logic", "description": "Radiance, illusion, blinding presence, and hard-light constructs."},
    "Charm_Utility": {"name": "Persuasion", "category": "Utility", "stat_bonus": "charm", "stat_penalty": "endurance", "description": "De-escalation, diplomacy, and gathering information through social grace."}
}
