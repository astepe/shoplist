"""
Business logic services for conversion, aggregation, and shopping list generation.
"""
import math
from typing import Any, Optional
from backend.database import get_db


def convert_standard_volume(from_unit_id, to_unit_id, quantity, db=None):
    """
    Convert between standard volume units using standard conversions.
    Only works for volume units (cup, tablespoon, teaspoon, fluid_ounce, milliliter).
    
    Args:
        from_unit_id: ID of source unit
        to_unit_id: ID of target unit
        quantity: Quantity to convert
        db: Optional database connection
        
    Returns:
        Converted quantity or None if conversion not possible
    """
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        
        # Get unit names and categories
        cursor.execute("SELECT id, name, category FROM unit_types WHERE id IN (?, ?)", 
                      (from_unit_id, to_unit_id))
        units = {row['id']: row for row in cursor.fetchall()}
        
        if from_unit_id not in units or to_unit_id not in units:
            return None
        
        from_unit = units[from_unit_id]
        to_unit = units[to_unit_id]
        
        # Only convert between volume units
        if from_unit['category'] != 'volume' or to_unit['category'] != 'volume':
            return None
        
        # Standard volume conversions (all to teaspoons as base)
        # 1 cup = 48 teaspoons
        # 1 tablespoon = 3 teaspoons
        # 1 fluid_ounce = 6 teaspoons
        # 1 milliliter ≈ 0.202884 teaspoons (1 ml = 0.202884 tsp)
        
        # Convert to teaspoons first
        tsp_per_unit = {
            'cup': 48.0,
            'tablespoon': 3.0,
            'teaspoon': 1.0,
            'fluid_ounce': 6.0,
            'milliliter': 0.202884,  # Approximate
        }
        
        from_name = from_unit['name'].lower()
        to_name = to_unit['name'].lower()
        
        if from_name not in tsp_per_unit or to_name not in tsp_per_unit:
            return None
        
        # Convert: from_unit → teaspoons → to_unit
        teaspoons = quantity * tsp_per_unit[from_name]
        result = teaspoons / tsp_per_unit[to_name]
        
        return result
    
    finally:
        if close_after:
            db.close()


def convert_to_shopping_unit(ingredient_id, quantity, from_unit_id, db=None):
    """
    Convert a quantity from recipe unit to shopping unit.
    
    Args:
        ingredient_id: ID of the ingredient
        quantity: Quantity in recipe unit
        from_unit_id: ID of the recipe unit
        db: Optional database connection
        
    Returns:
        Tuple of (shopping_quantity, shopping_unit_id) or None if no conversion rule found
    """
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        
        # Get ingredient's shopping unit
        cursor.execute("SELECT shopping_unit_id FROM ingredients WHERE id = ?", (ingredient_id,))
        ingredient = cursor.fetchone()
        if not ingredient:
            return None
        
        shopping_unit_id = ingredient['shopping_unit_id']
        
        # If already in shopping unit, return as-is
        if from_unit_id == shopping_unit_id:
            return (quantity, shopping_unit_id)
        
        # Find conversion rule
        cursor.execute("""
            SELECT conversion_factor 
            FROM conversion_rules 
            WHERE ingredient_id = ? AND from_unit_id = ? AND to_unit_id = ?
        """, (ingredient_id, from_unit_id, shopping_unit_id))
        
        rule = cursor.fetchone()
        if not rule:
            return None
        
        conversion_factor = rule['conversion_factor']
        shopping_quantity = quantity * conversion_factor
        
        return (shopping_quantity, shopping_unit_id)
    
    finally:
        if close_after:
            db.close()


def estimate_size_qualifier(ingredient_id, total_weight_or_volume, pieces, reference_unit_id, db=None):
    """
    Estimate size qualifier based on aggregated amount.
    
    Args:
        ingredient_id: ID of the ingredient
        total_weight_or_volume: Total weight or volume in reference unit
        pieces: Number of pieces
        reference_unit_id: Unit ID of the reference (e.g., gram for weight)
        db: Optional database connection
        
    Returns:
        Size qualifier ('small', 'medium', 'large') or None
    """
    if pieces == 0:
        return None
    
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        
        # Get size estimation rules for this ingredient
        cursor.execute("""
            SELECT size_qualifier, reference_value
            FROM size_estimation_rules
            WHERE ingredient_id = ? AND reference_unit_id = ?
            ORDER BY reference_value
        """, (ingredient_id, reference_unit_id))
        
        rules = cursor.fetchall()
        if not rules:
            return None
        
        # Calculate average per piece
        avg_per_piece = total_weight_or_volume / pieces
        
        # Find closest matching size
        best_match = None
        min_diff = float('inf')
        
        for rule in rules:
            diff = abs(avg_per_piece - rule['reference_value'])
            if diff < min_diff:
                min_diff = diff
                best_match = rule['size_qualifier']
        
        return best_match
    
    finally:
        if close_after:
            db.close()


