"""Mortal and Vampire trait definitions for Final Pulse 2E."""

from __future__ import annotations

# Each trait dict keys:
#   key: str              – unique identifier
#   name: str             – display name
#   cost: int | None      – None when variable
#   variable_cost: bool   – player picks from cost_options
#   cost_options: list    – [(int, str), ...] when variable_cost
#   max_times: int        – how many times a character can take this (default 1)
#   description: str
#   requires_detail: bool – player must enter a text description
#   detail_prompt: str    – label for the detail input
#   sub_options: list[str]– choices for folkloric bane etc.
#   requires_sub_choice: bool

MORTAL_TRAITS: list[dict] = [
    {
        "key": "specialist",
        "name": "Specialist",
        "cost": 1,
        "max_times": 2,
        "description": "Expertise in a narrow field. Gain +1 whenever you roll using this expertise.",
        "requires_detail": True,
        "detail_prompt": "Describe the expertise (e.g., Epidemiology, Celtic History):",
    },
    {
        "key": "rare_specialist",
        "name": "Rare Specialist",
        "cost": 2,
        "max_times": 2,
        "description": "Rare expertise in a narrow field. Gain +2 whenever you roll using this expertise.",
        "requires_detail": True,
        "detail_prompt": "Describe the rare expertise:",
    },
    {
        "key": "world_renowned_specialist",
        "name": "World-Renowned Specialist",
        "cost": 4,
        "max_times": 1,
        "description": "World-renowned expertise. Gain +3 whenever you roll using this expertise. Can be taken once.",
        "requires_detail": True,
        "detail_prompt": "Describe the world-renowned expertise:",
    },
    {
        "key": "medical_condition",
        "name": "Medical Condition",
        "cost": None,
        "variable_cost": True,
        "cost_options": [
            (-1, "Minor — very short-sighted, stammer, limp"),
            (-2, "Moderate — missing limb, loss of hearing"),
            (-3, "Severe — wheelchair bound, blindness"),
        ],
        "description": "A medical condition the Embrace did not fix. Relevant rolls will be impeded.",
        "requires_detail": True,
        "detail_prompt": "Describe the condition:",
    },
    {
        "key": "brave",
        "name": "Brave",
        "cost": 2,
        "description": "Add +2 to rolls involving resisting fear.",
    },
    {
        "key": "compulsion",
        "name": "Compulsion",
        "cost": -1,
        "description": "A persistent mundane habit or fixation. Resisting tempting opportunities requires a roll.",
        "requires_detail": True,
        "detail_prompt": "Describe the compulsion (e.g., gambling, collecting, ritual cleanliness):",
    },
    {
        "key": "distinctive_appearance",
        "name": "Distinctive Appearance",
        "cost": -1,
        "description": "A conspicuous, memorable feature. Attempts to identify or track you gain +1. Disguises must conceal this.",
        "requires_detail": True,
        "detail_prompt": "Describe the distinctive feature (e.g., facial scarring, unusual pigmentation):",
    },
    {
        "key": "illiterate",
        "name": "Illiterate",
        "cost": -2,
        "description": "Cannot read or write fluently. May recognize familiar signs but cannot reliably understand written material.",
    },
    {
        "key": "addiction",
        "name": "Addiction",
        "cost": None,
        "variable_cost": True,
        "cost_options": [
            (-1, "Deprivation makes you distracted and irritable, impeding relevant rolls"),
            (-2, "Prolonged deprivation also prevents recovering Willpower until you indulge"),
        ],
        "description": "Dependent on a mundane substance or behavior.",
        "requires_detail": True,
        "detail_prompt": "Describe the addiction:",
    },
    {
        "key": "phobia",
        "name": "Phobia",
        "cost": None,
        "variable_cost": True,
        "cost_options": [
            (-1, "Confronting it impedes relevant rolls"),
            (-2, "Must also succeed on a roll to willingly approach or remain near it"),
        ],
        "description": "Intense, irrational fear of a specific stimulus.",
        "requires_detail": True,
        "detail_prompt": "Describe the phobia (e.g., enclosed spaces, heights, deep water):",
    },
    {
        "key": "famous",
        "name": "Famous",
        "cost": 1,
        "description": "Publicly known before the Embrace. Reputation opens doors but strangers may recognize you.",
        "requires_detail": True,
        "detail_prompt": "What were you famous for?",
    },
    {
        "key": "beautiful",
        "name": "Beautiful",
        "cost": 2,
        "description": "Exceptionally attractive. Gain +1 on first-impression rolls where physical appeal is relevant.",
    },
    {
        "key": "large",
        "name": "Large",
        "cost": 1,
        "description": "Exceptionally tall and heavily built. Gain +1 when size helps with lifting, blocking, or intimidation.",
    },
    {
        "key": "dwarfism",
        "name": "Dwarfism",
        "cost": 0,
        "description": "Significantly shorter than average. Gain +1 when size helps you hide or squeeze through confined spaces.",
    },
    {
        "key": "criminal_record",
        "name": "Criminal Record",
        "cost": -1,
        "description": "Serious criminal history. Official scrutiny involving your mortal identity is more likely to escalate.",
    },
    {
        "key": "double_jointed",
        "name": "Double-Jointed",
        "cost": 1,
        "description": "Unusually flexible joints. Gain +1 when escaping restraints, contorting through confined spaces.",
    },
    {
        "key": "sterile",
        "name": "Sterile / Eunuch",
        "cost": 0,
        "description": "Infertile or castrated before the Embrace. No mechanical effect, but shapes your mortal history.",
    },
    {
        "key": "embraced_young",
        "name": "Embraced Young",
        "cost": -1,
        "description": "Embraced before physical adulthood. Adults often dismiss your authority; age-restricted access is difficult.",
    },
    {
        "key": "embraced_old",
        "name": "Embraced Old",
        "cost": -1,
        "description": "Embraced at an advanced age. Others underestimate or patronize you.",
    },
    {
        "key": "perfect_pitch",
        "name": "Perfect Pitch",
        "cost": 1,
        "description": "Can identify and reproduce musical notes without a reference. Gain +1 when directly relevant.",
    },
    {
        "key": "color_blindness",
        "name": "Color Blindness",
        "cost": -1,
        "description": "Cannot reliably distinguish colors. Rolls involving color-coded information are impeded when color matters.",
    },
    {
        "key": "face_blindness",
        "name": "Face Blindness",
        "cost": -1,
        "description": "Struggles to recognize people by faces. Rolls involving identifying individuals by appearance are impeded.",
    },
    {
        "key": "tetrachromat",
        "name": "Tetrachromat",
        "cost": 1,
        "description": "Perceive subtle color differences most cannot. Gain +1 when examining dyes, bruising, forged artwork.",
    },
    {
        "key": "aphantasia",
        "name": "Aphantasia",
        "cost": -1,
        "description": "Cannot voluntarily form mental images. Rolls depending on visualizing a remembered face, place, or scene are impeded.",
    },
    {
        "key": "unerring_direction",
        "name": "Unerring Sense of Direction",
        "cost": 1,
        "description": "Always knows cardinal directions. Gain +1 when navigating or estimating relative positions.",
    },
    {
        "key": "genius",
        "name": "Genius",
        "cost": 3,
        "description": "Exceptional general intelligence. Gain +1 on abstract reasoning, rapid learning, complex problem-solving.",
    },
    {
        "key": "iron_constitution",
        "name": "Iron Constitution",
        "cost": 2,
        "description": "Exceptionally resistant to poison, disease, exhaustion. Gain +1 HP and +1 to rolls to muddle through.",
    },
    {
        "key": "perfect_balance",
        "name": "Perfect Balance",
        "cost": 2,
        "description": "Extraordinary sense of balance. Gain +2 on rolls to keep footing, move across unstable surfaces.",
    },
    {
        "key": "lightning_reflexes",
        "name": "Lightning Reflexes",
        "cost": 3,
        "description": "Exceptionally fast reactions. Gain +1 to rolls involving sudden danger, avoiding ambushes, or reacting quickly.",
    },
    {
        "key": "cowardly",
        "name": "Cowardly",
        "cost": -2,
        "description": "Unusually vulnerable to fear and panic. Suffer -2 on rolls to resist fear; when failed, instinctively flee or freeze.",
    },
    {
        "key": "amnesiac",
        "name": "Amnesiac",
        "cost": -2,
        "description": "Large parts of mortal life are missing. Rolls depending on personal history are impeded.",
    },
    {
        "key": "bad_liar",
        "name": "Bad Liar",
        "cost": -2,
        "description": "Visibly uncomfortable when lying. Rolls to tell a direct lie are impeded. Evasion and omission are unaffected.",
    },
    {
        "key": "night_blindness",
        "name": "Night Blindness",
        "cost": -3,
        "description": "Exceptionally poor vision in dim light. Unless brightly lit, visual rolls are impeded.",
    },
    {
        "key": "ugly",
        "name": "Ugly",
        "cost": -2,
        "description": "Notably unpleasant appearance. Rolls relying on physical attractiveness or favorable first impressions are impeded.",
    },
    {
        "key": "chronic_pain",
        "name": "Chronic Pain",
        "cost": -2,
        "description": "Persistent pain the Embrace did not cure. During demanding scenes, one relevant roll may be impeded.",
    },
    {
        "key": "innumerate",
        "name": "Innumerate",
        "cost": -2,
        "description": "Severe difficulty with numbers and arithmetic. Rolls involving accounts, prices, or calculations are impeded.",
    },
    {
        "key": "severe_allergy",
        "name": "Severe Allergy",
        "cost": -2,
        "description": "A dangerous allergy retained from mortal life. Exposure to the trigger causes serious impairment.",
        "requires_detail": True,
        "detail_prompt": "Describe the allergen (e.g., nuts, latex, insect venom):",
    },
    {
        "key": "dyslexia",
        "name": "Dyslexia",
        "cost": -2,
        "description": "Severe difficulty reading quickly. Rolls involving written records, codes, or time-sensitive reading are impeded.",
    },
    {
        "key": "severe_motion_sickness",
        "name": "Severe Motion Sickness",
        "cost": -1,
        "description": "Becomes disoriented in moving vehicles. Relevant rolls are impeded during travel and shortly afterward.",
    },
    {
        "key": "paranoid",
        "name": "Paranoid",
        "cost": -2,
        "description": "Habitually perceives hidden threats and betrayal. Rolls to accurately judge trustworthiness are impeded.",
    },
    {
        "key": "dissociative_episodes",
        "name": "Dissociative Episodes",
        "cost": -2,
        "description": "Under severe stress, becomes detached from surroundings. Awareness, memory, and social rolls are impeded.",
    },
    {
        "key": "depressive_episodes",
        "name": "Depressive Episodes",
        "cost": -2,
        "description": "Periodically falls into profound hopelessness. Rolls requiring initiative or sustained effort are impeded.",
    },
    {
        "key": "manic_episodes",
        "name": "Manic Episodes",
        "cost": -2,
        "description": "Periodic extreme energy and reduced judgment. Rolls to resist risky opportunities are impeded during episodes.",
    },
    {
        "key": "psychotic_episodes",
        "name": "Psychotic Episodes",
        "cost": -3,
        "description": "Under severe stress, may experience hallucinations or delusions. Rolls to correctly interpret events are impeded.",
    },
    {
        "key": "selective_mutism",
        "name": "Selective Mutism",
        "cost": -2,
        "description": "In certain social situations becomes unable to speak. During such episodes, verbal social actions are impossible.",
    },
    {
        "key": "panic_disorder",
        "name": "Panic Disorder",
        "cost": -2,
        "description": "Under intense stress, may suffer a panic attack. Rolls requiring concentration or calm interaction are impeded.",
    },
    {
        "key": "ptsd",
        "name": "Post-Traumatic Stress",
        "cost": -2,
        "description": "Choose a trigger category. When confronted, rolls to remain composed or act against the trigger are impeded.",
        "requires_detail": True,
        "detail_prompt": "Describe the trauma trigger (e.g., fire, captivity, medical procedures):",
    },
    {
        "key": "delusional_belief",
        "name": "Delusional Belief",
        "cost": -2,
        "description": "One fixed false belief that resists evidence. When relevant, rolls to interpret events objectively are impeded.",
        "requires_detail": True,
        "detail_prompt": "Describe the delusion:",
    },
]

