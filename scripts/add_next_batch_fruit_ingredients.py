#!/usr/bin/env python3
"""
Script to add fruit/vegetable ingredients for next batch recipes:
1. Pomegranate Seeds
2. Pear
3. Shallot
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
    """Main function to add all fruit/vegetable ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Fruit/Vegetable Ingredients for Next Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Pomegranate Seeds
        print("\n--- Step 1: Adding Pomegranate Seeds ---")
        create_ingredient_with_conversions(
            name='Pomegranate Seeds',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 140/150},  # 140/150 = 0.933 packages/cup
                {'from': 'gram', 'factor': 1/150},  # 1/150 packages/g
                {'from': 'ounce', 'factor': 1/5.3},  # 1/5.3 = 0.189 packages/oz
            ],
            db=db
        )
        
        # Step 2: Add Pear
        print("\n--- Step 2: Adding Pear ---")
        create_ingredient_with_conversions(
            name='Pear',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'cup', 'factor': 175/175},  # 175/175 = 1.0 whole/cup (chopped)
                {'from': 'gram', 'factor': 1/175},  # 1/175 = 0.00571 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 150},
                {'size': 'medium', 'unit': 'gram', 'value': 175},
                {'size': 'large', 'unit': 'gram', 'value': 200},
            ],
            db=db
        )
        
        # Step 3: Add Shallot
        print("\n--- Step 3: Adding Shallot ---")
        create_ingredient_with_conversions(
            name='Shallot',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'gram', 'factor': 1/25},  # 1/25 = 0.04 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 15},
                {'size': 'medium', 'unit': 'gram', 'value': 25},
                {'size': 'large', 'unit': 'gram', 'value': 40},
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All fruit/vegetable ingredients added successfully!")
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