def check_circular_reference(recipe_id, sub_recipe_id, db=None):
    """
    Check if adding a sub-recipe would create a circular reference.
    
    Args:
        recipe_id: ID of the recipe that wants to add the sub-recipe
        sub_recipe_id: ID of the sub-recipe to be added
        db: Optional database connection
        
    Returns:
        True if circular reference would be created, False otherwise
    """
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        # Check if sub_recipe_id is in the chain of recipes that recipe_id depends on
        visited = set[Any]()
        cursor = db.cursor()
        
        def has_path_to_target(current_id, target_id):
            if current_id == target_id:
                return True
            if current_id in visited:
                return False
            
            visited.add(current_id)
            
            # Get all recipes that current_id uses as sub-recipes
            cursor.execute("""
                SELECT DISTINCT sub_recipe_id
                FROM recipe_items
                WHERE recipe_id = ? AND item_type = 'sub_recipe' AND sub_recipe_id IS NOT NULL
            """, (current_id,))
            
            for row in cursor.fetchall():
                if row['sub_recipe_id'] and has_path_to_target(row['sub_recipe_id'], target_id):
                    return True
            
            return False
        
        # Check if sub_recipe_id (or anything in its chain) leads back to recipe_id
        return has_path_to_target(sub_recipe_id, recipe_id)
    
    finally:
        if close_after:
            db.close()


def expand_sub_recipe(sub_recipe_id, needed_quantity, needed_unit_id, batch_multiplier, visited=None, db=None):
    """
    Recursively expand a sub-recipe to its base ingredients.
    
    Args:
        sub_recipe_id: ID of the sub-recipe to expand
        needed_quantity: Quantity needed from the sub-recipe
        needed_unit_id: Unit of the needed quantity
        batch_multiplier: Batch multiplier for the parent recipe
        visited: Set of visited recipe IDs (for circular reference detection)
        db: Optional database connection
        
    Returns:
        List of ingredient items with calculated quantities
    """
    if visited is None:
        visited = set[Any]()
    
    if sub_recipe_id in visited:
        raise ValueError(f"Circular reference detected with recipe {sub_recipe_id}")
    
    visited.add(sub_recipe_id)
    
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        
        # Get sub-recipe yield
        cursor.execute("""
            SELECT yield_quantity, yield_unit_id
            FROM recipes
            WHERE id = ?
        """, (sub_recipe_id,))
        
        recipe = cursor.fetchone()
        if not recipe:
            return []
        
        yield_quantity = recipe['yield_quantity']
        yield_unit_id = recipe['yield_unit_id']
        
        # Calculate proportion: how much of the sub-recipe do we need?
        # If needed_unit_id == yield_unit_id, direct proportion
        # Otherwise, we'd need unit conversion, but for now assume same unit type
        if needed_unit_id == yield_unit_id:
            proportion = needed_quantity / yield_quantity
        else:
            # For different units, assume 1:1 for now (could be enhanced)
            proportion = needed_quantity / yield_quantity
        
        # Get all items in the sub-recipe
        cursor.execute("""
            SELECT item_type, ingredient_id, sub_recipe_id, quantity, unit_id,
                   size_qualifier, preparation_notes
            FROM recipe_items
            WHERE recipe_id = ?
        """, (sub_recipe_id,))
        
        expanded_items = []
        
        for item in cursor.fetchall():
            # Calculate quantity with proportion and batch multiplier
            item_quantity = item['quantity'] * proportion * batch_multiplier
            
            if item['item_type'] == 'sub_recipe':
                # Recursively expand nested sub-recipes
                nested_items = expand_sub_recipe(
                    item['sub_recipe_id'],
                    item_quantity,
                    item['unit_id'],
                    batch_multiplier=1.0,  # Already multiplied
                    visited=visited.copy(),
                    db=db
                )
                expanded_items.extend(nested_items)
            else:
                # Base ingredient
                expanded_items.append({
                    'ingredient_id': item['ingredient_id'],
                    'quantity': item_quantity,
                    'unit_id': item['unit_id'],
                    'size_qualifier': item['size_qualifier'],
                    'preparation_notes': item['preparation_notes']
                })
        
        return expanded_items
    
    finally:
        if close_after:
            db.close()


