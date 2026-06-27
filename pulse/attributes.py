from __future__ import annotations

from collections import Counter

from pulse.constants import (
    ATTRIBUTES,
    BASE_ATTRIBUTE_VALUE,
    TARGET_DISTRIBUTION,
)


def compute_attributes(traits: list[dict[str, str]]) -> dict[str, int]:
    """Apply traits to base-2 attributes."""
    attrs = {name: BASE_ATTRIBUTE_VALUE for name in ATTRIBUTES}
    for trait in traits:
        plus = trait.get("plus")
        minus = trait.get("minus")
        if plus in attrs:
            attrs[plus] += 1
        if minus in attrs:
            attrs[minus] -= 1
    return attrs


def distribution_valid(attrs: dict[str, int]) -> bool:
    counts = Counter(attrs.values())
    return (
        counts.get(3, 0) == TARGET_DISTRIBUTION[3]
        and counts.get(2, 0) == TARGET_DISTRIBUTION[2]
        and counts.get(1, 0) == TARGET_DISTRIBUTION[1]
    )


def sync_mortal_attributes(character: dict) -> None:
    mortal = character.setdefault("mortal", {})
    mortal["attributes"] = compute_attributes(mortal.get("traits", []))
