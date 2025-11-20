#!/usr/bin/env python3
"""
Script to add ingredients for Vegetable Broth 2.0 recipe.
This script:
1. Removes generic "Onion" and "Tomato" ingredients (migrating Onion references first)
2. Adds all new ingredients with conversion rules
3. Updates existing ingredients if needed
"""

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import get_db

def get_unit_id(name, cursor):
    """Get unit type ID by name."""
    cursor.execute("SELECT id FROM unit_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Unit '{name}' not found")
    return result['id']

def get_type_id(name, cursor):
    """Get ingredient type ID by name."""
    cursor.execute("SELECT id FROM ingredient_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Ingredient type '{name}' not found")
    return result['id']

def create_ingredient_with_conversions(name, type_name, shopping_unit_name, conversion_rules, size_rules=None, db=None):
    """Create an ingredient with conversion and size estimation rules."""
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        
        # Get IDs
        type_id = get_type_id(type_name, cursor)
        shopping_unit_id = get_unit_id(shopping_unit_name, cursor)
        
        # Check if ingredient already exists
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name,))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ {name} already exists (ID: {existing['id']}) - skipping")
            return existing['id']
        
        # Create ingredient
        cursor.execute("""
            INSERT INTO ingredients (name, type_id, shopping_unit_id)
            VALUES (?, ?, ?)
        """, (name, type_id, shopping_unit_id))
        
        ingredient_id = cursor.lastrowid
        print(f"  ✓ Created {name} (ID: {ingredient_id})")
        
        # Add conversion rules
        for rule in conversion_rules:
            from_unit_id = get_unit_id(rule['from'], cursor)
            cursor.execute("""
                INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, from_unit_id, shopping_unit_id, rule['factor']))
            print(f"    ✓ Conversion: {rule['from']} → {shopping_unit_name}: {rule['factor']}")
        
        # Add size estimation rules
        if size_rules:
            for size_rule in size_rules:
                ref_unit_id = get_unit_id(size_rule['unit'], cursor)
                cursor.execute("""
                    INSERT INTO size_estimation_rules (ingredient_id, size_qualifier, reference_unit_id, reference_value)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, size_rule['size'], ref_unit_id, size_rule['value']))
                print(f"    ✓ Size rule: {size_rule['size']} = {size_rule['value']} {size_rule['unit']}")
        
        db.commit()
        return ingredient_id
    
    finally:
        if close_after:
            db.close()

def update_ingredient_shopping_unit(name, new_shopping_unit, conversion_rules, db=None):
    """Update an ingredient's shopping unit and conversion rules."""
    if db is None:
        db = get_db()
        close_after = True
    else:
        close_after = False
    
    try:
        cursor = db.cursor()
        
        # Get ingredient
        cursor.execute("SELECT id, shopping_unit_id FROM ingredients WHERE name = ?", (name,))
        ingredient = cursor.fetchone()
        if not ingredient:
            print(f"  ⚠ {name} not found - cannot update")
            return
        
        ingredient_id = ingredient['id']
        old_shopping_unit_id = ingredient['shopping_unit_id']
        new_shopping_unit_id = get_unit_id(new_shopping_unit, cursor)
        
        if old_shopping_unit_id == new_shopping_unit_id:
            print(f"  ✓ {name} already uses '{new_shopping_unit}' as shopping unit")
        else:
            # Update shopping unit
            cursor.execute("""
                UPDATE ingredients SET shopping_unit_id = ? WHERE id = ?
            """, (new_shopping_unit_id, ingredient_id))
            print(f"  ✓ Updated {name} shopping unit to '{new_shopping_unit}'")
        
        # Update or add conversion rules
        for rule in conversion_rules:
            from_unit_id = get_unit_id(rule['from'], cursor)
            
            # Check if rule exists
            cursor.execute("""
                SELECT id FROM conversion_rules
                WHERE ingredient_id = ? AND from_unit_id = ? AND to_unit_id = ?
            """, (ingredient_id, from_unit_id, new_shopping_unit_id))
            
            existing = cursor.fetchone()
            if existing:
                # Update existing rule
                cursor.execute("""
                    UPDATE conversion_rules SET conversion_factor = ?
                    WHERE id = ?
                """, (rule['factor'], existing['id']))
                print(f"    ✓ Updated conversion: {rule['from']} → {new_shopping_unit}: {rule['factor']}")
            else:
                # Add new rule
                cursor.execute("""
                    INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                    VALUES (?, ?, ?, ?)
                """, (ingredient_id, from_unit_id, new_shopping_unit_id, rule['factor']))
                print(f"    ✓ Added conversion: {rule['from']} → {new_shopping_unit}: {rule['factor']}")
        
        db.commit()
    
    finally:
        if close_after:
            db.close()