def generate_shopping_list(recipe_selections, db=None):
    """
    Generate a shopping list from selected recipes and batch counts.
    
    Args:
        recipe_selections: List of dicts with 'recipe_id' and 'batches' keys
        db: Optional database connection
        
    Returns:
        List of shopping list items with ingredient name, quantity, unit, and size qualifier
    """
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        all_ingredients = []
        all_sub_recipes = []  # Track sub-recipes separately
        
        # Step 1: Collect base ingredients and sub-recipes (without expanding sub-recipes)
        for selection in recipe_selections:
            recipe_id = selection['recipe_id']
            batches = selection.get('batches', 1)
            
            # Get all items in the recipe
            cursor.execute("""
                SELECT item_type, ingredient_id, sub_recipe_id, quantity, unit_id,
                       size_qualifier, preparation_notes
                FROM recipe_items
                WHERE recipe_id = ?
            """, (recipe_id,))
            
            recipe_items = cursor.fetchall()
            
            for item in recipe_items:
                item_quantity = item['quantity'] * batches
                
                if item['item_type'] == 'sub_recipe':
                    # Don't expand sub-recipe - add it as-is to be shown separately
                    all_sub_recipes.append({
                        'sub_recipe_id': item['sub_recipe_id'],
                        'quantity': item_quantity,
                        'unit_id': item['unit_id'],
                        'size_qualifier': item['size_qualifier'],
                        'preparation_notes': item['preparation_notes']
                    })
                else:
                    # Base ingredient
                    all_ingredients.append({
                        'ingredient_id': item['ingredient_id'],
                        'quantity': item_quantity,
                        'unit_id': item['unit_id'],
                        'size_qualifier': item['size_qualifier'],
                        'preparation_notes': item['preparation_notes']
                    })
        
        # Step 2: Group by ingredient ID
        ingredient_groups = {}
        
        for item in all_ingredients:
            ingredient_id = item['ingredient_id']
            if ingredient_id not in ingredient_groups:
                ingredient_groups[ingredient_id] = []
            ingredient_groups[ingredient_id].append(item)
        
        # Step 2b: Group sub-recipes by recipe ID and aggregate quantities
        sub_recipe_groups = {}
        
        for item in all_sub_recipes:
            sub_recipe_id = item['sub_recipe_id']
            if sub_recipe_id not in sub_recipe_groups:
                sub_recipe_groups[sub_recipe_id] = []
            sub_recipe_groups[sub_recipe_id].append(item)
        
        # Get the "whole" unit ID (size qualifiers apply when shopping unit is "whole")
        cursor.execute("SELECT id FROM unit_types WHERE name = 'whole'")
        whole_unit_row = cursor.fetchone()
        whole_unit_id = whole_unit_row['id'] if whole_unit_row else None
        
        # Step 3: Process each ingredient group
        shopping_list = []
        
        for ingredient_id, items in ingredient_groups.items():
            # Get ingredient details
            cursor.execute("""
                SELECT i.name, i.shopping_unit_id, ut.name as shopping_unit_name,
                       ut.category as shopping_unit_category
                FROM ingredients i
                JOIN unit_types ut ON i.shopping_unit_id = ut.id
                WHERE i.id = ?
            """, (ingredient_id,))
            
            ingredient = cursor.fetchone()
            if not ingredient:
                continue
            
            # Aggregate ALL items together and estimate size qualifier based on total weight/volume
            # Strategy:
            # 1. Convert all items to a reference unit (weight/volume)
            # 2. Sum the total reference value
            # 3. Convert total to shopping units
            # 4. Estimate size qualifier based on average weight per piece
            
            total_shopping_quantity = 0
            total_reference_value = 0  # Total weight or volume in reference unit
            reference_unit_id = None
            
            # First, try to get a reference unit for size estimation (prefer weight)
            cursor.execute("""
                SELECT reference_unit_id FROM size_estimation_rules 
                WHERE ingredient_id = ? 
                ORDER BY 
                    CASE 
                        WHEN reference_unit_id IN (SELECT id FROM unit_types WHERE category = 'weight') THEN 1
                        WHEN reference_unit_id IN (SELECT id FROM unit_types WHERE category = 'volume') THEN 2
                        ELSE 3
                    END
                LIMIT 1
            """, (ingredient_id,))
            ref_rule = cursor.fetchone()
            if ref_rule:
                reference_unit_id = ref_rule['reference_unit_id']
            
            # Track original recipe quantities for packaged ingredients (to show actual volume/weight needed)
            # For ingredients where shopping unit is a container/package, we want to show the actual amount needed
            total_recipe_volume = 0  # Total in a standard volume unit (cup)
            total_recipe_weight = 0  # Total in a standard weight unit (gram)
            volume_unit_id = None
            weight_unit_id = None
            
            # Get standard volume and weight units
            cursor.execute("SELECT id FROM unit_types WHERE name = 'cup'")
            cup_unit = cursor.fetchone()
            volume_unit_id = cup_unit['id'] if cup_unit else None
            
            cursor.execute("SELECT id FROM unit_types WHERE name = 'gram'")
            gram_unit = cursor.fetchone()
            weight_unit_id = gram_unit['id'] if gram_unit else None
            
            # Check if shopping unit is a container/package type (for which we should show actual amounts)
            container_units = ['package', 'can', 'bottle', 'jar', 'container']
            is_container_unit = ingredient['shopping_unit_name'] in container_units
            
            # Convert all items to shopping unit AND to reference unit (if available)
            for item in items:
                # Convert to shopping unit
                result = convert_to_shopping_unit(
                    ingredient_id,
                    item['quantity'],
                    item['unit_id'],
                    db
                )
                
                if result:
                    item_shopping_quantity, shopping_unit_id = result
                    total_shopping_quantity += item_shopping_quantity
                    
                    # For container units, track actual volume/weight needed
                    if is_container_unit:
                        # Try to convert item quantity to volume (cup)
                        if volume_unit_id:
                            if item['unit_id'] == volume_unit_id:
                                total_recipe_volume += item['quantity']
                            else:
                                # Try direct conversion
                                cursor.execute("""
                                    SELECT conversion_factor FROM conversion_rules
                                    WHERE ingredient_id = ? 
                                    AND from_unit_id = ? 
                                    AND to_unit_id = ?
                                """, (ingredient_id, item['unit_id'], volume_unit_id))
                                vol_conv = cursor.fetchone()
                                if vol_conv:
                                    total_recipe_volume += item['quantity'] * vol_conv['conversion_factor']
                                else:
                                    # Try standard volume conversion (for volume units)
                                    standard_vol = convert_standard_volume(item['unit_id'], volume_unit_id, item['quantity'], db)
                                    if standard_vol is not None:
                                        total_recipe_volume += standard_vol
                                    else:
                                        # Try indirect: item_unit → shopping_unit → volume_unit
                                        # Use the item shopping quantity (converted from this item only)
                                        if item_shopping_quantity > 0:
                                            # Reverse convert from shopping unit to volume unit
                                            cursor.execute("""
                                                SELECT conversion_factor FROM conversion_rules
                                                WHERE ingredient_id = ? 
                                                AND from_unit_id = ? 
                                                AND to_unit_id = ?
                                            """, (ingredient_id, volume_unit_id, shopping_unit_id))
                                            reverse_conv = cursor.fetchone()
                                            if reverse_conv:
                                                # Reverse conversion: shopping → volume
                                                # item_shopping_quantity is packages, reverse_conv is cup→package
                                                # So: packages / (cup→package) = cups
                                                item_volume = item_shopping_quantity / reverse_conv['conversion_factor']
                                                total_recipe_volume += item_volume
                        
                        # Try to convert item quantity to weight (gram)
                        if weight_unit_id:
                            if item['unit_id'] == weight_unit_id:
                                total_recipe_weight += item['quantity']
                            else:
                                # Try direct conversion
                                cursor.execute("""
                                    SELECT conversion_factor FROM conversion_rules
                                    WHERE ingredient_id = ? 
                                    AND from_unit_id = ? 
                                    AND to_unit_id = ?
                                """, (ingredient_id, item['unit_id'], weight_unit_id))
                                wt_conv = cursor.fetchone()
                                if wt_conv:
                                    total_recipe_weight += item['quantity'] * wt_conv['conversion_factor']
                                else:
                                    # Try indirect: item_unit → shopping_unit → weight_unit
                                    # Use the item shopping quantity (converted from this item only)
                                    if item_shopping_quantity > 0:
                                        # Reverse convert from shopping unit to weight unit
                                        cursor.execute("""
                                            SELECT conversion_factor FROM conversion_rules
                                            WHERE ingredient_id = ? 
                                            AND from_unit_id = ? 
                                            AND to_unit_id = ?
                                        """, (ingredient_id, weight_unit_id, shopping_unit_id))
                                        reverse_conv = cursor.fetchone()
                                        if reverse_conv:
                                            # Reverse conversion: shopping → weight
                                            # item_shopping_quantity is packages, reverse_conv is gram→package
                                            # So: packages / (gram→package) = grams
                                            item_weight = item_shopping_quantity / reverse_conv['conversion_factor']
                                            total_recipe_weight += item_weight
                    
                    # If we have a reference unit, also convert to that for size estimation
                    if reference_unit_id:
                        item_ref_value = 0
                        
                        # Check if item has a size qualifier (count units with size qualifiers)
                        if item['size_qualifier']:
                            # Get the reference value for this size qualifier
                            cursor.execute("""
                                SELECT reference_value FROM size_estimation_rules
                                WHERE ingredient_id = ? 
                                AND reference_unit_id = ?
                                AND size_qualifier = ?
                            """, (ingredient_id, reference_unit_id, item['size_qualifier']))
                            size_rule = cursor.fetchone()
                            
                            if size_rule:
                                # For each piece, use the size's reference value
                                # Since item_shopping_quantity is already converted to pieces,
                                # multiply by the reference value for this size
                                item_ref_value = item_shopping_quantity * size_rule['reference_value']
                            else:
                                # Size qualifier doesn't have a rule, skip this item's reference value
                                pass
                        elif item['unit_id'] == reference_unit_id:
                            # Item is already in reference unit (weight/volume)
                            item_ref_value = item['quantity']
                        else:
                            # Try to convert item's unit to reference unit
                            # Check if there's a conversion path from item's unit to reference unit
                            cursor.execute("""
                                SELECT conversion_factor FROM conversion_rules
                                WHERE ingredient_id = ? 
                                AND from_unit_id = ? 
                                AND to_unit_id = ?
                            """, (ingredient_id, item['unit_id'], reference_unit_id))
                            direct_conv = cursor.fetchone()
                            
                            if direct_conv:
                                # Direct conversion exists
                                item_ref_value = item['quantity'] * direct_conv['conversion_factor']
                            else:
                                # Try indirect: item -> shopping_unit -> reference_unit
                                # First convert item to shopping unit (already have item_shopping_quantity)
                                # Then need conversion from shopping unit to reference unit
                                cursor.execute("""
                                    SELECT conversion_factor FROM conversion_rules
                                    WHERE ingredient_id = ? 
                                    AND from_unit_id = ? 
                                    AND to_unit_id = ?
                                """, (ingredient_id, shopping_unit_id, reference_unit_id))
                                indirect_conv = cursor.fetchone()
                                
                                if indirect_conv:
                                    # Use item shopping quantity as intermediate
                                    item_ref_value = item_shopping_quantity * indirect_conv['conversion_factor']
                        
                        total_reference_value += item_ref_value
            
            # Round up total shopping quantity
            if total_shopping_quantity > 0:
                # Optimize size qualifier selection to minimize number of items needed
                # This is a knapsack-like problem: minimize items while covering total weight
                optimized_quantity = total_shopping_quantity
                optimized_size = None
                
                if (reference_unit_id and total_shopping_quantity > 0 and 
                    ingredient['shopping_unit_id'] == whole_unit_id):
                    # Get all size estimation rules, ordered by size (largest first)
                    cursor.execute("""
                        SELECT size_qualifier, reference_value
                        FROM size_estimation_rules
                        WHERE ingredient_id = ? AND reference_unit_id = ?
                        ORDER BY reference_value DESC
                    """, (ingredient_id, reference_unit_id))
                    
                    size_rules = cursor.fetchall()
                    
                    if size_rules and total_reference_value > 0:
                        # Calculate total weight needed (from reference value)
                        total_weight_needed = total_reference_value
                        
                        # Optimize to minimize number of items (knapsack-like problem)
                        # Strategy: Try all sizes to find the one that minimizes items needed
                        best_combination = None
                        min_items = float('inf')
                        
                        # For each size option, calculate how many items we'd need
                        for rule in size_rules:
                            # Calculate items needed using this size (round up to cover total weight)
                            items_needed = math.ceil(total_weight_needed / rule['reference_value'])
                            
                            # Track the best option (fewest items)
                            if items_needed < min_items:
                                min_items = items_needed
                                best_combination = (items_needed, rule['size_qualifier'])
                        
                        if best_combination:
                            optimized_quantity, optimized_size = best_combination
                        else:
                            # Fallback: estimate size based on average
                            optimized_quantity = math.ceil(total_shopping_quantity)
                            optimized_size = estimate_size_qualifier(
                                ingredient_id,
                                total_reference_value,
                                optimized_quantity,
                                reference_unit_id,
                                db
                            )
                    else:
                        # No size estimation rules, just round up
                        optimized_quantity = math.ceil(total_shopping_quantity)
                else:
                    # Not a "whole" unit or no reference unit, just round up
                    optimized_quantity = math.ceil(total_shopping_quantity)
                
                shopping_item = {
                    'ingredient_id': ingredient_id,
                    'ingredient_name': ingredient['name'],
                    'quantity': optimized_quantity,
                    'unit_id': ingredient['shopping_unit_id'],
                    'unit_name': ingredient['shopping_unit_name'],
                    'size_qualifier': optimized_size,
                    'preparation_notes': None  # Not preserved for aggregated items
                }
                
                # For container/package units, add the actual volume/weight needed
                if is_container_unit:
                    if total_recipe_volume > 0:
                        # Convert cups to fluid ounces for display (1 cup = 8 fl oz)
                        shopping_item['recipe_volume'] = total_recipe_volume * 8
                        shopping_item['recipe_volume_unit'] = 'fl oz'
                    if total_recipe_weight > 0:
                        shopping_item['recipe_weight'] = total_recipe_weight
                        shopping_item['recipe_weight_unit'] = 'gram'
                
                shopping_list.append(shopping_item)
        
        # Step 4: Process sub-recipes as separate shopping list items
        for sub_recipe_id, items in sub_recipe_groups.items():
            # Get sub-recipe details
            cursor.execute("""
                SELECT r.name, r.yield_quantity, r.yield_unit_id,
                       ut.name as yield_unit_name
                FROM recipes r
                JOIN unit_types ut ON r.yield_unit_id = ut.id
                WHERE r.id = ?
            """, (sub_recipe_id,))
            
            sub_recipe = cursor.fetchone()
            if not sub_recipe:
                continue
            
            # Aggregate quantities by unit
            # Group by unit_id to handle cases where the same sub-recipe is requested in different units
            quantities_by_unit = {}
            
            for item in items:
                unit_id = item['unit_id']
                if unit_id not in quantities_by_unit:
                    quantities_by_unit[unit_id] = 0
                quantities_by_unit[unit_id] += item['quantity']
            
            # For each unit, create a shopping list item
            for unit_id, total_quantity in quantities_by_unit.items():
                # Get unit name
                cursor.execute("SELECT name FROM unit_types WHERE id = ?", (unit_id,))
                unit_row = cursor.fetchone()
                unit_name = unit_row['name'] if unit_row else 'unit'
                
                sub_recipe_item = {
                    'is_sub_recipe': True,
                    'sub_recipe_id': sub_recipe_id,
                    'sub_recipe_name': sub_recipe['name'],
                    'quantity': total_quantity,
                    'unit_id': unit_id,
                    'unit_name': unit_name,
                    'yield_quantity': sub_recipe['yield_quantity'],
                    'yield_unit_name': sub_recipe['yield_unit_name'],
                    'size_qualifier': None,
                    'preparation_notes': None
                }
                
                shopping_list.append(sub_recipe_item)
        
        # Sort: sub-recipes first (with badge), then ingredients
        def sort_key(item):
            if item.get('is_sub_recipe'):
                return (0, item.get('sub_recipe_name', ''))
            else:
                return (1, item.get('ingredient_name', ''))
        
        shopping_list.sort(key=sort_key)
        
        return shopping_list
    
    finally:
        if close_after:
            db.close()


