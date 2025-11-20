#!/usr/bin/env python3
"""
Script to add vegetable ingredients for next batch recipes:
1. Oyster Mushrooms
2. Yellow Potatoes
3. Kale
4. Watercress
5. Mixed Baby Greens
6. Ripe Tomatoes
7. Escarole
8. Purple Cabbage
9. Arugula
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
        print("Adding Vegetable Ingredients for Next Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Oyster Mushrooms
        print("\n--- Step 1: Adding Oyster Mushrooms ---")
        create_ingredient_with_conversions(
            name='Oyster Mushrooms',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'gram', 'factor': 1/225},  # 1/225 = 0.00444 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
                {'from': 'cup', 'factor': 85/225},  # 85/225 = 0.378 packages/cup (chopped)
            ],
            db=db
        )
        
        # Step 2: Add Yellow Potatoes
        print("\n--- Step 2: Adding Yellow Potatoes ---")
        create_ingredient_with_conversions(
            name='Yellow Potatoes',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'whole', 'factor': 1/9.07},  # 1/9.07 = 0.1103 packages/whole (for 3 lb bag)
                {'from': 'cup', 'factor': 150/1361},  # 150/1361 = 0.1102 packages/cup (chopped)
                {'from': 'gram', 'factor': 1/1361},  # 1/1361 packages/g
                {'from': 'pound', 'factor': 1/3},  # 1/3 = 0.333 packages/lb
            ],
            db=db
        )
        
        # Step 3: Add Kale
        print("\n--- Step 3: Adding Kale ---")
        create_ingredient_with_conversions(
            name='Kale',
            type_name='Vegetables',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},
                {'from': 'cup', 'factor': 67/170},  # 67/170 = 0.394 bunches/cup (chopped, stems removed)
                {'from': 'gram', 'factor': 1/170},  # 1/170 = 0.00588 bunches/g
            ],
            db=db
        )
        
        # Step 4: Add Watercress
        print("\n--- Step 4: Adding Watercress ---")
        create_ingredient_with_conversions(
            name='Watercress',
            type_name='Vegetables',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},
                {'from': 'cup', 'factor': 34/85},  # 34/85 = 0.4 bunches/cup (chopped, tough stems removed)
                {'from': 'gram', 'factor': 1/85},  # 1/85 = 0.0118 bunches/g
            ],
            db=db
        )
        
        # Step 5: Add Mixed Baby Greens
        print("\n--- Step 5: Adding Mixed Baby Greens ---")
        create_ingredient_with_conversions(
            name='Mixed Baby Greens',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 30/142},  # 30/142 = 0.211 packages/cup
                {'from': 'gram', 'factor': 1/142},  # 1/142 packages/g
                {'from': 'ounce', 'factor': 1/5},  # 1/5 = 0.2 packages/oz
            ],
            db=db
        )
        
        # Step 6: Add Ripe Tomatoes
        print("\n--- Step 6: Adding Ripe Tomatoes ---")
        create_ingredient_with_conversions(
            name='Ripe Tomatoes',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'cup', 'factor': 180/150},  # 180/150 = 1.2 whole/cup (chopped)
                {'from': 'gram', 'factor': 1/150},  # 1/150 = 0.00667 whole/g (medium)
                {'from': 'pound', 'factor': 453.6/150},  # 453.6/150 = 3.024 whole/lb
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 100},
                {'size': 'medium', 'unit': 'gram', 'value': 150},
                {'size': 'large', 'unit': 'gram', 'value': 200},
            ],
            db=db
        )
        
        # Step 7: Add Escarole
        print("\n--- Step 7: Adding Escarole ---")
        create_ingredient_with_conversions(
            name='Escarole',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},
                {'from': 'cup', 'factor': 85/680},  # 85/680 = 0.125 heads/cup (chopped)
                {'from': 'gram', 'factor': 1/680},  # 1/680 = 0.00147 heads/g
            ],
            db=db
        )
        
        # Step 8: Add Purple Cabbage
        print("\n--- Step 8: Adding Purple Cabbage ---")
        create_ingredient_with_conversions(
            name='Purple Cabbage',
            type_name='Vegetables',
            shopping_unit_name='head',
            conversion_rules=[
                {'from': 'head', 'factor': 1.0},
                {'from': 'cup', 'factor': 95/680},  # 95/680 = 0.140 heads/cup (shredded)
                {'from': 'gram', 'factor': 1/680},  # 1/680 = 0.00147 heads/g
            ],
            db=db
        )
        
        # Step 9: Add Arugula
        print("\n--- Step 9: Adding Arugula ---")
        create_ingredient_with_conversions(
            name='Arugula',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 20/142},  # 20/142 = 0.141 packages/cup
                {'from': 'gram', 'factor': 1/142},  # 1/142 packages/g
                {'from': 'ounce', 'factor': 1/5},  # 1/5 = 0.2 packages/oz
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

