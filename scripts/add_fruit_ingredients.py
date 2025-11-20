#!/usr/bin/env python3
"""
Script to add fruit ingredients:
1. Banana
2. Blueberries
3. Fresh Blackberries
4. Peaches
5. Strawberries
6. Dried Goji Berries
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
    """Main function to add all fruit ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Fruit Ingredients")
        print("=" * 60)
        
        # Step 1: Add Banana
        print("\n--- Step 1: Adding Banana ---")
        create_ingredient_with_conversions(
            name='Banana',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
                {'from': 'cup', 'factor': 150/120},  # 150/120 = 1.25 whole/cup (mashed)
                {'from': 'gram', 'factor': 1/120},  # 1/120 = 0.00833 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 100},
                {'size': 'medium', 'unit': 'gram', 'value': 120},
                {'size': 'large', 'unit': 'gram', 'value': 150},
            ],
            db=db
        )
        
        # Step 2: Add Blueberries
        print("\n--- Step 2: Adding Blueberries ---")
        create_ingredient_with_conversions(
            name='Blueberries',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 130/170},  # 130/170 = 0.765 packages/cup
                {'from': 'gram', 'factor': 1/170},  # 1/170 packages/g
                {'from': 'ounce', 'factor': 1/6},  # 1/6 = 0.167 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Fresh Blackberries
        print("\n--- Step 3: Adding Fresh Blackberries ---")
        create_ingredient_with_conversions(
            name='Fresh Blackberries',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 130/170},  # 130/170 = 0.765 packages/cup
                {'from': 'gram', 'factor': 1/170},  # 1/170 packages/g
                {'from': 'ounce', 'factor': 1/6},  # 1/6 = 0.167 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Peaches
        print("\n--- Step 4: Adding Peaches ---")
        create_ingredient_with_conversions(
            name='Peaches',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
                {'from': 'cup', 'factor': 175/150},  # 175/150 = 1.17 whole/cup (chopped, medium)
                {'from': 'gram', 'factor': 1/150},  # 1/150 = 0.00667 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 120},
                {'size': 'medium', 'unit': 'gram', 'value': 150},
                {'size': 'large', 'unit': 'gram', 'value': 180},
            ],
            db=db
        )
        
        # Step 5: Add Strawberries
        print("\n--- Step 5: Adding Strawberries ---")
        create_ingredient_with_conversions(
            name='Strawberries',
            type_name='Fruits',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 125/454},  # 125/454 = 0.275 packages/cup (hulled and sliced)
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 6: Add Dried Goji Berries
        print("\n--- Step 6: Adding Dried Goji Berries ---")
        create_ingredient_with_conversions(
            name='Dried Goji Berries',
            type_name='Pantry Items',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/18.92},  # 1/18.92 = 0.0529 packages/tbsp
                {'from': 'gram', 'factor': 1/227},  # 1/227 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All fruit ingredients added successfully!")
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