def get_store_section(ingredient_name, ingredient_type_name, shopping_unit_name, db=None):
    """
    Determine grocery store section for an ingredient.
    
    Args:
        ingredient_name: Name of the ingredient (e.g., "Fresh Mango", "Frozen Blueberries")
        ingredient_type_name: Ingredient type name (e.g., "Fruits", "Vegetables")
        shopping_unit_name: Shopping unit name (e.g., "whole", "package", "can")
        db: Optional database connection
        
    Returns: 
        'produce', 'dry_bulk', 'canned_preserved', 'refrigerated', 'frozen'
    """
    name_lower = ingredient_name.lower()
    type_lower = ingredient_type_name.lower()
    unit_lower = shopping_unit_name.lower()
    
    # FROZEN - highest priority (explicit in name)
    if 'frozen' in name_lower:
        return 'frozen'
    
    # REFRIGERATED - check before produce (milk, tempeh, tortillas, miso paste)
    if 'milk' in name_lower or 'tempeh' in name_lower or 'tortilla' in name_lower:
        return 'refrigerated'
    # Miso paste is refrigerated
    if 'miso' in name_lower:
        return 'refrigerated'
    if type_lower == 'liquids':
        # Most liquids in this system are plant-based milks (refrigerated)
        return 'refrigerated'
    
    # PRODUCE
    # Fresh ginger and garlic go to produce (even though they're in Spices type)
    if 'fresh ginger' in name_lower or (name_lower == 'ginger' and 'fresh' not in name_lower):
        return 'produce'
    if name_lower == 'garlic' or (name_lower.startswith('garlic') and 'powder' not in name_lower and 'salt' not in name_lower):
        return 'produce'
    
    if type_lower == 'vegetables' and 'frozen' not in name_lower:
        return 'produce'
    if type_lower == 'fruits':
        # Fresh fruits go to produce, frozen go to frozen (already handled above)
        if 'frozen' not in name_lower:
            return 'produce'
    if type_lower == 'herbs':
        # Fresh herbs go to produce, dried go to dry_bulk
        if 'fresh' in name_lower or 'dried' not in name_lower:
            return 'produce'
    
    # DRY/BULK (includes baking section)
    # Vanilla extract goes to dry/bulk (baking section)
    if 'vanilla extract' in name_lower or 'vanilla' in name_lower:
        return 'dry_bulk'
    
    if type_lower in ['grains', 'nuts & seeds', 'spices']:
        return 'dry_bulk'
    if type_lower == 'herbs' and 'dried' in name_lower:
        return 'dry_bulk'
    if type_lower == 'pantry items':
        # Check for dry goods patterns
        dry_keywords = ['flour', 'sugar', 'yeast', 'oats', 'rice', 'quinoa', 'barley', 
                       'millet', 'farro', 'buckwheat', 'lentil']
        if any(word in name_lower for word in dry_keywords):
            # Make sure it's not canned - exclude canned beans/lentils
            if not any(canned_word in name_lower for canned_word in ['canned', 'can', 'salt-free']):
                return 'dry_bulk'
    
    # CANNED/PRESERVED
    if type_lower == 'pantry items':
        # Canned/jarred items
        if unit_lower in ['can', 'jar', 'bottle']:
            return 'canned_preserved'
        if any(word in name_lower for word in ['salt-free', 'canned', 'crushed', 'diced', 
                                               'marinara', 'tahini', 'molasses', 
                                               'vinegar', 'sauce']):
            # Note: miso is handled above as refrigerated
            return 'canned_preserved'
    
    # PLANT PROTEINS - most are canned/preserved (beans) or refrigerated (tempeh)
    if type_lower == 'plant proteins':
        if 'tempeh' in name_lower:
            return 'refrigerated'
        # Most others are canned beans
        return 'canned_preserved'
    
    # Default fallback
    return 'dry_bulk'  # Safe default for unclassified items