def migrate_onion_references(db):
    """Migrate recipe references from 'Onion' to 'Yellow Onion'."""
    cursor = db.cursor()
    
    # Check if Onion exists
    cursor.execute("SELECT id FROM ingredients WHERE name = 'Onion'")
    onion = cursor.fetchone()
    if not onion:
        print("  ✓ 'Onion' not found - nothing to migrate")
        return
    
    onion_id = onion['id']
    
    # Get Yellow Onion ID
    cursor.execute("SELECT id FROM ingredients WHERE name = 'Yellow Onion'")
    yellow_onion = cursor.fetchone()
    if not yellow_onion:
        print("  ⚠ Yellow Onion not found - cannot migrate")
        return
    
    yellow_onion_id = yellow_onion['id']
    
    # Find recipes using Onion
    cursor.execute("""
        SELECT ri.id, ri.recipe_id, r.name as recipe_name, ri.quantity, ri.unit_id
        FROM recipe_items ri
        JOIN recipes r ON ri.recipe_id = r.id
        WHERE ri.ingredient_id = ?
    """, (onion_id,))
    
    usage = cursor.fetchall()
    if usage:
        print(f"  Found {len(usage)} recipe items using 'Onion':")
        for item in usage:
            print(f"    - Recipe '{item['recipe_name']}' (ID: {item['recipe_id']})")
        
        # Migrate to Yellow Onion
        cursor.execute("""
            UPDATE recipe_items SET ingredient_id = ? WHERE ingredient_id = ?
        """, (yellow_onion_id, onion_id))
        db.commit()
        print(f"  ✓ Migrated {len(usage)} recipe items from 'Onion' to 'Yellow Onion'")
    else:
        print("  ✓ No recipe items using 'Onion' - nothing to migrate")

def remove_ingredient(name, db):
    """Remove an ingredient (only if not used in recipes)."""
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name,))
    ingredient = cursor.fetchone()
    if not ingredient:
        print(f"  ✓ '{name}' not found - nothing to remove")
        return
    
    ingredient_id = ingredient['id']
    
    # Check usage
    cursor.execute("SELECT COUNT(*) as count FROM recipe_items WHERE ingredient_id = ?", (ingredient_id,))
    usage = cursor.fetchone()['count']
    
    if usage > 0:
        print(f"  ⚠ '{name}' is used in {usage} recipe items - cannot remove")
        return
    
    # Remove ingredient (cascades to conversion rules and size rules)
    cursor.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
    db.commit()
    print(f"  ✓ Removed '{name}'")

