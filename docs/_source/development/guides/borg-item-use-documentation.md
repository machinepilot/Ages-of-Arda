---
title: Borg Item Use Documentation
id: borg-item-use-documentation
section: development
category: guides
created: '2025-03-14'
updated: '2025-03-14'
version: 0.1.0
---


# Borg Item Use Documentation

## File Overview

`borg-item-use.h` is a header file that is part of the Borg AI system in Angband. It contains function declarations and enums related to the Borg's decision-making process for using items such as potions, scrolls, wands, staves, rods, rings, and dragon armor. The functions in this file implement the logic for the Borg to determine when and how to use these items effectively.

## Data Structures

### enum borg_need

An enumeration representing the Borg's need for using an item.

- `BORG_NO_NEED`: The Borg does not need to use the item.
- `BORG_MET_NEED`: The Borg's need for the item has been met.
- `BORG_UNMET_NEED`: The Borg has an unmet need for the item.

## Global Variables

This header file does not contain any global variables.

## Functions

### borg_quaff_crit(bool no_check)

- **Purpose**: Attempt to quaff a potion of cure critical wounds.
- **Parameters**:
  - `no_check` (bool): If true, skip certain checks before quaffing the potion.
- **Return value**: True if the potion was successfully quaffed, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the potion is quaffed.

### borg_quaff_potion(int sval)

- **Purpose**: Attempt to quaff the given potion (identified by its sval).
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the potion to quaff.
- **Return value**: True if the potion was successfully quaffed, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the potion is quaffed.

### borg_quaff_unknown()

- **Purpose**: Attempt to quaff an unknown potion.
- **Parameters**: None.
- **Return value**: True if an unknown potion was successfully quaffed, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if a potion is quaffed.

### borg_read_scroll(int sval)

- **Purpose**: Attempt to read the given scroll (identified by its sval).
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the scroll to read.
- **Return value**: True if the scroll was successfully read, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the scroll is read.

### borg_read_unknown()

- **Purpose**: Attempt to read an unknown scroll.
- **Parameters**: None.
- **Return value**: True if an unknown scroll was successfully read, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if a scroll is read.

### borg_eat(int tval, int sval)

- **Purpose**: Attempt to eat the given food or mushroom.
- **Parameters**:
  - `tval` (int): The tval (type) of the item to eat (food or mushroom).
  - `sval` (int): The sval (sub-type) of the item to eat.
- **Return value**: True if the item was successfully eaten, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the item is eaten.

### borg_eat_unknown()

- **Purpose**: Attempt to eat an unknown food or mushroom.
- **Parameters**: None.
- **Return value**: True if an unknown food or mushroom was successfully eaten, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if an item is eaten.

### borg_eat_food_any()

- **Purpose**: Prevent starvation by any means possible (eating any food or mushroom).
- **Parameters**: None.
- **Return value**: True if the Borg successfully ate something to prevent starvation, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if an item is eaten.

### borg_equips_rod(int sval)

- **Purpose**: Check if the Borg is currently equipped with a rod of the given sval.
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the rod to check for.
- **Return value**: True if the Borg is equipped with the specified rod, false otherwise.

### borg_zap_rod(int sval)

- **Purpose**: Attempt to zap (use) the given charged rod (identified by its sval).
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the rod to zap.
- **Return value**: True if the rod was successfully zapped, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the rod is zapped.

### borg_use_staff(int sval)

- **Purpose**: Attempt to use the given charged staff (identified by its sval).
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the staff to use.
- **Return value**: True if the staff was successfully used, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the staff is used.

### borg_use_unknown()

- **Purpose**: Attempt to use an unknown staff.
- **Parameters**: None.
- **Return value**: True if an unknown staff was successfully used, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if a staff is used.

### borg_use_staff_fail(int sval)

- **Purpose**: Attempt to use the given charged staff (identified by its sval) and make a failure check on it.
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the staff to use.
- **Return value**: True if the staff was successfully used (and passed the failure check), false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the staff is used.

### borg_equips_staff_fail(int sval)

- **Purpose**: Check if the Borg is currently equipped with a staff of the given sval and make a "will I fail" check on it.
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the staff to check for.
- **Return value**: True if the Borg is equipped with the specified staff and it passes the failure check, false otherwise.

### borg_aim_wand(int sval)

