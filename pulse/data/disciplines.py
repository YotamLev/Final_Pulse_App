"""Discipline definitions and power helper for Final Pulse 2E."""

from __future__ import annotations

# Each power dict:
#   name: str
#   level: int       — minimum discipline level to acquire
#   description: str
#   requires: str | None  — name of another power that must be acquired first

DISCIPLINES: dict[str, dict] = {
    "Auspex": {
        "image": "Data/Images/Auspex_symbol.png",
        "powers": [
            {"name": "Enhance Senses", "level": 1, "description": "Add Auspex level to sensory input: seeing, hearing, etc.", "requires": None},
            {"name": "Sense The Unseen", "level": 1, "description": "Roll Auspex to find hidden and invisible creatures or objects.", "requires": None},
            {"name": "Impulse", "level": 1, "description": "Ask 1 question per scene about: danger, emotions, or specific secrets.", "requires": None},
            {"name": "Read Aura", "level": 2, "description": "Pay 1 Blood, roll Auspex — margin is number of questions you ask about a target creature, or skim surface thoughts of people nearby.", "requires": None},
            {"name": "Spirit's Touch", "level": 2, "description": "Pay 1 Blood, roll Auspex — margin is number of questions you ask about a target item or building.", "requires": None},
            {"name": "Anticipation", "level": 2, "description": "Pay 1 Blood, add Auspex to rolls made to dodge or defend against all kinds of attacks and dangers, for a scene.", "requires": None},
            {"name": "Telepathy", "level": 3, "description": "Pay 1 Blood, talk to 1 target you know for a scene. If target is unwilling or far, roll Auspex. Lasts for a scene.", "requires": None},
            {"name": "Write Script", "level": 3, "description": "Pay 1 Blood, choose a short phrase and a target whom you are in conversation with - the target will utter it, in some form.", "requires": None},
            {"name": "Clairvoyance", "level": 3, "description": "Pay 1 Blood, roll Auspex — margin is number of questions about events during the last day in a large area.", "requires": None},
            {"name": "Tempt Fate", "level": 4, "description": "Pay 3 Blood, cause another to reroll a roll. Once per night.", "requires": None},
            {"name": "Scry", "level": 4, "description": "When using Telepathy you can roll Auspex to avoid the target sensing you. When Telepathy is active, experience the target's senses in real time.", "requires": "Telepathy"},
        ],
    },
    "Animalism": {
        "image": "Data/Images/Animalism_symbol.png",
        "powers": [
            {"name": "Ghoul Animal", "level": 1, "description": "Pay 1 Blood to ghoul an animal to serve you. Up to Animalism level simultaneously. Wants to serve like a loyal dog but no greater intelligence.", "requires": None},
            {"name": "Mark Territory", "level": 1, "description": "Pay 1 Blood in a place you own to impose difficulty on rivals in it.", "requires": None},
            {"name": "Confront the Beast", "level": 1, "description": "Pay 1 Blood, roll Animalism — relax or enrage another Vampire's Beast.", "requires": None},
            {"name": "Borrowed Wisdom", "level": 2, "description": "Drinking from an animal gives +3 to +5 in things it excels at until next feed. In addition, animal blood becomes as nourishing as human Blood - a large dog can give 3 Blood, a wolf can give 4 Blood, a horse 6.", "requires": None},
            {"name": "Abomination", "level": 2, "description": "Pay 1 Blood to make monstrous changes to a ghouled animal (enlarge, add HP, add features). Max changes = Animalism level.", "requires": "Ghoul Animal"},
            {"name": "Unliving Hive", "level": 2, "description": "A swarm of small animals lives in your dead flesh. Add Animalism level to Intimidation rolls, half Animalism (rounded down) to close-range attacks.", "requires": None},
            {"name": "The Wild Hunt", "level": 3, "description": "Pay 1 Blood, enrage all animals to seek and attack a target — your Animalism is their roll.", "requires": None},
            {"name": "Wild Whispers", "level": 3, "description": "Pay 1 Blood, communicate with any animal fully for a scene.", "requires": None},
            {"name": "Summon Animal", "level": 3, "description": "Summon a specific type of animal or specify characteristics. Roll Animalism if very specific or uncommon in area.", "requires": None},
            {"name": "Wild Escape", "level": 5, "description": "When reduced to 0 HP, instantly move your consciousness to a nearby ghouled animal instead of torpor. Getting a drop of your original blood lets you reform your old body.", "requires": "Ghoul Animal"},
        ],
    },
    "Celerity": {
        "image": "Data/Images/Celerity_symbol.png",
        "powers": [
            {"name": "Speed", "level": 1, "description": "Add Celerity level to rolls involving speed: running, slashing, dodging. Add half Celerity (rounded down) to rolls of precision.", "requires": None},
            {"name": "Blink", "level": 2, "description": "Pay 1 Blood, move super-fast in your turn: walk on water, on vertical walls, between the blades of a spinning jet engine.", "requires": None},
            {"name": "Bullet Speed", "level": 3, "description": "When using Speed, add Celerity level (instead of half) to rolls of precision, including shooting.", "requires": "Speed"},
            {"name": "Hover", "level": 4, "description": "The vampire can hover slightly above ground.", "requires": None},
            {"name": "Fast Strike", "level": 4, "description": "Pay 2 Blood, you can take 2 actions in a turn without penalties.", "requires": None},
            {"name": "Unholy Flight", "level": 5, "description": "Pay 1 Blood, the vampire can fly at running speed for a scene.", "requires": "Hover"},
            {"name": "Uncanny Dodge", "level": 5, "description": "When attacked by something you can dodge, pay 1 Blood, lower incoming HP damage by 2, as a reflex.", "requires": "Bullet Speed"},
        ],
    },
    "Dominate": {
        "image": "Data/Images/Dominate_symbol.png",
        "powers": [
            {"name": "Draw On Instinct", "level": 1, "description": "Cause a mortal to obey a simple command that is some form of: Flee ('run away!'), Freeze ('kneel before me,'), or Fight ('shoot that guy!').", "requires": None},
            {"name": "Cloud Mind", "level": 1, "description": "Cause a mortal to forget the last 5 minutes and the next 2 minutes.", "requires": None},
            {"name": "Mesmerize", "level": 2, "description": "Pay 1 Blood, target a mortal (roll Dominate if they resist), set a simple task, which the target will do for about a scene. Task can't be suicidal. Mortals remember the task but not why.", "requires": None},
            {"name": "Modify Memory", "level": 2, "description": "Pay 1 Blood, target a mortal, roll Dominate, alter memories. Cannot extract information.", "requires": None},
            {"name": "Implant Trigger", "level": 3, "description": "Pay 1 Blood, allows Mesmerize, Cloud Mind, and Modify Memory to have a trigger. Lasts for Dominate level days or until triggered.", "requires": None},
            {"name": "Terminal Decree", "level": 3, "description": "Allows suicidal tasks with Mesmerize.", "requires": "Mesmerize"},
            {"name": "Dominate Your Kind", "level": 4, "description": "Allows using Dominate powers on vampires. Very hard and very risky.", "requires": None},
            {"name": "Mass Dominate", "level": 4, "description": "Target more than 1 mortal with Dominate, paying 1 Blood per extra mortal. Max targets = Dominate level.", "requires": None},
            {"name": "Rationalize", "level": 4, "description": "Targets of Dominate powers will attempt to reconcile their actions & memories, possibly scarring their personality.", "requires": None},
        ],
    },
    "Fortitude": {
        "image": "Data/Images/Fortitude_symbol.png",
        "powers": [
            {"name": "Rapid Healing", "level": 1, "description": "Each 1 Blood paid allows healing 2 HP instead of 1.", "requires": None},
            {"name": "Toughness", "level": 1, "description": "Add 2 max HP per level of Fortitude.", "requires": None},
            {"name": "Prowess From Pain", "level": 2, "description": "Each HP damage you have, up to Fortitude level, can be added to physical attacks or stressed efforts.", "requires": None},
            {"name": "Draught of Endurance", "level": 2, "description": "Your ghouls add your Fortitude level to their HP. A vampire drinking at least 1 of your Blood gets your Fortitude powers for the night.", "requires": None},
            {"name": "Flesh of Marble", "level": 3, "description": "Pay 2 Blood, take no damage for 1 turn.", "requires": None},
            {"name": "Mind Fortress", "level": 3, "description": "Add Fortitude level to rolls to resist mental powers.", "requires": None},
            {"name": "Last Stand", "level": 4, "description": "If reduced to 0 HP, Flesh of Marble activates automatically to prevent Torpor, as long as Blood is -8 or higher. Blood cost paid as normal.", "requires": "Flesh of Marble"},
            {"name": "Endurance", "level": 5, "description": "Flesh of Marble costs 1 Blood instead of 2.", "requires": "Flesh of Marble"},
        ],
    },
    "Nightmare": {
        "image": "Data/Images/nightmare.png",
        "powers": [
            {"name": "Haunting Dream", "level": 1, "description": "This power has 2 uses, depending on target: mortals, either sleeping or awake. For sleeping mortals, this power lets the vampire to appear in a mortal's dreams, affecting them, creating any effect the vampire desires. The mortal can be specific, or the vampire can search for someone with characteristics, such as: a rich person, a loyal servant, a young man. Very specific, or very distant mortals might be harder to reach. For waking mortals, this power can cause them to believe something unnatural they witnessed is a dream or hallucination.", "requires": None},
            {"name": "Lullaby", "level": 1, "description": "Put an unsuspecting mortal to sleep. You can pay 1 Blood and affect a group of mortals. Suspecting mortals or stressful environments may require a Nightmare roll.", "requires": None},
            {"name": "Primal Feed", "level": 1, "description": "Drinking from a terrified target yields between 1 and 3 extra Blood. So, with a properly freightened mortal, the vampire can take a small sip of 1 Blood - leaving the mortal barely affected by anemia - but gain 4 Blood for the vampire themselves.", "requires": None},
            {"name": "Dread Gaze", "level": 1, "description": "Add Nightmare to Intimidation rolls, and a +2 margin on intimidation can paralyze a target for a turn. By 1 paying 1 Blood, you can paralyze multiple targets with the roll (after rolling). If you fail the use of this power, you may take a different action for your turn.", "requires": None},
            {"name": "Encroach", "level": 2, "description": "This power allows the vampire to project themselves in a variety of ways: you can cast your voice to sound as if coming from elsewhere, you can create illusory copies of parts of your body (hands, eyes, mouth) and project them as distorted (for example, twice larger, or discolored, or younger). This power can be used to whisper in someone's ear, have your gaze follow the victim from every mirror and window, or create the illusion of a carpet made of your grasping hands. This illusions are momentary.", "requires": None},
            {"name": "Haunting Ground", "level": 2, "description": "Activate to cause mortals to subconsciously avoid an area when you are there, can be active during daysleep.", "requires": None},
            {"name": "Paranoia", "level": 3, "description": "Pay 1 Blood, unnerve a target you talk to, rolling Intimidation and causing willpower damage per margin.", "requires": None},
            {"name": "Illusion", "level": 3, "description": "Pay 1 Blood, Create one of three types of illusions: 1. a stationary persistent illusion, up to the size of a horse or a wide double-door. 2. a moving, momentary illusion, up to a size of a car. 3. A scenic, intangible illusion: the sound, sight, and ambience of a rainstorm appearing through all windows in a building; A thunder booming at the end of your sentence; A crowd of distant intangible ghosts in a graveyard. Interaction with these illusions can reveal it, as can Auspex powers. Complex illusion may require a Nightmare or Deception roll. Type 1 and 3 lasts a scene, as type 2 is momentary. You can pay more Blood to create more illusions, but this can be harder to maintain.", "requires": None},
            {"name": "Doom Prophecy", "level": 3, "description": "Pay 1 Blood if not in Torpor. You cause a mortal to believe some terrible doom will affect them, thier loved ones, or the world - unless they do something. You define that necessary act, for example: kill the mayor, dig a specific coffin from somewhere, bring all of your money to a parking lot at midnight. This is one of the only powers that can be activated from Torpor.", "requires": "Haunting Dream"},
            {"name": "Psychic Bomb", "level": 5, "description": "Pay 3 Blood. You cause nearby mortals to go mad, believing an eldritch god has awakened, or aliens invaded, or something else of your choosing. Their behaviour is unpredictable, and this power can break Blood Bonds (for Ghouls), Presence powers, and Dominate powers.", "requires": None},
        ],
    },
    "Obfuscate": {
        "image": "Data/Images/Obfuscate_symbol.png",
        "powers": [
            {"name": "Fade", "level": 1, "description": "Low-level hypnotism makes all mortals avert their eyes and ignore you, seeing you as a forgettable nobody.", "requires": None},
            {"name": "Cloak of Shadows", "level": 1, "description": "Standing still or moving obscured against a backdrop allows you to be totally ignored by mortals — they see you as an object or vegetation.", "requires": None},
            {"name": "Vanish", "level": 2, "description": "Pay 1 Blood, be completely invisible for a scene. Intentionally stopping from hiding, by attacking, talking loudly etc, - ends the invisibility.", "requires": None},
            {"name": "Disguise", "level": 2, "description": "Pay 1 Blood, alter your appearance to appear as another person. Copying someone exactly is much harder.", "requires": None},
            {"name": "Labyrinth", "level": 2, "description": "Pay 1 Blood, cause mortals to get confused and lost around you, having difficulty navigating. Lasts a scene or pay 1 extra Blood for the whole day.", "requires": None},
            {"name": "Silent Hunter", "level": 2, "description": "When using Fade, Cloak of Shadows, or Vanish — the vampire can also completely silence sounds from themselves.", "requires": None},
            {"name": "Ambusher", "level": 3, "description": "All Obfuscate powers now work on other Vampires. Those with Auspex can roll against your Obfuscate, but suffer -3.", "requires": None},
            {"name": "Cloak the Gathering", "level": 3, "description": "Extend Obfuscate powers to willing vampires who stay close. Pay 1 extra Blood per vampire per scene.", "requires": None},
        ],
    },
    "Potence": {
        "image": "Data/Images/Potence_symbol.png",
        "powers": [
            {"name": "Vigor", "level": 1, "description": "Add Potence to rolls involving strength and muscles: swinging a sword, jumping, bending metal.", "requires": None},
            {"name": "Shockwave", "level": 2, "description": "Pay 1 Blood, your attacks count against all in close-range to you instead of choosing 1 enemy.", "requires": None},
            {"name": "Bloody Strangle", "level": 2, "description": "Pay 1 Blood while grappling a target — that target cannot use supernatural powers, except Potence and Fortitude, as long as you hold it.", "requires": None},
            {"name": "Brutal Feed", "level": 2, "description": "Can drain an entire mortal in 1 turn.", "requires": None},
            {"name": "Unholy Might", "level": 5, "description": "When using Blood Surge on a roll involving strength and muscles, add 2 red dice per Blood instead of 1.", "requires": None},
        ],
    },
    "Presence": {
        "image": "Data/Images/Presence_symbol.png",
        "powers": [
            {"name": "Awe", "level": 1, "description": "Add Presence to Social rolls.", "requires": None},
            {"name": "Summon", "level": 1, "description": "Call a mortal you know to you. They will do all in their power to reach you.", "requires": None},
            {"name": "Midnight Command", "level": 2, "description": "Pay 1 Blood, add your Presence to rolls made by your ghouls and mortals you lead for a scene.", "requires": None},
            {"name": "Hypnotize", "level": 2, "description": "Pay 1 Blood, roll Presence, paralyze a group of mortals or a vampire for as long as you keep using turns on this power.", "requires": None},
            {"name": "Affect Mood", "level": 2, "description": "Choose an emotion and project it to all mortals in the scene. This can heighten resonance in victims' blood.", "requires": None},
            {"name": "Sway", "level": 3, "description": "Pay 2 Blood, cause a great crowd of mortals to absolutely believe in a plausible cause. They will endanger themselves for it. Lasts a scene.", "requires": None},
            {"name": "Art Necro", "level": 4, "description": "Create a piece of art that can project one of your Presence powers on viewers.", "requires": None},
            {"name": "Ultimate Hypnotic", "level": 4, "description": "Hypnotize can now work on as many vampires as your Presence level.", "requires": "Hypnotize"},
            {"name": "Susceptible", "level": 5, "description": "Mortals exposed to your Presence powers act as loyal as Ghouls, for a night.", "requires": None},
        ],
    },
    "Protean": {
        "image": "Data/Images/Protean_symbol.png",
        "powers": [
            {"name": "Animorph", "level": 1, "description": "Pay 1 Blood, assume the shape of an animal (mouse to tiger) for a scene. Transforming takes a turn.", "requires": None},
            {"name": "Feral Weapons", "level": 1, "description": "Extend fangs and claws, add your Protean to close-range physical attacks.", "requires": None},
            {"name": "Bone Armor", "level": 1, "description": "Pay 1 or more Blood, gain 2 extra HP per Blood for a scene.", "requires": None},
            {"name": "Bone Bullets", "level": 1, "description": "Shoot teeth, bone spurs, or nails as natural weapons. Add your Protean to Projetile attacks.", "requires": None},
            {"name": "Separate Limb", "level": 2, "description": "Pay 1 Blood, separate a limb and grant it independence. It serves you but only has senses it physically has. Up to Protean level simultaneously.", "requires": None},
            {"name": "Mist Form", "level": 3, "description": "Pay 1 Blood, spend two turns to transform into a cloud of mist — untouchable save by fire and sunlight. Cannot spend more than two scenes as mist.", "requires": None},
            {"name": "Internal Shift", "level": 3, "description": "Move your internal organs at will — shift your heart to dodge a stake, make it seem to pound, terrify onlookers.", "requires": None},
            {"name": "Fleshcraft", "level": 4, "description": "pay 2 Blood, take two turns to transform your body: rotate your head 180°, move your hands to your belly, even attaching organs from other creatures, like having extra hands or spider eyes. Note that sensory organs offer no sensory input, but muscle, bone, chitin etc. do. wings require a giant bird, and flying with them is very hard. Up to Protean level changes simultaneously.", "requires": None},
            {"name": "Szlachta", "level": 5, "description": "You can use your Protean powers on your ghouls by touching them. This is very painful. Pay Blood prices as usual.", "requires": None},
        ],
    },
    "Arrete": {
        "image": "Data/Images/Alchemy_symbol.png",
        "powers": [
            {"name": "Calculating", "level": 1, "description": "Add your Arrete to mental actions requiring intelligence, typically in the Scheming Skill Tree.", "requires": None},
            {"name": "Perfect Recall", "level": 1, "description": "Pay 1 Blood, retroactively remember a detail from something you have seen, heard, or read.", "requires": None},
            {"name": "Borrowed Knowledge", "level": 2, "description": "When feeding from a victim, gain a bonus (1-3 dice) to areas of expertise they had until next feeding.", "requires": None},
            {"name": "The Common Denominator", "level": 2, "description": "Pay 1 Blood, learn any human language for a scene. Pay 2 Blood to decipher any encoded message you can access.", "requires": None},
            {"name": "Perfectionism", "level": 3, "description": "You can use Willpower to reroll up to 5 dice, instead of 3.", "requires": None},
            {"name": "Oral History", "level": 3, "description": "When feeding from a victim, gain a temporary custom skill at level 4 in an area of expertise the victim had, for the night. Up to Arrete level simultaneous skills. This does not interrupt Borrowed Knowledge.", "requires": "Borrowed Knowledge"},
        ],
    },
    "Necromancy": {
        "image": "Data/Images/Necromancy.png",
        "powers": [
            {"name": "Touch of Oblivion", "level": 1, "description": "Pay 1 Blood, cripple and age a body part with a single touch. Roll Necromancy and relevant skills to touch an unwilling creature.", "requires": None},
            {"name": "Ashes to Ashes", "level": 1, "description": "Turn a body to fine ash, eliminating all blood and gore. Can be used on rival zombies.", "requires": None},
            {"name": "Kill the Vibe", "level": 1, "description": "Roll Mortifex (Necromancy) to cancel Presence and Nightmare powers.", "requires": None},
            {"name": "Raise Corpse", "level": 2, "description": "Pay 1 Blood to raise a zombie using your Necromancy to act. Lasts for a night. The zombie obeys your commands as long as it can percieve you. Up to Necromancy level simultaneously.", "requires": None},
            {"name": "Summon Wraith", "level": 2, "description": "Pay 1 Blood to summon a ghost. Convince them to help — they can spy and frighten but not move anything materially except weak wind and sound.", "requires": None},
            {"name": "Ossuary Explosion", "level": 2, "description": "Pay 1 Blood, cause a body to explode, dealing Necromancy level damage to those nearby. No roll required.", "requires": None},
            {"name": "Zombie Legion", "level": 3, "description": "Undead created with Raise Corpse last to the next night as long as they aren't in sunlight. In addition, these undead serve even if they can't percieve who raised them.", "requires": "Raise Corpse"},
        ],
    },
    "Druidic": {
        "image": "Data/Images/Druidic.png",
        "powers": [
            {"name": "Frost Touch", "level": 1, "description": "Chill objects, freeze areas of water, or inflict frostbite with a touch.", "requires": None},
            {"name": "Disband Beasts", "level": 1, "description": "Roll Druidic to counter Animalism powers.", "requires": None},
            {"name": "Druidcraft", "level": 1, "description": "Cause minor changes in vegetation: flowers wither or bloom, mushrooms sprout.", "requires": None},
            {"name": "Upend the Course", "level": 2, "description": "Pay 1 Blood, somewhat affect the weather of a city area. Summon clouds, rain, or snow for the night.", "requires": None},
            {"name": "Wrath of Zeus", "level": 2, "description": "Pay 1 Blood, direct lightning to strike a target, rolling Druidic.", "requires": None},
            {"name": "Earth Meld", "level": 2, "description": "Pay 1 Blood, sink into and become one with soil. Leave when you wish. You can travel slowly through natural earth and wood in this state.", "requires": None},
            {"name": "Root Grasp", "level": 2, "description": "Pay 1 Blood, command roots, vines, branches, or other living plants to move, entangle, or immobilize targets. Roll Druidic. Lasts a scene.", "requires": None},
            {"name": "Sweet Sap", "level": 2, "description": "You can drink Blood from trees, killing them. A large old tree gives 2 Blood, and large bushes give 1.", "requires": None},
            {"name": "Malakan's Gift", "level": 3, "description": "Pay 1 Blood, animate a tree or major plant as a servant for a night. The older the plant is - the more powerful it is as a servant.", "requires": None},
            {"name": "Foul Wind", "level": 4, "description": "Pay 2 Blood, for a scene: strong winds can lift you to fly, and you can direct strong wind to push people and objects around.", "requires": None},
        ],
    },
    "Blood Sorcery": {
        "image": "Data/Images/Blood_Sorcery_symbol.png",
        "powers": [
            {"name": "Bend Blood", "level": 1, "description": "Control spilled blood, making it flow or float in the air. Up to 2 Liters at a time, and the max force it can apply is 3 kg.", "requires": None},
            {"name": "A Taste for Blood", "level": 1, "description": "By tasting blood, detect many facts: age, birthplace, Sire (if Vampire), Disciplines (if Vampire), emotions when blood was spilled. Additional facts may require a Blood Sorcery roll.", "requires": None},
            {"name": "Bend Veins", "level": 2, "description": "by paying 3 Blood, you can use Bend Blood even on blood inside another's body, rolling Blood Sorcery, for a scene. Causing damage is very difficult; slowing movement or causing a vampire to vomit blood is easy.", "requires": "Bend Blood"},
            {"name": "Telekinesis", "level": 3, "description": "by paying 1 Blood, Your Bend Blood power can now control up to 10 Liters of blood, and apply some force (roughly ~50 kg) at a time, for a turn.", "requires": "Bend Blood"},
            {"name": "Scorpion's Touch", "level": 3, "description": "Turn your own spilled vitae corrosive, melting whatever it touches. 1 Blood extracted is enough to melt a hole through a regular door.", "requires": None},
            {"name": "Vanigma", "level": 3, "description": "You can research and cast various spells and rituals. Describe your desited effect to the Storyteller, and they will present you with the Scheme difficulty to research & cast it.", "requires": None},
            {"name": "Cauldron of Blood", "level": 5, "description": "Pay 2 Blood, boil an enemy's blood in their veins, causing Blood Sorcery level damage in a turn to a target you can reach. No roll required.", "requires": None},
        ],
    },
    "Shadow Sorcery": {
        "image": "Data/Images/Oblivion_symbol.png",
        "powers": [
            {"name": "Dim the Lights", "level": 1, "description": "Cause lights to dim or flicker, subject to your control.", "requires": None},
            {"name": "Shadow Perspective", "level": 1, "description": "Look into a shadow and see from another shadow nearby.", "requires": None},
            {"name": "Shadow Step", "level": 2, "description": "Pay 1 Blood, slip into a shadow and re-emerge into another shadow close by.", "requires": None},
            {"name": "Grab the Effigy", "level": 2, "description": "Pay 1 Blood, for a scene you can beat, grapple, or use another's shadow as if it were the target. Roll Shadow Sorcery, adding Brawl if relevant.", "requires": None},
            {"name": "Shadow Step Mastery", "level": 3, "description": "Shadow Step costs 1 Blood and lasts for the scene.", "requires": "Shadow Step"},
            {"name": "Shoot the Shadow", "level": 3, "description": "Pay 2 Blood, cause one attack that hit you to hit your shadow instead, reflexively (no action required).", "requires": None},
            {"name": "Shadow Avatar", "level": 4, "description": "Pay 3 Blood, cause your shadow to materialize and act for a scene, acting as your double.", "requires": None},
        ],
    },
}