def organize_shopping_list_by_sections(shopping_list, db=None):
    """
    Organize shopping list items by grocery store sections.
    
    Args:
        shopping_list: List of shopping list items from generate_shopping_list()
        db: Optional database connection
        
    Returns:
        Dictionary mapping section names to arrays of items:
        {
            'produce': [...],
            'dry_bulk': [...],
            'canned_preserved': [...],
            'refrigerated': [...],
            'frozen': [...],
            'sub_recipes': [...]
        }
    """
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        organized = {
            'produce': [],
            'dry_bulk': [],
            'canned_preserved': [],
            'refrigerated': [],
            'frozen': [],
            'sub_recipes': []
        }
        
        # Get ingredient details for each item
        for item in shopping_list:
            # Sub-recipes go to separate section
            if item.get('is_sub_recipe'):
                organized['sub_recipes'].append(item)
                continue
            
            # Get ingredient type and shopping unit
            ingredient_id = item.get('ingredient_id')
            if not ingredient_id:
                # Skip items without ingredient_id
                continue
            
            cursor.execute("""
                SELECT i.name as ingredient_name, it.name as type_name, ut.name as shopping_unit_name
                FROM ingredients i
                JOIN ingredient_types it ON i.type_id = it.id
                JOIN unit_types ut ON i.shopping_unit_id = ut.id
                WHERE i.id = ?
            """, (ingredient_id,))
            
            ingredient_info = cursor.fetchone()
            if not ingredient_info:
                continue
            
            # Determine section
            section = get_store_section(
                ingredient_info['ingredient_name'],
                ingredient_info['type_name'],
                ingredient_info['shopping_unit_name'],
                db
            )
            
            organized[section].append(item)
        
        # Sort each section alphabetically by ingredient/sub-recipe name
        for section in organized:
            organized[section].sort(key=lambda x: (
                x.get('ingredient_name', '') or 
                x.get('sub_recipe_name', '')
            ).lower())
        
        return organized
    
    finally:
        if close_after:
            db.close()


