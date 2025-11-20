#!/usr/bin/env python3
"""
Script to add vegetable ingredients for new batch recipes:
1. Fresh Baby Spinach
2. Frozen Green Peas
3. Broccoli (Broccoli Florets)
4. Fennel Bulb
5. Small Potatoes
6. Jalapeño
7. Plum Tomatoes
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
    """Main function to add all vegetable ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Vegetable Ingredients for New Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Fresh Baby Spinach
        print("\n--- Step 1: Adding Fresh Baby Spinach ---")
        create_ingredient_with_conversions(
            name='Fresh Baby Spinach',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'gram', 'factor': 1/285},  # 1/285 = 0.00351 packages/g
                {'from': 'ounce', 'factor': 1/10},  # 1/10 = 0.1 packages/oz
                {'from': 'cup', 'factor': 30/285},  # 30/285 = 0.105 packages/cup (fresh, raw)
            ],
            db=db
        )
        
        # Step 2: Add Frozen Green Peas
        print("\n--- Step 2: Adding Frozen Green Peas ---")
        create_ingredient_with_conversions(
            name='Frozen Green Peas',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 130/454},  # 130/454 = 0.286 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Broccoli Florets
        print("\n--- Step 3: Adding Broccoli Florets ---")
        create_ingredient_with_conversions(
            name='Broccoli Florets',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 85/454},  # 85/454 = 0.187 packages/cup
                {'from': 'gram', 'factor': 1/454},  # 1/454 packages/g
                {'from': 'ounce', 'factor': 1/16},  # 1/16 = 0.0625 packages/oz
            ],
            db=db
        )
        
        # Step 4: Add Fennel Bulb
        print("\n--- Step 4: Adding Fennel Bulb ---")
        create_ingredient_with_conversions(
            name='Fennel Bulb',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'cup', 'factor': 87/250},  # 87/250 = 0.348 whole/cup (chopped)
                {'from': 'gram', 'factor': 1/250},  # 1/250 = 0.004 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 200},
                {'size': 'medium', 'unit': 'gram', 'value': 250},
                {'size': 'large', 'unit': 'gram', 'value': 300},
            ],
            db=db
        )
        
        # Step 5: Add Small Potatoes
        print("\n--- Step 5: Adding Small Potatoes ---")
        create_ingredient_with_conversions(
            name='Small Potatoes',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'whole', 'factor': 1/13.61},  # 1/13.61 = 0.0735 packages/whole (for 3 lb bag)
                {'from': 'gram', 'factor': 1/1361},  # 1/1361 packages/g
                {'from': 'pound', 'factor': 1/3},  # 1/3 = 0.333 packages/lb
            ],
            db=db
        )
        
        # Step 6: Add Jalapeño
        print("\n--- Step 6: Adding Jalapeño ---")
        create_ingredient_with_conversions(
            name='Jalapeño',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'gram', 'factor': 1/15},  # 1/15 = 0.0667 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 10},
                {'size': 'medium', 'unit': 'gram', 'value': 15},
                {'size': 'large', 'unit': 'gram', 'value': 20},
            ],
            db=db
        )
        
        # Step 7: Add Plum Tomatoes
        print("\n--- Step 7: Adding Plum Tomatoes ---")
        create_ingredient_with_conversions(
            name='Plum Tomatoes',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'cup', 'factor': 185/80},  # 185/80 = 2.31 whole/cup (chopped)
                {'from': 'gram', 'factor': 1/80},  # 1/80 = 0.0125 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 60},
                {'size': 'medium', 'unit': 'gram', 'value': 80},
                {'size': 'large', 'unit': 'gram', 'value': 100},
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All vegetable ingredients added successfully!")
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