ALL_DISCIPLINE_NAMES: list[str] = list(DISCIPLINES.keys())
MAX_DISCIPLINE_LEVEL: int = 5
MAX_DISCIPLINES: int = 3

DISC_SHORT_DESC: dict[str, str] = {
    "Animalism":      "Control animals, act on your inner animal.",
    "Auspex":         "Enhance senses, peer into other dimensions, telepathy.",
    "Arrete":         "Supernatural intelligence.",
    "Celerity":       "Superhuman speed and agility.",
    "Dominate":       "Puppeteer others, wipe memories.",
    "Fortitude":      "Heal, absorb damage, enhance your capacity.",
    "Necromancy":     "Decay, raise lesser undead.",
    "Nightmare":      "Scare, unsettle, put to sleep.",
    "Obfuscate":      "Hide, appear differently.",
    "Potence":        "Strength, brutality.",
    "Presence":       "Enrapture, charm, control masses.",
    "Protean":        "Shapeshift.",
    "Blood Sorcery":  "Bend blood.",
    "Druidic":        "Control plants.",
    "Shadow Sorcery": "Grab others by their shadow, spy through shadows.",
}


def get_available_powers(disc_name: str, new_level: int, acquired_powers: list[str]) -> list[dict]:
    """Powers available to pick when raising a discipline to new_level."""
    powers = DISCIPLINES[disc_name]["powers"]
    return [
        p for p in powers
        if p["level"] <= new_level
        and p["name"] not in acquired_powers
        and (p["requires"] is None or p["requires"] in acquired_powers)
    ]


def total_disc_xp(disc_levels: dict[str, int]) -> int:
    """Total XP spent on discipline levels across all disciplines."""
    total = 0
    for level in disc_levels.values():
        if level > 0:
            total += level * (level + 1) // 2
    return total


def xp_cost_for_disc_level(current_level: int) -> int:
    """XP cost to raise a discipline from current_level to current_level + 1."""
    return current_level + 1