def main():
    """Main function to add all Vegetable Broth 2.0 ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Ingredients for Vegetable Broth 2.0")
        print("=" * 60)
        
        # Step 1: Migrate and remove old ingredients
        print("\n--- Step 1: Migrating and Removing Old Ingredients ---")
        migrate_onion_references(db)
        remove_ingredient('Onion', db)
        remove_ingredient('Tomato', db)
        
        # Step 2: Add Red Onion
        print("\n--- Step 2: Adding Red Onion ---")
        create_ingredient_with_conversions(
            name='Red Onion',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'cup', 'factor': 1.0},  # 1 cup chopped ≈ 1 whole
                {'from': 'tablespoon', 'factor': 0.0625},  # 1 tbsp = 0.0625 whole
                {'from': 'teaspoon', 'factor': 0.0208},  # 1 tsp = 0.0208 whole
                {'from': 'gram', 'factor': 0.00667},  # 150g = 1 whole
                {'from': 'kilogram', 'factor': 6.67},  # 1kg = 6.67 whole
                {'from': 'ounce', 'factor': 0.189},  # 1 oz ≈ 0.189 whole
                {'from': 'pound', 'factor': 3.02},  # 1 lb ≈ 3.02 whole
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 100},
                {'size': 'medium', 'unit': 'gram', 'value': 150},
                {'size': 'large', 'unit': 'gram', 'value': 200},
            ],
            db=db
        )
        
        # Step 3: Check/Add Carrot
        print("\n--- Step 3: Adding/Updating Carrot ---")
        cursor = db.cursor()
        cursor.execute("SELECT id, shopping_unit_id FROM ingredients WHERE name = 'Carrot'")
        carrot = cursor.fetchone()
        
        if carrot:
            # Update shopping unit to 'whole'
            update_ingredient_shopping_unit(
                name='Carrot',
                new_shopping_unit='whole',
                conversion_rules=[
                    {'from': 'cup', 'factor': 1.0},  # 1 cup chopped ≈ 1 whole
                    {'from': 'gram', 'factor': 0.005},  # 200g = 1 whole
                    {'from': 'kilogram', 'factor': 5.0},  # 1kg = 5 whole
                    {'from': 'whole', 'factor': 1.0},
                    {'from': 'piece', 'factor': 1.0},
                ],
                db=db
            )
        else:
            # Create new
            create_ingredient_with_conversions(
                name='Carrot',
                type_name='Vegetables',
                shopping_unit_name='whole',
                conversion_rules=[
                    {'from': 'cup', 'factor': 1.0},
                    {'from': 'gram', 'factor': 0.005},  # 200g = 1 whole
                    {'from': 'kilogram', 'factor': 5.0},
                    {'from': 'whole', 'factor': 1.0},
                    {'from': 'piece', 'factor': 1.0},
                ],
                size_rules=[
                    {'size': 'small', 'unit': 'gram', 'value': 100},
                    {'size': 'medium', 'unit': 'gram', 'value': 150},
                    {'size': 'large', 'unit': 'gram', 'value': 200},
                ],
                db=db
            )
        
        # Step 4: Add Bell Peppers (all colors with same conversions)
        print("\n--- Step 4: Adding Bell Peppers ---")
        bell_pepper_rules = [
            {'from': 'cup', 'factor': 0.5},  # 1 cup chopped ≈ 2 whole
            {'from': 'gram', 'factor': 0.005},  # 200g = 1 whole
            {'from': 'kilogram', 'factor': 5.0},  # 1kg = 5 whole
            {'from': 'whole', 'factor': 1.0},
            {'from': 'piece', 'factor': 1.0},
        ]
        bell_pepper_sizes = [
            {'size': 'small', 'unit': 'gram', 'value': 100},
            {'size': 'medium', 'unit': 'gram', 'value': 150},
            {'size': 'large', 'unit': 'gram', 'value': 250},
        ]
        
        for color in ['Red', 'Green', 'Yellow']:
            create_ingredient_with_conversions(
                name=f'{color} Bell Pepper',
                type_name='Vegetables',
                shopping_unit_name='whole',
                conversion_rules=bell_pepper_rules,
                size_rules=bell_pepper_sizes,
                db=db
            )
        
        # Step 5: Add Garlic
        print("\n--- Step 5: Adding Garlic ---")
        create_ingredient_with_conversions(
            name='Garlic',
            type_name='Spices',
            shopping_unit_name='clove',
            conversion_rules=[
                {'from': 'clove', 'factor': 1.0},
                {'from': 'whole', 'factor': 10.0},  # 1 head = 10 cloves
                {'from': 'gram', 'factor': 0.1},  # 10g = 1 clove (average)
                {'from': 'teaspoon', 'factor': 1.0},  # 1 tsp minced ≈ 1 large clove
                {'from': 'tablespoon', 'factor': 0.333},  # 1 tbsp ≈ 3 cloves
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 3},
                {'size': 'medium', 'unit': 'gram', 'value': 5},
                {'size': 'large', 'unit': 'gram', 'value': 7},
            ],
            db=db
        )
        
        # Step 6: Add Roma Tomato
        print("\n--- Step 6: Adding Roma Tomato ---")
        create_ingredient_with_conversions(
            name='Roma Tomato',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'cup', 'factor': 0.8},  # 1 cup chopped ≈ 0.8 whole (1.25 whole = 1 cup)
                {'from': 'gram', 'factor': 0.0133},  # 75g = 1 whole
                {'from': 'kilogram', 'factor': 13.3},  # 1kg = 13.3 whole
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 60},
                {'size': 'medium', 'unit': 'gram', 'value': 75},
                {'size': 'large', 'unit': 'gram', 'value': 90},
            ],
            db=db
        )
        
        # Step 7: Add Dried Shiitake Mushroom
        print("\n--- Step 7: Adding Dried Shiitake Mushroom ---")
        create_ingredient_with_conversions(
            name='Dried Shiitake Mushroom',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'piece', 'factor': 0.067},  # 1 piece = 0.067 packages (15 pieces = 1 package)
                {'from': 'gram', 'factor': 0.0175},  # 57g = 1 package
                {'from': 'kilogram', 'factor': 17.5},  # 1kg = 17.5 packages
                {'from': 'ounce', 'factor': 0.5},  # 2 oz = 1 package
                {'from': 'pound', 'factor': 8.0},  # 0.125 lb = 1 package (2 oz)
            ],
            db=db
        )
        
        # Step 8: Add Bay Leaf
        print("\n--- Step 8: Adding Bay Leaf ---")
        create_ingredient_with_conversions(
            name='Bay Leaf',
            type_name='Herbs',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'piece', 'factor': 0.033},  # 1 leaf = 0.033 packages (30 leaves = 1 package)
                {'from': 'gram', 'factor': 0.071},  # 14g = 1 package
                {'from': 'kilogram', 'factor': 71.43},  # 1kg = 71.43 packages
                {'from': 'ounce', 'factor': 2.0},  # 0.5 oz = 1 package
            ],
            db=db
        )
        
        # Step 9: Add Kombu
        print("\n--- Step 9: Adding Kombu ---")
        create_ingredient_with_conversions(
            name='Kombu',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'piece', 'factor': 0.2},  # 1 piece = 0.2 packages (5 pieces = 1 package)
                {'from': 'gram', 'factor': 0.02},  # 50g = 1 package
                {'from': 'kilogram', 'factor': 20.0},  # 1kg = 20 packages
                {'from': 'ounce', 'factor': 0.56},  # 50g ≈ 1.76 oz = 1 package
            ],
            db=db
        )
        
        # Step 10: Check/Update Parsley
        print("\n--- Step 10: Adding/Updating Parsley ---")
        cursor.execute("SELECT id FROM ingredients WHERE name = 'Parsley'")
        parsley = cursor.fetchone()
        
        if parsley:
            # Update conversions to 60g per bunch
            update_ingredient_shopping_unit(
                name='Parsley',
                new_shopping_unit='bunch',
                conversion_rules=[
                    {'from': 'cup', 'factor': 1.0},  # 1 cup = 1 bunch (60g each)
                    {'from': 'gram', 'factor': 0.0167},  # 60g = 1 bunch
                    {'from': 'kilogram', 'factor': 16.67},  # 1kg = 16.67 bunches
                    {'from': 'tablespoon', 'factor': 0.125},  # 1 tbsp = 0.125 bunches (8 tbsp = 1 cup)
                    {'from': 'ounce', 'factor': 0.47},  # 60g ≈ 2.12 oz = 1 bunch
                ],
                db=db
            )
        else:
            # Create new
            create_ingredient_with_conversions(
                name='Parsley',
                type_name='Herbs',
                shopping_unit_name='bunch',
                conversion_rules=[
                    {'from': 'cup', 'factor': 1.0},  # 1 cup = 1 bunch (60g)
                    {'from': 'gram', 'factor': 0.0167},  # 60g = 1 bunch
                    {'from': 'kilogram', 'factor': 16.67},
                    {'from': 'tablespoon', 'factor': 0.125},
                    {'from': 'ounce', 'factor': 0.47},
                ],
                db=db
            )
        
        # Step 11: Add Black Pepper
        print("\n--- Step 11: Adding Black Pepper ---")
        create_ingredient_with_conversions(
            name='Black Pepper',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 0.003},  # ~330 tsp per 3oz package
                {'from': 'tablespoon', 'factor': 0.01},  # ~110 tbsp per package
                {'from': 'gram', 'factor': 0.01},  # ~100g package
                {'from': 'ounce', 'factor': 0.33},  # 3 oz = 1 package
                {'from': 'pound', 'factor': 5.33},  # 0.1875 lb (3 oz) = 1 package
            ],
            db=db
        )
        
        # Step 12: Add White Miso Paste
        print("\n--- Step 12: Adding White Miso Paste ---")
        create_ingredient_with_conversions(
            name='White Miso Paste',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 0.006},  # ~170 tbsp per 14 oz package
                {'from': 'teaspoon', 'factor': 0.002},  # ~510 tsp per package
                {'from': 'gram', 'factor': 0.0025},  # 400g = 1 package
                {'from': 'kilogram', 'factor': 2.5},  # 1kg = 2.5 packages
                {'from': 'ounce', 'factor': 0.071},  # 14 oz = 1 package
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All ingredients added successfully!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    main()

