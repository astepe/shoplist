#!/usr/bin/env python3
"""
Script to add ingredients for batch 5 recipes:
1. Whole-Grain Burger Buns
2. Whole-Grain Lasagna Noodles
3. Whole-Grain Spaghetti
4. Whole-Grain Rotini
5. Red Lentils
6. Salt-Free Marinara Sauce
7. Mushrooms (regular white mushrooms)
8. Fresh Mango
9. Quinoa
10. Portobello Mushrooms
11. Russet Potatoes
12. Romaine Lettuce
13. Boston Lettuce
14. Cauliflower Florets
15. Lettuce (generic lettuce)
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
        print("Adding Ingredients for Batch 5 Recipes")
        print("=" * 60)
        
        # Step 1: Whole-Grain Burger Buns
        print("\n--- Step 1: Adding Whole-Grain Burger Buns ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Burger Buns',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'whole', 'factor': 1/4},  # 0.25 packages/bun
                {'from': 'package', 'factor': 1.0},  # 1.0 (4 buns)
            ],
            db=db
        )
        
        # Step 2: Whole-Grain Lasagna Noodles
        print("\n--- Step 2: Adding Whole-Grain Lasagna Noodles ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Lasagna Noodles',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'whole', 'factor': 1/18},  # 0.0556 packages/noodle
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz, 18 noodles)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 3: Whole-Grain Spaghetti
        print("\n--- Step 3: Adding Whole-Grain Spaghetti ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Spaghetti',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
                {'from': 'pound', 'factor': 1/1},  # 1.0 packages/lb
            ],
            db=db
        )
        
        # Step 4: Whole-Grain Rotini
        print("\n--- Step 4: Adding Whole-Grain Rotini ---")
        create_ingredient_with_conversions(
            name='Whole-Grain Rotini',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
                {'from': 'pound', 'factor': 1/1},  # 1.0 packages/lb
            ],
            db=db
        )
        
        # Step 5: Red Lentils
        print("\n--- Step 5: Adding Red Lentils ---")
        create_ingredient_with_conversions(
            name='Red Lentils',
            type_name='Plant Proteins',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 lb)
                {'from': 'cup', 'factor': 190/454},  # 0.418 packages/cup (~190g per cup dry)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
            ],
            db=db
        )
        
        # Step 6: Salt-Free Marinara Sauce
        print("\n--- Step 6: Adding Salt-Free Marinara Sauce ---")
        create_ingredient_with_conversions(
            name='Salt-Free Marinara Sauce',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (24 oz)
                {'from': 'cup', 'factor': 1/3},  # 0.333 packages/cup (240ml)
                {'from': 'gram', 'factor': 1/680},  # 0.00147 packages/g
                {'from': 'fluid_ounce', 'factor': 1/24},  # 0.0417 packages/fl oz
            ],
            db=db
        )
        
        # Step 7: Mushrooms (regular white mushrooms)
        print("\n--- Step 7: Adding Mushrooms ---")
        create_ingredient_with_conversions(
            name='Mushrooms',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (8 oz package)
                {'from': 'gram', 'factor': 1/226.8},  # 1/226.8 = 0.00441 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
                {'from': 'cup', 'factor': 1/2},  # ~2 cups per 8 oz package
            ],
            db=db
        )
        
        # Step 8: Fresh Mango
        print("\n--- Step 8: Adding Fresh Mango ---")
        create_ingredient_with_conversions(
            name='Fresh Mango',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0 (large mango ~400g)
                {'from': 'gram', 'factor': 1/400},  # 0.0025 whole/g
                {'from': 'pound', 'factor': 453.6/400},  # 1.134 whole/lb
                {'from': 'cup', 'factor': 1/2},  # ~2 cups chopped per large mango
            ],
            db=db
        )
        
        # Step 9: Quinoa
        print("\n--- Step 9: Adding Quinoa ---")
        create_ingredient_with_conversions(
            name='Quinoa',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 lb package)
                {'from': 'cup', 'factor': 180/454},  # 180/454 = 0.396 packages/cup (~180g cooked per cup)
                {'from': 'gram', 'factor': 1/454},  # 0.0022 packages/g
            ],
            db=db
        )
        
        # Step 10: Portobello Mushrooms
        print("\n--- Step 10: Adding Portobello Mushrooms ---")
        create_ingredient_with_conversions(
            name='Portobello Mushrooms',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0 (large cap ~100g)
                {'from': 'gram', 'factor': 1/100},  # 0.01 whole/g
                {'from': 'ounce', 'factor': 28.35/100},  # 0.2835 whole/oz
                {'from': 'pound', 'factor': 453.6/100},  # 4.536 whole/lb
            ],
            db=db
        )
        
        # Step 11: Russet Potatoes
        print("\n--- Step 11: Adding Russet Potatoes ---")
        create_ingredient_with_conversions(
            name='Russet Potatoes',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0 (large potato ~350g)
                {'from': 'gram', 'factor': 1/350},  # 0.00286 whole/g
                {'from': 'pound', 'factor': 453.6/350},  # 1.296 whole/lb
                {'from': 'cup', 'factor': 0.25},  # 0.25 whole/cup (mashed)
            ],
            db=db
        )
        
        # Step 12: Romaine Lettuce
        print("\n--- Step 12: Adding Romaine Lettuce ---")
        create_ingredient_with_conversions(
            name='Romaine Lettuce',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0
                {'from': 'cup', 'factor': 1/10},  # 0.1 heads/cup (shredded)
                {'from': 'gram', 'factor': 1/450},  # 0.00222 heads/g
            ],
            db=db
        )
        
        # Step 13: Boston Lettuce
        print("\n--- Step 13: Adding Boston Lettuce ---")
        create_ingredient_with_conversions(
            name='Boston Lettuce',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0
                {'from': 'whole', 'factor': 1/8},  # 0.125 heads/leaf (~25g per large leaf)
                {'from': 'cup', 'factor': 1/8},  # 0.125 heads/cup (chopped)
                {'from': 'gram', 'factor': 1/200},  # 0.005 heads/g
            ],
            db=db
        )
        
        # Step 14: Cauliflower Florets
        print("\n--- Step 14: Adding Cauliflower Florets ---")
        create_ingredient_with_conversions(
            name='Cauliflower Florets',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0 (~800g per head)
                {'from': 'cup', 'factor': 1/6},  # ~6 cups florets per head
                {'from': 'gram', 'factor': 1/800},  # 0.00125 heads/g
                {'from': 'pound', 'factor': 453.6/800},  # 0.567 heads/lb
            ],
            db=db
        )
        
        # Step 15: Lettuce (generic lettuce)
        print("\n--- Step 15: Adding Lettuce ---")
        create_ingredient_with_conversions(
            name='Lettuce',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0
                {'from': 'whole', 'factor': 1/10},  # 0.1 heads/leaf (~40g per large leaf)
                {'from': 'cup', 'factor': 1/8},  # 0.125 heads/cup (chopped)
                {'from': 'gram', 'factor': 1/400},  # 0.0025 heads/g
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