def get_item_id(item):
    """Generate a unique ID for an item (matches frontend logic)."""
    if item.get('is_sub_recipe'):
        return f"subrecipe-{item.get('sub_recipe_id')}-{item.get('quantity')}-{item.get('unit_id')}"
    else:
        return f"ingredient-{item.get('ingredient_id')}-{item.get('quantity')}-{item.get('unit_id')}-{item.get('size_qualifier') or ''}"

def format_shopping_list_text(organized_list, recipes_info=None, checked_item_ids=None, shopping_list=None):
    """
    Format organized shopping list as SMS-friendly text.
    
    Args:
        organized_list: Dictionary from organize_shopping_list_by_sections()
        recipes_info: Optional list of recipe info dicts
        checked_item_ids: Optional list of checked item IDs (from frontend)
        shopping_list: Optional full shopping list to match IDs against
        
    Returns:
        Formatted string ready for SMS
    """
    # Build a set of checked item IDs for quick lookup
    checked_set = set(checked_item_ids) if checked_item_ids else set()
    
    # If we have a shopping list, map IDs to items
    checked_items_by_id = {}
    if shopping_list and checked_set:
        for item in shopping_list:
            item_id = get_item_id(item)
            if item_id in checked_set:
                checked_items_by_id[item_id] = item
    
    sections = [
        ('produce', '🥬 PRODUCE'),
        ('dry_bulk', '📦 DRY/BULK GOODS'),
        ('canned_preserved', '🥫 CANNED/PRESERVED'),
        ('refrigerated', '🥛 REFRIGERATED'),
        ('frozen', '❄️ FROZEN'),
        ('sub_recipes', '🔄 SUB-RECIPES'),
    ]
    
    lines = ['🛒 Shopping List', '']  # Header
    
    # Separate items into "need to buy" and "already have"
    need_to_buy = {}
    already_have = {}
    
    for section_key, section_header in sections:
        items = organized_list.get(section_key, [])
        if not items:
            continue
        
        need_to_buy[section_key] = []
        already_have[section_key] = []
        
        for item in items:
            item_id = get_item_id(item)
            if item_id in checked_set:
                already_have[section_key].append(item)
            else:
                need_to_buy[section_key].append(item)
    
    # Format "Need to Buy" section
    has_items_to_buy = any(items for items in need_to_buy.values())
    if has_items_to_buy:
        lines.append('🛒 NEED TO BUY')
        lines.append('')
        
        for section_key, section_header in sections:
            items = need_to_buy.get(section_key, [])
            if not items:
                continue
            
            lines.append(section_header)
            
            for item in items:
                line = format_item_line(item)
                lines.append(line)
            
            lines.append('')  # Blank line between sections
    
    # Format "Already Have" section
    has_items_already = any(items for items in already_have.values())
    if has_items_already:
        if has_items_to_buy:
            lines.append('')  # Extra blank line before "Already Have"
        lines.append('✅ ALREADY HAVE')
        lines.append('')
        
        for section_key, section_header in sections:
            items = already_have.get(section_key, [])
            if not items:
                continue
            
            lines.append(section_header)
            
            for item in items:
                line = format_item_line(item)
                lines.append(line)
            
            lines.append('')  # Blank line between sections
    
    # Append recipes used (if provided)
    if recipes_info:
        lines.append('📖 RECIPES USED')
        for r in recipes_info:
            name = r.get('name', 'Unknown')
            page = r.get('page_number')
            if page:
                lines.append(f"• {name} (p. {page})")
            else:
                lines.append(f"• {name}")
        lines.append('')
    
    return '\n'.join(lines)


