#!/usr/bin/env python3
"""
Script to add ingredients for batch 9 recipes:
1. Cornmeal
2. Sorghum
3. Kasha (Roasted Buckwheat Groats)
4. Ground Sage
5. Japanese Eggplant
6. Wheat Germ
7. Radicchio
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
        print("Adding Ingredients for Batch 9 Recipes")
        print("=" * 60)
        
        # Step 1: Cornmeal
        print("\n--- Step 1: Adding Cornmeal ---")
        create_ingredient_with_conversions(
            name='Cornmeal',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (24 oz / 680g package)
                {'from': 'cup', 'factor': 155/680},  # 0.228 packages/cup (155g per cup)
                {'from': 'gram', 'factor': 1/680},  # 0.00147 packages/g
                {'from': 'ounce', 'factor': 1/24},  # 0.0417 packages/oz
            ],
            db=db
        )
        
        # Step 2: Sorghum
        print("\n--- Step 2: Adding Sorghum ---")
        create_ingredient_with_conversions(
            name='Sorghum',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (16 oz / 454g package)
                {'from': 'cup', 'factor': 190/454},  # 0.419 packages/cup (190g per cup dry)
                {'from': 'gram', 'factor': 1/454},  # 0.00220 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 3: Kasha (Roasted Buckwheat Groats)
        print("\n--- Step 3: Adding Kasha (Roasted Buckwheat Groats) ---")
        create_ingredient_with_conversions(
            name='Kasha (Roasted Buckwheat Groats)',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (13 oz / 369g package)
                {'from': 'cup', 'factor': 180/369},  # 0.488 packages/cup (180g per cup dry)
                {'from': 'gram', 'factor': 1/369},  # 0.00271 packages/g
                {'from': 'ounce', 'factor': 1/13},  # 0.0769 packages/oz
            ],
            db=db
        )
        
        # Step 4: Ground Sage
        print("\n--- Step 4: Adding Ground Sage ---")
        create_ingredient_with_conversions(
            name='Ground Sage',
            type_name='Spices',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (1 oz / 28g package)
                {'from': 'teaspoon', 'factor': 1/50},  # 0.02 packages/tsp (estimate)
                {'from': 'gram', 'factor': 1/28},  # 0.0357 packages/g
            ],
            db=db
        )
        
        # Step 5: Japanese Eggplant
        print("\n--- Step 5: Adding Japanese Eggplant ---")
        create_ingredient_with_conversions(
            name='Japanese Eggplant',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},  # 1.0
            ],
            db=db
        )
        
        # Step 6: Wheat Germ
        print("\n--- Step 6: Adding Wheat Germ ---")
        create_ingredient_with_conversions(
            name='Wheat Germ',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'package', 'factor': 1.0},  # 1.0 (8 oz / 227g package)
                {'from': 'cup', 'factor': 120/227},  # 0.529 packages/cup (~120g per cup)
                {'from': 'gram', 'factor': 1/227},  # 0.00441 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 0.125 packages/oz
            ],
            db=db
        )
        
        # Step 7: Radicchio
        print("\n--- Step 7: Adding Radicchio ---")
        create_ingredient_with_conversions(
            name='Radicchio',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},  # 1.0
                {'from': 'whole', 'factor': 1.0},  # 1.0 (same as head)
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