# Mortal trait keys that qualify as mental illness (Malkavian requirement)
MENTAL_ILLNESS_KEYS: set[str] = {
    "paranoid",
    "dissociative_episodes",
    "depressive_episodes",
    "manic_episodes",
    "psychotic_episodes",
    "panic_disorder",
    "ptsd",
    "delusional_belief",
    "selective_mutism",
}

VAMPIRE_TRAITS: list[dict] = [
    {
        "key": "folkloric_bane",
        "name": "Folkloric Bane",
        "cost": -1,
        "max_times": 7,
        "description": "A classic vampiric weakness from folklore. Choose one each time you take this trait.",
        "requires_sub_choice": True,
        "sub_options": [
            "Weakness to garlic",
            "Willpower roll to enter homes uninvited",
            "Hearing ringing bells or crowing of a rooster causes 1 HP damage",
            "Willpower roll to cross running water",
            "Weakness to salt",
            "No mirror reflection",
            "Your shadow is uncanny: moves too late, in wrong directions",
        ],
    },
    {
        "key": "morph",
        "name": "Morph",
        "cost": 2,
        "description": "Can change your timeless appearance to adapt to the times. Spend 2 Blood per change consistent with some passage of time (up to 1 year). Changes apply and revert during daysleep.",
    },
    {
        "key": "prone_to_rage",
        "name": "Prone to Rage",
        "cost": -2,
        "description": "Suffer -2 to resist Rage Frenzy.",
    },
    {
        "key": "archaic",
        "name": "Archaic",
        "cost": -3,
        "description": "Cannot competently use modern technology. Computers, smartphones, elevators, cars — require assistance or a difficult roll.",
    },
    {
        "key": "ravenous",
        "name": "Ravenous",
        "cost": -3,
        "description": "Feeding without killing always requires a Willpower roll.",
    },
    {
        "key": "selective_taste",
        "name": "Selective Taste",
        "cost": None,
        "variable_cost": True,
        "cost_options": [
            (-1, "Broadly selective (e.g., 20-30 year old males)"),
            (-2, "Selective (e.g., a specific ethnicity or profession)"),
            (-3, "Very selective"),
            (-4, "Extremely selective"),
            (-5, "Near-impossible (e.g., only pregnant women)"),
        ],
        "description": "Only feed on a specific type of mortal. Feeding on others costs 1-5 Willpower depending on proximity to desired prey.",
        "requires_detail": True,
        "detail_prompt": "Describe your preferred prey type:",
    },
    {
        "key": "territorial",
        "name": "Territorial",
        "cost": -2,
        "description": "Every encroachment on your territory or property triggers a Rage Frenzy, or costs 2 Willpower.",
    },
    {
        "key": "stigmata",
        "name": "Stigmata",
        "cost": -1,
        "description": "Begin to bleed from your eyes when Blood reaches -4.",
    },
    {
        "key": "corpse_like",
        "name": "Corpse-Like",
        "cost": -2,
        "description": "Your appearance feels wrong and dead. Rolls relying on physical attractiveness or favorable first impressions are impeded.",
    },
    {
        "key": "iron_gullet",
        "name": "Iron Gullet",
        "cost": 2,
        "description": "Can feed from cold blood, rancid blood, and fractionated plasma.",
    },
    {
        "key": "dead_stillness",
        "name": "Dead Stillness",
        "cost": 1,
        "description": "Can remain perfectly motionless for any length of time. Casual observers mistake you for a corpse or statue.",
    },
    {
        "key": "scent_hound",
        "name": "Scent Hound",
        "cost": 2,
        "description": "Can smell fresh blood from several rooms away and distinguish individuals by the scent of their blood.",
    },
    {
        "key": "infatuation",
        "name": "Infatuation",
        "cost": -1,
        "description": "Easily emotionally bonded to mortals, caring about them deeply.",
    },
    {
        "key": "painful_bite",
        "name": "Painful Bite",
        "cost": -2,
        "description": "The Kiss doesn't work — mortals experience only pain when bitten. You can still close wounds afterwards.",
    },
]


def get_mortal_trait(key: str) -> dict | None:
    return next((t for t in MORTAL_TRAITS if t["key"] == key), None)


def get_vampire_trait(key: str) -> dict | None:
    return next((t for t in VAMPIRE_TRAITS if t["key"] == key), None)