def format_item_line(item):
    """Format a single shopping list item as a line of text."""
    if item.get('is_sub_recipe'):
        # Format sub-recipe
        quantity = item.get('quantity', 0)
        unit_name = item.get('unit_name', '')
        sub_recipe_name = item.get('sub_recipe_name', 'Unknown Recipe')
        yield_quantity = item.get('yield_quantity', 0)
        yield_unit_name = item.get('yield_unit_name', '')
        
        # Format quantity (remove trailing zeros for whole numbers)
        qty_str = f"{quantity:.0f}" if quantity == int(quantity) else str(quantity)
        
        line = f"• {qty_str} {unit_name} {sub_recipe_name}"
        if yield_quantity and yield_unit_name:
            yield_str = f"{yield_quantity:.0f}" if yield_quantity == int(yield_quantity) else str(yield_quantity)
            line += f" (yields {yield_str} {yield_unit_name})"
        
        return line
    else:
        # Format regular ingredient
        quantity = item.get('quantity', 0)
        unit_name = item.get('unit_name', '')
        ingredient_name = item.get('ingredient_name', 'Unknown')
        size_qualifier = item.get('size_qualifier')
        
        # Format quantity
        qty_str = f"{quantity:.0f}" if quantity == int(quantity) else str(quantity)
        
        # Build line
        if size_qualifier:
            line = f"• {qty_str} {size_qualifier} {unit_name} {ingredient_name}"
        else:
            line = f"• {qty_str} {unit_name} {ingredient_name}"
        
        # Add need amount for container items
        recipe_volume = item.get('recipe_volume')
        recipe_weight = item.get('recipe_weight')
        if recipe_volume or recipe_weight:
            details = []
            if recipe_volume:
                vol = float(recipe_volume)
                vol_str = f"{vol:.2f}" if vol < 1 else f"{vol:.1f}"
                details.append(f"{vol_str} {item.get('recipe_volume_unit', 'fl oz')}")
            if recipe_weight:
                wt = float(recipe_weight)
                wt_str = f"{wt:.2f}" if wt < 1 else f"{wt:.1f}"
                details.append(f"{wt_str} {item.get('recipe_weight_unit', 'g')}")
            if details:
                line += f" (need: {', '.join(details)})"
        
        return line


