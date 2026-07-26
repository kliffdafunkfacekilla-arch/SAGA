"""
skills_data.py
Contains the massive B.R.U.T.A.L. Engine skill dictionary for use by the ActionResolver and AIDirector.
"""

SKILL_TRACKS = {
    "the_ghost": {
        "name": "The Ghost",
        "category": "archetype",
        "base_stat": "reflex",
        "description": "Masters of kinetic speed, dual-wielding, light blades, and absolute evasion.",
        "skills": {
            # Branch A: The Breaker
            "flurry": {
                "name": "Flurry",
                "stamina_cost": 1,
                "mechanic_tags": ["dual_wield", "minor_injury"],
                "director_flavor": "The character blurs, executing a blistering secondary strike with their off-hand weapon in the same split second."
            },
            "hamstring": {
                "name": "Hamstring",
                "stamina_cost": 0,
                "mechanic_tags": ["move_beat_drain", "leg_target"],
                "director_flavor": "A precision slice to the tendons drops the enemy's mobility, immediately crippling their movement."
            },
            "kinetic_throw": {
                "name": "Kinetic Throw",
                "stamina_cost": 0,
                "mechanic_tags": ["ranged", "boomerang"],
                "director_flavor": "The character hurls a light blade that ricochets violently off the target and snaps perfectly back into their awaiting hand."
            },
            "a_thousand_cuts": {
                "name": "A Thousand Cuts",
                "stamina_cost": 0,
                "mechanic_tags": ["momentum", "upgrade_injury"],
                "director_flavor": "Riding the kinetic momentum of the first strike, the second blade bites far deeper, tearing open a massive wound."
            },
            "sonic_strike": {
                "name": "Sonic Strike",
                "focus_cost": 1,
                "mechanic_tags": ["ignore_armor", "deafen", "composure_damage"],
                "director_flavor": "The blade is swung fast enough to break the sound barrier. A deafening crack shatters the target's eardrums and rips right through their armor."
            },
            "blink_step": {
                "name": "Blink Step",
                "stamina_cost": 1,
                "move_cost": 1,
                "mechanic_tags": ["teleport_strike", "close_distance"],
                "director_flavor": "The character vibrates out of focus and instantly materializes next to the enemy, striking in the exact same fluid motion."
            },
            "arterial_slash": {
                "name": "Arterial Slash",
                "stamina_cost": 0,
                "mechanic_tags": ["bleed_dot", "major_injury"],
                "director_flavor": "A calculated slice finds the seams in the plating, severing a major artery. A catastrophic spray of blood begins draining the enemy's life force."
            },
            "ricochet_arc": {
                "name": "Ricochet Arc",
                "stamina_cost": 0,
                "mechanic_tags": ["aoe", "bouncing"],
                "director_flavor": "The thrown weapon bounces between multiple targets at impossible speeds, slicing through the cluster before returning."
            },
            "vibrating_edge": {
                "name": "Vibrating Edge",
                "stamina_cost": 0,
                "mechanic_tags": ["critical_hit", "sever_limb"],
                "director_flavor": "The weapon vibrates at a molecular frequency, acting as a hyper-saw that effortlessly severs the enemy's limb."
            },
            "the_blender": {
                "name": "The Blender",
                "stamina_cost": 99, # All remaining
                "mechanic_tags": ["aoe_burst", "major_injury", "capstone"],
                "director_flavor": "The character becomes a localized kinetic storm of blades, vibrating at terminal velocity and shredding everything in the zone."
            },
            # Branch B: The Bastion
            "blur": {
                "name": "Blur",
                "passive": True,
                "director_flavor": "The character naturally vibrates, their edges constantly out of focus to the naked eye."
            },
            "kinetic_dampening": {
                "name": "Kinetic Dampening",
                "stamina_cost": 0,
                "mechanic_tags": ["downgrade_injury"],
                "director_flavor": "At the exact millisecond of impact, the character vibrates to bleed off the incoming kinetic force, turning a lethal blow into a flesh wound."
            },
            "sidestep": {
                "name": "Sidestep",
                "stamina_cost": 1,
                "mechanic_tags": ["auto_dodge_ranged"],
                "director_flavor": "A casual, mathematically perfect shift of the torso causes the projectile to pass harmlessly by."
            },
            "afterimage": {
                "name": "Afterimage",
                "focus_cost": 1,
                "mechanic_tags": ["auto_miss"],
                "director_flavor": "The enemy's weapon cleaves through the character, only for the image to dissipate like smoke—a visual echo left behind."
            },
            "roll_with_the_punch": {
                "name": "Roll with the Punch",
                "stamina_cost": 0,
                "mechanic_tags": ["free_movement"],
                "director_flavor": "Riding the kinetic energy of the attack, the character uses the momentum to instantly slide away from the attacker."
            },
            "vibration_ward": {
                "name": "Vibration Ward",
                "passive": True,
                "director_flavor": "The character vibrates at a frequency that makes it physically impossible for grapples or restraints to hold them."
            },
            "deflect": {
                "name": "Deflect",
                "stamina_cost": 0,
                "mechanic_tags": ["parry_projectiles"],
                "director_flavor": "A blurring swat of their blade knocks the incoming projectile out of the air."
            },
            "untouchable": {
                "name": "Untouchable",
                "passive": True,
                "director_flavor": "Untouched and flawless, the character moves with terrifying, accelerated speed."
            },
            "phase_dodge": {
                "name": "Phase Dodge",
                "stamina_cost": 2,
                "mechanic_tags": ["negate_critical"],
                "director_flavor": "Faced with a lethal blow, the character vibrates completely out of sync with reality for a split second, taking absolutely zero trauma."
            },
            "ghost_in_the_machine": {
                "name": "Ghost in the Machine",
                "stamina_cost": 0,
                "mechanic_tags": ["capstone", "invulnerable"],
                "director_flavor": "Entering a state of absolute kinetic flow, the character becomes totally untouchable, weaving through the chaos like a ghost."
            },
            # Branch C: The Catalyst
            "feather_fall": { "name": "Feather Fall", "passive": True, "director_flavor": "Unconsciously bleeding momentum, the character lands lightly without taking any falling damage." },
            "wall_run": { "name": "Wall Run", "move_cost": 1, "director_flavor": "Defying gravity, the character sprints horizontally across the vertical surface." },
            "lightning_reflexes": { "name": "Lightning Reflexes", "passive": True, "director_flavor": "Their nervous system fires impossibly fast, always acting first." },
            "sleight_of_hand": { "name": "Sleight of Hand", "passive": True, "director_flavor": "Their hands blur, manipulating the object faster than the naked eye can process." },
            "vibration_sense": { "name": "Vibration Sense", "stamina_cost": 0, "director_flavor": "Touching the surface, they read the micro-vibrations to perfectly map the surrounding entities." },
            "sonic_hush": { "name": "Sonic Hush", "passive": True, "director_flavor": "They vibrate to perfectly cancel out their own physical friction, moving in absolute silence." },
            "kinetic_transfer": { "name": "Kinetic Transfer", "stamina_cost": 0, "director_flavor": "Touching their ally, they instantly transfer their raw physical momentum into them." },
            "escape_artist": { "name": "Escape Artist", "stamina_cost": 0, "director_flavor": "In a fraction of a second, joints pop and dislocate, slipping free from the restraints." },
            "hyper_metabolism": { "name": "Hyper-Metabolism", "passive": True, "director_flavor": "Their accelerated metabolism rapidly flushes the toxins from their system." },
            "time_dilation": {
                "name": "Time Dilation",
                "focus_cost": 99,
                "stamina_cost": 99,
                "mechanic_tags": ["capstone", "time_stop"],
                "director_flavor": "Perception accelerates to the point where the rest of the world completely freezes in place."
            }
        }
    },

    "the_razor": {
        "name": "The Razor",
        "category": "archetype",
        "base_stat": "finesse",
        "description": "Masters of liquid geometry, pinpoint accuracy, dueling blades, and bows.",
        "skills": {
            # Branch A: The Breaker
            "precision_strike": {
                "name": "Precision Strike",
                "mechanic_tags": ["ignore_armor"],
                "director_flavor": "The blade finds the exact seam in the armor, bypassing the plating entirely."
            },
            "hamstring_shot": {
                "name": "Hamstring Shot",
                "mechanic_tags": ["move_beat_drain"],
                "director_flavor": "A pinpoint shot to the leg instantly cripples the target's mobility."
            },
            "riposte": {
                "name": "Riposte",
                "stamina_cost": 1,
                "mechanic_tags": ["counter_attack"],
                "director_flavor": "Deflecting the blow, they instantly reverse the momentum into a lightning-fast counter-thrust."
            },
            "molecular_edge": {
                "name": "Molecular Edge",
                "focus_cost": 1,
                "mechanic_tags": ["upgrade_injury", "major_injury"],
                "director_flavor": "Honing the weapon to an atom-thin edge, the strike slices through matter with terrifying ease."
            },
            "disarm": {
                "name": "Disarm",
                "mechanic_tags": ["drop_weapon"],
                "director_flavor": "A surgical cut to the wrist tendons forces the screaming enemy to drop their weapon."
            },
            "pinning_shot": {
                "name": "Pinning Shot",
                "mechanic_tags": ["pin_target", "move_beat_drain"],
                "director_flavor": "The projectile slams into the target, violently pinning their clothing or limbs to the environment."
            },
            "destabilizing_wound": {
                "name": "Destabilizing Wound",
                "mechanic_tags": ["bleed_dot"],
                "director_flavor": "The alchemically unbinding cut refuses to clot, leaving a grisly, continuously bleeding wound."
            },
            "snipers_mark": {
                "name": "Sniper's Mark",
                "move_cost": 1,
                "mechanic_tags": ["upgrade_injury"],
                "director_flavor": "Remaining perfectly still, they line up a flawless, devastating shot."
            },
            "heart_seeker": {
                "name": "Heart-Seeker",
                "mechanic_tags": ["stealth_critical"],
                "director_flavor": "Striking from the shadows, the blade slips perfectly between the ribs and directly into the heart."
            },
            "telefrag": {
                "name": "Telefrag",
                "stamina_cost": 99,
                "mechanic_tags": ["capstone", "instant_kill", "ignore_thresholds"],
                "director_flavor": "The character materializes violently inside the target's physical space, forcing their atoms apart from the inside in an explosion of gore."
            },
            
            # Branch B: The Bastion
            "parry": {
                "name": "Parry",
                "stamina_cost": 1,
                "mechanic_tags": ["negate_injury"],
                "director_flavor": "With a flick of the wrist, the incoming attack is batted harmlessly aside."
            },
            "liquefy": {
                "name": "Liquefy",
                "mechanic_tags": ["downgrade_injury"],
                "director_flavor": "The character's flesh turns momentarily malleable; the weapon passes partially through them like water."
            },
            "frictionless": {
                "name": "Frictionless",
                "passive": True,
                "director_flavor": "Their altered surface friction allows them to slip out of any physical grasp."
            },
            "phase_step": {
                "name": "Phase-Step",
                "focus_cost": 1,
                "mechanic_tags": ["teleport_dodge"],
                "director_flavor": "Space folds around them; they instantly teleport to a nearby zone, leaving the attack to strike empty air."
            },
            "refract": {
                "name": "Refract",
                "passive": True,
                "director_flavor": "Bending the space around their body, incoming projectiles warp off-target."
            },
            "riposte_guard": {
                "name": "Riposte Guard",
                "passive": True,
                "director_flavor": "Their defensive stance is a lethal trap. As the enemy misses, a waiting blade instantly punishes them."
            },
            "liquid_evasion": {
                "name": "Liquid Evasion",
                "mechanic_tags": ["aoe_resistance"],
                "director_flavor": "Flowing like liquid around the blast, they emerge almost completely unscathed."
            },
            "molecular_shift": {
                "name": "Molecular Shift",
                "mechanic_tags": ["downgrade_critical"],
                "director_flavor": "Vital organs phase out of reality for a microsecond, turning a lethal blow into a glancing scratch."
            },
            "slippery_target": {
                "name": "Slippery Target",
                "passive": True,
                "director_flavor": "Constant, fluid movement makes them increasingly impossible to hit."
            },
            "untethered": {
                "name": "Untethered",
                "stamina_cost": 0,
                "mechanic_tags": ["capstone", "invulnerable", "ethereal"],
                "director_flavor": "Stepping completely out of phase with the physical world, they walk through solid walls and enemy blades as an untouchable phantom."
            },

            # Branch C: The Catalyst
            "grip_and_slip": { "name": "Grip & Slip", "passive": True, "director_flavor": "Altering friction, they traverse impossible surfaces with ease." },
            "reshape": { "name": "Reshape", "stamina_cost": 0, "director_flavor": "Inanimate matter yields to them like wet clay." },
            "perfect_balance": { "name": "Perfect Balance", "passive": True, "director_flavor": "They walk the razor's edge with absolute, inhuman stability." },
            "liquid_egress": { "name": "Liquid Egress", "stamina_cost": 0, "director_flavor": "Bones dislocate and flesh liquefies as they squeeze through the impossibly small opening." },
            "phase_reach": { "name": "Phase-Reach", "focus_cost": 1, "director_flavor": "Their arm phases directly through the solid matter to grasp what lies beyond." },
            "saboteurs_eye": { "name": "Saboteur's Eye", "passive": True, "director_flavor": "A glance reveals the hidden linchpin holding the mechanism together." },
            "acrobatic_vault": { "name": "Acrobatic Vault", "stamina_cost": 0, "director_flavor": "Manipulating gravity, they execute a massive, graceful leap over the battlefield." },
            "silent_step": { "name": "Silent Step", "passive": True, "director_flavor": "Every footstep is rendered totally frictionless and silent." },
            "transmute_matter": { "name": "Transmute Matter", "stamina_cost": 0, "director_flavor": "The solid object dissolves into a swirling liquid or gas for safe storage." },
            "spatial_fold": {
                "name": "Spatial Fold",
                "focus_cost": 99,
                "mechanic_tags": ["capstone", "create_portal"],
                "director_flavor": "The character rips the geometry of the map apart, forging a permanent two-way tear in reality."
            }
        }
    },

    "endurance": {
        "name": "Endurance",
        "category": "core",
        "description": "Pure physical stamina, pain tolerance, heavy plate, and polearm mastery.",
        "skills": {
            "forced_march": { "name": "Forced March", "director_flavor": "Pushing their biology through extreme exhaustion." },
            "hardened_lungs": { "name": "Hardened Lungs", "director_flavor": "Holding their breath or resisting airborne toxins with iron lungs." },
            "structural_brace": { "name": "Structural Brace", "director_flavor": "Reinforcing a doorway using sheer body weight." },
            "ablative_guard": { "name": "Ablative Guard", "director_flavor": "Angling heavy armor to turn a direct hit into a glancing blow." },
            "phalanx": { "name": "Phalanx", "director_flavor": "Physically stepping in with a shield to cover a teammate." },
            "pain_suppression": { "name": "Pain Suppression", "director_flavor": "Ignoring the agonizing penalties of their wounds." },
            "pike_wall": { "name": "Pike Wall", "director_flavor": "Setting a polearm to receive a charging enemy." },
            "batter": { "name": "Batter", "director_flavor": "Delivering repeated, exhausting blows against the target's shield." },
            "impale": { "name": "Impale", "director_flavor": "Pinning an enemy to the ground with a polearm." },
            "the_anvil": { 
                "name": "The Anvil", 
                "stamina_cost": 99, 
                "director_flavor": "Becoming an immovable object, refusing to be incapacitated by any physical trauma until the battle ends." 
            }
        }
    },

    "vitality": {
        "name": "Vitality",
        "category": "core",
        "description": "Biological resilience, natural healing, unarmed strikes, and pure survival instinct.",
        "skills": {
            "clot": { "name": "Clot", "director_flavor": "Flexing their musculature to physically seal open wounds." },
            "feral_resilience": { "name": "Feral Resilience", "director_flavor": "Falling back on primal survival instincts when cornered." },
            "iron_gut": { "name": "Iron Gut", "director_flavor": "Resisting ingested hazards or extreme environmental exposure." },
            "grapple": { "name": "Grapple", "director_flavor": "Locking the enemy in a brutal biological hold." },
            "feral_strike": { "name": "Feral Strike", "director_flavor": "Executing unarmed attacks using bone, teeth, or raw body weight." },
            "chokehold": { "name": "Chokehold", "director_flavor": "Cutting off air and blood flow to the brain." },
            "apex_predator": {
                "name": "Apex Predator",
                "stamina_cost": 99,
                "director_flavor": "Tapping into primal adrenaline, stabilizing all bleeding and striking with terrifying, heavy force."
            }
        }
    },

    "fortitude": {
        "name": "Fortitude",
        "category": "core",
        "description": "Grit, environmental resistance, heavy recoil management, and exotic weapons.",
        "skills": {
            "grit": { "name": "Grit", "director_flavor": "Biting down on the pain and bracing their core against blunt-force impact." },
            "momentum_swing": { "name": "Momentum Swing", "director_flavor": "Maximizing the kinetic energy of an exotic spinning weapon to shatter shields." },
            "suppressive_fire": { "name": "Suppressive Fire", "director_flavor": "Unleashing a deafening hail of projectiles to keep heads down." },
            "shrapnel_burst": { "name": "Shrapnel Burst", "director_flavor": "Firing an explosive or scatter-shot at close range." },
            "the_juggernaut": {
                "name": "The Juggernaut",
                "stamina_cost": 99,
                "director_flavor": "Becoming a walking siege engine, smashing straight through barricades and sending enemies flying."
            }
        }
    },
    
    "knowledge": {
        "name": "Knowledge",
        "category": "core",
        "description": "Information recall, alchemy, traps, anatomical exploits, and sensory revulsion.",
        "skills": {
            "tactical_anticipation": { "name": "Tactical Anticipation", "director_flavor": "Reading the enemy's stance and footwork to perfectly predict their strike." },
            "formulate_antidote": { "name": "Formulate Antidote", "director_flavor": "Quickly mixing and administering a chemical counter-agent." },
            "mental_compartmentalization": { "name": "Mental Compartmentalization", "director_flavor": "Blocking out pain and horror using pure clinical detachment." },
            "anatomical_strike": { "name": "Anatomical Strike", "director_flavor": "Directing a physical attack exactly where the organs are unprotected." },
            "toxic_coating": { "name": "Toxic Coating", "director_flavor": "Applying an alchemical irritant that inflicts nauseating disgust upon impact." },
            "jury_rig_trap": { "name": "Jury-Rig Trap", "director_flavor": "Setting a rapid snare or explosive using the environment." },
            "the_architects_flaw": {
                "name": "The Architect's Flaw",
                "focus_cost": 99,
                "director_flavor": "Identifying the single, catastrophic flaw in the target's defense to ensure an unmitigable critical hit."
            }
        }
    },

    "logic": {
        "name": "Logic",
        "category": "core",
        "description": "Geometry, calculated risk, coordination, acoustic dissonance, and trap utilization.",
        "skills": {
            "predictive_evasion": { "name": "Predictive Evasion", "director_flavor": "Moving to the exact coordinate where the attack mathematically won't be." },
            "deflection_angle": { "name": "Deflection Angle", "director_flavor": "Angling a shield perfectly to redirect force away from their center of mass." },
            "rationalize": { "name": "Rationalize", "director_flavor": "Breaking down a terrifying supernatural event into cold, hard facts." },
            "ricochet": { "name": "Ricochet", "director_flavor": "Bouncing a projectile off the environment to hit a hidden target." },
            "acoustic_dissonance": { "name": "Acoustic Dissonance", "director_flavor": "Creating a loud, mathematically jarring distraction." },
            "flanking_maneuver": { "name": "Flanking Maneuver", "director_flavor": "Positioning mathematically to cut off all escape vectors." },
            "the_grand_equation": {
                "name": "The Grand Equation",
                "focus_cost": 99,
                "director_flavor": "Perfectly calculating the battlefield geometry to ensure absolute advantage for all allies."
            }
        }
    },

    "awareness": {
        "name": "Awareness",
        "category": "core",
        "description": "Perception, tracking, situational awareness, blinding tactics, and sensory overload.",
        "skills": {
            "uncanny_dodge": { "name": "Uncanny Dodge", "director_flavor": "Reacting instantly to an attack they couldn't fully see coming." },
            "flash_smoke_screen": { "name": "Flash/Smoke Screen", "director_flavor": "Deploying blinding powder or smoke to totally obscure vision." },
            "grounding_focus": { "name": "Grounding Focus", "director_flavor": "Focusing intensely on a mundane detail to prevent sensory overload." },
            "called_shot": { "name": "Called Shot", "director_flavor": "Targeting a tiny, specific vulnerability like an eye slit or strap." },
            "distract": { "name": "Distract", "director_flavor": "Reflecting light or throwing an object to force the enemy to look away." },
            "expose": { "name": "Expose", "director_flavor": "Revealing a hidden or invisible enemy's location to the party." },
            "omnidirectional_sight": {
                "name": "Omnidirectional Sight",
                "focus_cost": 99,
                "director_flavor": "Entering a state of hyper-awareness, making it impossible to be surprised or flanked."
            }
        }
    },

    "intuition": {
        "name": "Intuition",
        "category": "core",
        "description": "Gut feelings, reading tells, weaponized luck, and instilling self-doubt.",
        "skills": {
            "blind_luck": { "name": "Blind Luck", "director_flavor": "Stumbling or accidentally dropping their guard at the exact perfect moment to avoid a lethal blow." },
            "read_the_tell": { "name": "Read the Tell", "director_flavor": "Anticipating the enemy's attack by reading their eyes and body language." },
            "shake_it_off": { "name": "Shake it Off", "director_flavor": "Dismissing supernatural dread as just a 'bad feeling'." },
            "feint": { "name": "Feint", "director_flavor": "Tricking the enemy into blocking the wrong way with a false tell." },
            "jinx": { "name": "Jinx", "director_flavor": "Noticing an environmental hazard and coincidentally triggering it right next to the enemy." },
            "sow_doubt": { "name": "Sow Doubt", "director_flavor": "Casually pointing out a flaw in the enemy's stance, instilling deep self-doubt." },
            "the_winning_hand": {
                "name": "The Winning Hand",
                "focus_cost": 99,
                "director_flavor": "Perfectly reading the flow of fate to dictate the exact result of the next critical moment."
            }
        }
    },

    "charm": {
        "name": "Charm",
        "category": "core",
        "description": "Charisma, persuasion, leadership, emotional manipulation, and imposing awe.",
        "skills": {
            "defuse": { "name": "Defuse", "director_flavor": "Talking an enemy down, causing them to hesitate right before they strike." },
            "inspire_courage": { "name": "Inspire Courage", "director_flavor": "Bolstering an ally's resolve in the heat of battle." },
            "the_martyr": { "name": "The Martyr", "director_flavor": "Drawing enemy attention using pure, overwhelming presence to save an ally." },
            "command": { "name": "Command", "director_flavor": "Barking a military order so forcefully the enemy instinctively obeys." },
            "demoralize": { "name": "Demoralize", "director_flavor": "Taunting and mocking the enemy to shatter their spirit." },
            "incite": { "name": "Incite", "director_flavor": "Manipulating the enemy's anger to turn them against their own allies." },
            "the_sovereigns_decree": {
                "name": "The Sovereign's Decree",
                "focus_cost": 99,
                "director_flavor": "Commanding absolute attention, forcing enemies to drop their weapons in sheer Awe."
            }
        }
    },

    "willpower": {
        "name": "Willpower",
        "category": "core",
        "description": "Mental grit, interrogation, intimidation, and raw, unyielding determination.",
        "skills": {
            "mental_fortress": { "name": "Mental Fortress", "director_flavor": "Locking the mind shut against psychological trauma or psychic intrusion." },
            "defiance": { "name": "Defiance", "director_flavor": "Staring down the attacker and bracing for impact out of pure stubbornness." },
            "bite_the_bullet": { "name": "Bite the Bullet", "director_flavor": "Performing agonizing field surgery without anesthetic." },
            "intimidate": { "name": "Intimidate", "director_flavor": "Projecting an aura of overwhelming dread and unquestionable authority." },
            "relentless_pursuit": { "name": "Relentless Pursuit", "director_flavor": "Mentally refusing to let the target escape, ignoring all distractions." },
            "brutal_takedown": { "name": "Brutal Takedown", "director_flavor": "Executing a vicious, terrifying strike meant specifically to send a message to onlookers." },
            "absolute_grit": {
                "name": "Absolute Grit",
                "focus_cost": 99,
                "director_flavor": "Refusing to break. Becoming completely immune to fear, trauma, and intimidation driven by unstoppable willpower."
            }
        }
    }
}

def get_skill_flavor(skill_name: str) -> str:
    """Helper to do a deep search for a skill name and return its flavor text."""
    if not skill_name:
        return ""
        
    lookup = skill_name.lower().replace(" ", "_").replace("'", "")
    
    for track_key, track_data in SKILL_TRACKS.items():
        skills = track_data.get("skills", {})
        if lookup in skills:
            return skills[lookup].get("director_flavor", "")
            
    return ""