- **Purpose**: Attempt to aim (use) the given charged wand (identified by its sval).
- **Parameters**:
  - `sval` (int): The sval (sub-type) of the wand to aim.
- **Return value**: True if the wand was successfully aimed, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the wand is aimed.

### borg_equips_ring(int ring_sval)

- **Purpose**: Check if the Borg is currently equipped with a ring of the given sval and make a failure check on it.
- **Parameters**:
  - `ring_sval` (int): The sval (sub-type) of the ring to check for.
- **Return value**: True if the Borg is equipped with the specified ring and it passes the failure check, false otherwise.

### borg_activate_ring(int ring_sval)

- **Purpose**: Attempt to activate (use) the given ring (identified by its sval).
- **Parameters**:
  - `ring_sval` (int): The sval (sub-type) of the ring to activate.
- **Return value**: True if the ring was successfully activated, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the ring is activated.

### borg_equips_dragon(int drag_sval)

- **Purpose**: Check if the Borg is currently equipped with dragon armor of the given sval and make a failure check on it.
- **Parameters**:
  - `drag_sval` (int): The sval (sub-type) of the dragon armor to check for.
- **Return value**: True if the Borg is equipped with the specified dragon armor and it passes the failure check, false otherwise.

### borg_activate_dragon(int drag_sval)

- **Purpose**: Attempt to activate (use) the given dragon armor (identified by its sval).
- **Parameters**:
  - `drag_sval` (int): The sval (sub-type) of the dragon armor to activate.
- **Return value**: True if the dragon armor was successfully activated, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the dragon armor is activated.

### borg_activate_item(int activation)

- **Purpose**: Attempt to activate (use) the given item (identified by its activation effect).
- **Parameters**:
  - `activation` (int): The activation effect of the item to use.
- **Return value**: True if the item was successfully activated, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if the item is activated.

### borg_equips_item(int activation, bool check_charge)

- **Purpose**: Check if the Borg is currently equipped with an item that has the given activation effect.
- **Parameters**:
  - `activation` (int): The activation effect to check for.
  - `check_charge` (bool): If true, also check if the item is charged (has enough charges to be used).
- **Return value**: True if the Borg is equipped with an item that has the specified activation effect (and is charged, if `check_charge` is true), false otherwise.

### borg_activate_failure(int tval, int sval)

- **Purpose**: Return the relative chance for failure when activating an item of the given tval and sval.
- **Parameters**:
  - `tval` (int): The tval (type) of the item.
  - `sval` (int): The sval (sub-type) of the item.
- **Return value**: An integer representing the relative chance of failure when activating the item (higher values indicate a higher chance of failure).

### borg_use_things()

- **Purpose**: Use things (items) in a useful, but non-essential, manner.
- **Parameters**: None.
- **Return value**: True if the Borg successfully used one or more items, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if items are used.

### borg_recharging()

- **Purpose**: Attempt to recharge items (wands, staves, rods) in the Borg's inventory.
- **Parameters**: None.
- **Return value**: True if the Borg successfully recharged one or more items, false otherwise.
- **Side effects**: The Borg's state and inventory are updated if items are recharged.

## Algorithms

The functions in this file implement various decision-making algorithms for the Borg AI to determine when and how to use items effectively. These algorithms take into account factors such as the Borg's current state, inventory, and the specific effects of each item type.

The item usage logic is based on the Borg's assessment of its needs and the potential benefits and risks associated with using each item. The Borg considers aspects such as healing, buffing, escaping dangerous situations, and maintaining its overall survivability and performance.

## Dependencies

This header file depends on the following files:
- `angband.h`: The main Angband header file, which must be included before this file.

Other files in the Borg AI system may depend on this header file to access the item usage functions and enums.

## Historical Context

The Borg AI system was developed as an autonomous player for Angband, designed to make intelligent decisions and navigate the game's challenges effectively. The item usage logic implemented in this file is a critical component of the Borg's decision-making process, enabling it to use items strategically to improve its chances of survival and success.

The code in this file has evolved over time, with contributions from various developers, including Ben Harrison, James E. Wilson, Robert A. Koeneke, Andi Sidwell, Chris Carr, Ed Graham, and Erik Osheim, among others. The copyright notices at the beginning of the file acknowledge their contributions and the licensing terms under which the code is distributed.