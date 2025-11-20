#!/usr/bin/env python3
"""
Script to add vegetable ingredients:
1. Frozen Artichoke Hearts
2. White Mushrooms
3. Scallions
4. Fresh Thyme
5. Zucchini
6. Cherry Tomatoes
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
    """Main function to add all vegetable ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Vegetable Ingredients")
        print("=" * 60)
        
        # Step 1: Add Frozen Artichoke Hearts
        print("\n--- Step 1: Adding Frozen Artichoke Hearts ---")
        create_ingredient_with_conversions(
            name='Frozen Artichoke Hearts',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'gram', 'factor': 1/285},  # 1/285 packages/g
                {'from': 'ounce', 'factor': 1/10},  # 1/10 = 0.1 packages/oz
            ],
            db=db
        )
        
        # Step 2: Add White Mushrooms
        print("\n--- Step 2: Adding White Mushrooms ---")
        create_ingredient_with_conversions(
            name='White Mushrooms',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 70/227},  # 70/227 = 0.308 packages/cup (sliced)
                {'from': 'gram', 'factor': 1/227},  # 1/227 packages/g
                {'from': 'ounce', 'factor': 1/8},  # 1/8 = 0.125 packages/oz
            ],
            db=db
        )
        
        # Step 3: Add Scallions
        print("\n--- Step 3: Adding Scallions ---")
        create_ingredient_with_conversions(
            name='Scallions',
            type_name='Vegetables',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'cup', 'factor': 50/50},  # 50/50 = 1.0 bunches/cup (chopped)
                {'from': 'tablespoon', 'factor': 6/50},  # 6/50 = 0.12 bunches/tbsp (chopped)
                {'from': 'gram', 'factor': 1/50},  # 1/50 = 0.02 bunches/g
                {'from': 'bunch', 'factor': 1.0},
            ],
            db=db
        )
        
        # Step 4: Add Fresh Thyme
        print("\n--- Step 4: Adding Fresh Thyme ---")
        create_ingredient_with_conversions(
            name='Fresh Thyme',
            type_name='Herbs',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'teaspoon', 'factor': 1/11.67},  # 1/11.67 = 0.0857 bunches/tsp (minced)
                {'from': 'gram', 'factor': 1/14},  # 1/14 = 0.0714 bunches/g
                {'from': 'bunch', 'factor': 1.0},
            ],
            db=db
        )
        
        # Step 5: Add Zucchini
        print("\n--- Step 5: Adding Zucchini ---")
        create_ingredient_with_conversions(
            name='Zucchini',
            type_name='Vegetables',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'cup', 'factor': 120/200},  # 120/200 = 0.6 whole/cup (chopped, medium)
                {'from': 'gram', 'factor': 1/200},  # 1/200 = 0.005 whole/g (medium)
                {'from': 'whole', 'factor': 1.0},
                {'from': 'piece', 'factor': 1.0},
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 150},
                {'size': 'medium', 'unit': 'gram', 'value': 200},
                {'size': 'large', 'unit': 'gram', 'value': 250},
            ],
            db=db
        )
        
        # Step 6: Add Cherry Tomatoes
        print("\n--- Step 6: Adding Cherry Tomatoes ---")
        create_ingredient_with_conversions(
            name='Cherry Tomatoes',
            type_name='Vegetables',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 150/298},  # 150/298 = 0.503 packages/cup
                {'from': 'gram', 'factor': 1/298},  # 1/298 packages/g
                {'from': 'ounce', 'factor': 1/10.5},  # 1/10.5 = 0.0952 packages/oz
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

