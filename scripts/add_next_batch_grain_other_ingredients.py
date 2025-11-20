#!/usr/bin/env python3
"""
Script to add grain/other ingredients for next batch recipes:
1. Farro
2. Date Sugar
3. Thai Bird's Eye Chile
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
    """Main function to add all grain/other ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Grain/Other Ingredients for Next Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Farro
        print("\n--- Step 1: Adding Farro ---")
        create_ingredient_with_conversions(
            name='Farro',
            type_name='Grains',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 165/454},  # 165/454 = 0.363 packages/cup (raw farro)
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 2: Add Date Sugar
        print("\n--- Step 2: Adding Date Sugar ---")
        create_ingredient_with_conversions(
            name='Date Sugar',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/68},  # 1/68 = 0.0147 packages/tsp (5g/tsp)
                {'from': 'tablespoon', 'factor': 1/22.67},  # 1/22.67 = 0.0441 packages/tbsp (15g/tbsp)
                {'from': 'cup', 'factor': 192/340},  # 192/340 = 0.565 packages/cup
                {'from': 'gram', 'factor': 1/340},  # 1/340 packages/g
                {'from': 'ounce', 'factor': 1/12},  # 1/12 = 0.0833 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Thai Bird's Eye Chile
        print("\n--- Step 3: Adding Thai Bird's Eye Chile ---")
        create_ingredient_with_conversions(
            name='Thai Bird\'s Eye Chile',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'gram', 'factor': 1/8},  # 1/8 = 0.125 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 5},
                {'size': 'medium', 'unit': 'gram', 'value': 8},
                {'size': 'large', 'unit': 'gram', 'value': 10},
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All grain/other ingredients added successfully!")
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

