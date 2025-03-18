# File: borg-home-notice.h

## File Overview

The `borg-home-notice.h` header file is part of the Borg AI system in the Angband roguelike game. It declares global variables used to track various item quantities and bonuses in the player's home inventory. The Borg AI uses this information to make decisions about item management and character optimization.

## Data Structures

There are no structs or typedefs defined in this file.

## Global Variables

The file declares several global variables to track item quantities and bonuses:

- `num_food`: Number of food rations.
- `num_fuel`: Number of light sources (torches, lanterns).
- `num_mold`: Number of molds (for Warrior priests).
- `num_ident`: Number of identify scrolls.
- `num_recall`: Number of recall scrolls.
- `num_phase`: Number of phase door scrolls.
- `num_escape`: Number of teleport scrolls.
- `num_tele_staves`: Number of teleport staves.
- `num_teleport`: Number of teleport items (scrolls, staves, etc.).
- `num_berserk`: Number of berserk potions.
- `num_teleport_level`: Number of teleport level items.
- `num_recharge`: Number of recharge staves.
- `num_cure_critical`: Number of cure critical wounds potions.
- `num_cure_serious`: Number of cure serious wounds potions.
- `num_pot_rheat`: Number of resist heat potions.
- `num_pot_rcold`: Number of resist cold potions.
- `num_missile`: Number of missile items (arrows, bolts, etc.).
- `num_book`: Array tracking the number of spellbooks for each spell realm.
- `num_fix_stat`: Array tracking the number of stat restoration potions for each stat.
- `home_stat_add`: Array tracking the total stat bonuses from home inventory items.
- `num_fix_exp`: Number of restore experience potions.
- `num_mana`: Number of restore mana potions.
- `num_heal`: Number of healing potions.
- `num_heal_true`: Number of *healing* potions.
- `num_ezheal`: Number of life potions.
- `num_ezheal_true`: Number of *life* potions.
- `num_life`: Number of life restoration items (potions, scrolls, etc.).
- `num_life_true`: Number of *life restoration* items (potions, scrolls, etc.).
- `num_pfe`: Number of protection from evil scrolls.
- `num_glyph`: Number of glyph of warding scrolls.
- `num_enchant_to_a`: Number of enchant armor scrolls.
- `num_enchant_to_d`: Number of enchant weapon to damage scrolls.
- `num_enchant_to_h`: Number of enchant weapon to hit scrolls.
- `num_brand_weapon`: Number of *branding* items (scrolls, etc.).
- `num_genocide`: Number of genocide scrolls.
- `num_mass_genocide`: Number of mass genocide scrolls.
- `num_artifact`: Number of artifacts in home inventory.
- `num_ego`: Number of ego items in home inventory.
- `home_slot_free`: Number of free slots in home inventory.
- `home_un_id`: Number of unidentified items in home inventory.
- `home_damage`: Total damage value from home melee weapons.
- `num_duplicate_items`: Number of duplicate items in home inventory.

(Continued in next message...)