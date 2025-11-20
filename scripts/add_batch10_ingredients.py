#!/usr/bin/env python3
"""
Script to add ingredients for batch 10 recipes:
1. Parsnip
2. Yukon Gold Potatoes
3. Asparagus
4. White Sesame Seeds
5. Black Sesame Seeds
6. Tomato Puree
7. Pecan Halves
8. Spaghetti Squash
9. Mixed Berries
10. Raspberries
11. Almond Flour
"""

import os
import sys
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
            print(f"    ✓ Conversion: {rule['from']} → {shopping_unit_name}: {rule['factor']:.6f}")
        
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

def main():
    """Main function to add all ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Ingredients for Batch 10 Recipes")
        print("=" * 60)
        
        # Step 1: Parsnip
        print("\n--- Step 1: Adding Parsnip ---")
        create_ingredient_with_conversions(
            name='Parsnip',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0
            ],
            db=db
        )
        
        # Step 2: Yukon Gold Potatoes
        print("\n--- Step 2: Adding Yukon Gold Potatoes ---")
        create_ingredient_with_conversions(
            name='Yukon Gold Potatoes',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0
                {'from': 'pound', 'factor': 1.0},  # 1.0
                {'from': 'gram', 'factor': 1/454},  # 0.00220 pounds/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 pounds/oz
            ],
            db=db
        )
        
        # Step 3: Asparagus
        print("\n--- Step 3: Adding Asparagus ---")
        create_ingredient_with_conversions(
            name='Asparagus',
            type_name='Vegetables',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},  # 1.0
                {'from': 'pound', 'factor': 1.0},  # 1.0
                {'from': 'gram', 'factor': 1/454},  # 0.00220 pounds/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 pounds/oz
            ],
            db=db
        )
        
        # Step 4: White Sesame Seeds
        print("\n--- Step 4: Adding White Sesame Seeds ---")
        create_ingredient_with_conversions(
            name='White Sesame Seeds',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (2 oz / 57g package)
                {'from': 'tablespoon', 'factor': 9/57},  # 0.158 packages/tbsp (1 tbsp ≈ 9g)
                {'from': 'gram', 'factor': 1/57},  # 0.0175 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 5: Black Sesame Seeds
        print("\n--- Step 5: Adding Black Sesame Seeds ---")
        create_ingredient_with_conversions(
            name='Black Sesame Seeds',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (2 oz / 57g package)
                {'from': 'tablespoon', 'factor': 9/57},  # 0.158 packages/tbsp (1 tbsp ≈ 9g)
                {'from': 'gram', 'factor': 1/57},  # 0.0175 packages/g
                {'from': 'ounce', 'factor': 1/2},  # 0.5 packages/oz
            ],
            db=db
        )
        
        # Step 6: Tomato Puree
        print("\n--- Step 6: Adding Tomato Puree ---")
        create_ingredient_with_conversions(
            name='Tomato Puree',
            type_name='Pantry Items',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'can', 'factor': 1.0},  # 1.0 (15 oz / 425g can)
                {'from': 'cup', 'factor': 240/425},  # 0.565 cans/cup (0.25 cup = 60g, so ~240g per cup)
                {'from': 'gram', 'factor': 1/425},  # 0.00235 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 7: Pecan Halves
        print("\n--- Step 7: Adding Pecan Halves ---")
        create_ingredient_with_conversions(
            name='Pecan Halves',
            type_name='Nuts & Seeds',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (8 oz / 227g package)
                {'from': 'cup', 'factor': 100/227},  # 0.441 packages/cup (0.5 cup = 50g, so ~100g per cup)
                {'from': 'gram', 'factor': 1/227},  # 0.00441 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 0.125 packages/oz
            ],
            db=db
        )
        
        # Step 8: Spaghetti Squash
        print("\n--- Step 8: Adding Spaghetti Squash ---")
        create_ingredient_with_conversions(
            name='Spaghetti Squash',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0
                {'from': 'pound', 'factor': 1/4},  # 0.25 wholes/pound (estimate 4 pounds per squash)
                {'from': 'gram', 'factor': 1/(4*454)},  # 0.000551 wholes/g
                {'from': 'ounce', 'factor': 1/(4*16)},  # 0.0156 wholes/oz
            ],
            db=db
        )
        
        # Step 9: Mixed Berries
        print("\n--- Step 9: Adding Mixed Berries ---")
        create_ingredient_with_conversions(
            name='Mixed Berries',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (12 oz / 340g package for frozen)
                {'from': 'cup', 'factor': 160/340},  # 0.471 packages/cup (2.25 cups = 400g, so ~177.8g per cup, use 160g for simplicity)
                {'from': 'gram', 'factor': 1/340},  # 0.00294 packages/g
                {'from': 'ounce', 'factor': 1/12},  # 0.0833 packages/oz
            ],
            db=db
        )
        
        # Step 10: Raspberries
        print("\n--- Step 10: Adding Raspberries ---")
        create_ingredient_with_conversions(
            name='Raspberries',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (estimate 6 oz / 170g package for fresh)
                {'from': 'cup', 'factor': 170/170},  # 1.0 packages/cup (estimate 1 cup = 170g)
                {'from': 'gram', 'factor': 1/170},  # 0.00588 packages/g
                {'from': 'ounce', 'factor': 1/6},  # 0.167 packages/oz
            ],
            db=db
        )
        
        # Step 11: Almond Flour
        print("\n--- Step 11: Adding Almond Flour ---")
        create_ingredient_with_conversions(
            name='Almond Flour',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz / 454g package)
                {'from': 'cup', 'factor': 110/454},  # 0.242 packages/cup (0.5 cup = 55g, so ~110g per cup)
                {'from': 'gram', 'factor': 1/454},  # 0.00220 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
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

