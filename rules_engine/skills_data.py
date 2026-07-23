# rules_engine/skills_data.py

# Redesigned for the ECS Tag System and Zonal Map
# Skills now act as Delivery Systems for Tags and Zone Manipulators.

PASSIVE_HARDWARE = {
    "Assault": {
        "T1": {
            "name": "Drive Back",
            "type": "ACTIVE",
            "cost": {"stamina": 1},
            "range": "Melee",
            "tags": ["impact", "force"]
        },
        "T3": {
            "name": "Cleave",
            "type": "ACTIVE",
            "cost": {"stamina": 2},
            "range": "Melee",
            "tags": ["slashing", "brutal"]
        }
    }
}

SUBCONSCIOUS_MAGIC = {
    "The Wrangler": {
        "T1": {
            "name": "Orbital Drop",
            "type": "ACTIVE",
            "cost": {"stamina": 3, "focus": 2},
            "range": "Melee",
            "tags": ["impact", "force", "brutal"]
        }
    },
    "The Spark": {
        "T1": {
            "name": "Thunderstep",
            "type": "ACTIVE",
            "cost": {"stamina": 1, "focus": 2},
            "range": "Far",
            "tags": ["shock", "force"],
            "zone_shift": "Melee" # Instantly moves the actor to Melee
        }
    }
}

ANOMALIES = {
    "Nexus": {
        "T1": {
            "name": "Frost Nova",
            "type": "ACTIVE",
            "cost": {"stamina": 1, "focus": 3},
            "range": "Melee",
            "tags": ["frost"] # Hits everything in the zone
        },
        "T2": {
            "name": "Venom Spit",
            "type": "ACTIVE",
            "cost": {"stamina": 1, "focus": 1},
            "range": "Close",
            "tags": ["poison", "liquid"]
        },
        "T3": {
            "name": "Chain Lightning",
            "type": "ACTIVE",
            "cost": {"stamina": 2, "focus": 4},
            "range": "Close",
            "tags": ["shock", "force"]
        }
    }
}