def send_sms_shopping_list(phone_number, text, twilio_sid=None, twilio_token=None, twilio_from=None):
    """
    Send formatted shopping list via SMS using Twilio.
    
    Args:
        phone_number: Phone number in E.164 format (e.g., "+15551234567")
        text: Formatted shopping list text
        twilio_sid: Twilio Account SID (from environment if None)
        twilio_token: Twilio Auth Token (from environment if None)
        twilio_from: Twilio phone number to send from (from environment if None)
        
    Returns:
        Dictionary with 'success' (bool), 'message_sid' (str), and 'error' (str if failed)
    """
    import os
    
    try:
        from twilio.rest import Client
    except ImportError:
        return {
            'success': False,
            'error': 'Twilio package not installed. Please install with: pip install twilio'
        }
    
    # Get credentials from environment or parameters
    account_sid = twilio_sid or os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = twilio_token or os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = twilio_from or os.environ.get('TWILIO_PHONE_NUMBER')
    
    if not account_sid or not auth_token:
        return {
            'success': False,
            'error': 'Twilio credentials not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.'
        }
    
    if not from_number:
        # Try to use trial number format or fetch from Twilio
        # For now, return error if not provided
        return {
            'success': False,
            'error': 'Twilio phone number not configured. Please set TWILIO_PHONE_NUMBER environment variable.'
        }
    
    try:
        client = Client(account_sid, auth_token)
        
        # Twilio automatically handles message splitting for long messages
        message = client.messages.create(
            body=text,
            from_=from_number,
            to=phone_number
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'message': 'Shopping list sent successfully'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to send SMS: {str(e)}'
        }
