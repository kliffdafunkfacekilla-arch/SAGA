# interaction_matrix.py

# Map (Power_Tag, Property_Tag/State_Tag) -> Outcome
INTERACTION_MATRIX = {
    # Power vs. Property Interactions
    ('Pyric', 'Flammable'): 'IGNITE',
    ('Kinetic', 'Brittle'): 'SHATTER',
    ('Volt', 'Conductive'): 'ELECTRIFY',
    
    # State Manipulation
    ('Cryo', 'Burning'): 'EXTINGUISH',
    ('Kinetic', 'Movable'): 'RELOCATE',
    ('Kinetic', 'Barricaded'): 'BREAK_BARRICADE',
    
    # Advanced Power Reactions
    ('Pyric', 'Cryo'): 'STEAM_EXPLOSION', # Creates AOE Hazard
    ('Volt', 'Aether'): 'MAGIC_SURGE',    # Amplifies spell effect
    ('Kinetic', 'Gravitic'): 'CRUSH'      # Massive damage to target
}

def map_action_to_power(action_type):
    """
    Maps standard system actions to Power Tags.
    """
    mapping = {
        'ATTACK': 'Kinetic',
        'COMBAT_TACTIC': 'Kinetic',
        'BARRICADE': 'Kinetic',
        'FLIP': 'Kinetic',
        'IGNITE': 'Pyric',
        'EXTINGUISH': 'Cryo',
        'GRAB': 'Kinetic',
        'SHATTER': 'Kinetic',
        'SURGE': 'Volt',
        'CHANNEL': 'Aether'
    }
    return mapping.get(action_type.upper(), 'Kinetic')

def check_interaction(power_tag, target_tags):
    """
    Checks if a power tag interacts with any of the target's tags.
    Returns the specific interaction result or 'DEFAULT'.
    """
    if not target_tags:
        return 'DEFAULT'
        
    for tag in target_tags:
        key = (power_tag, tag)
        if key in INTERACTION_MATRIX:
            return INTERACTION_MATRIX[key]
            
    return 'DEFAULT'
