#!/usr/bin/env python3
"""
Script to add fruit ingredients for new batch recipes:
1. Hass Avocado
2. Mango (fresh)
3. Lime (Fresh Lime Juice)
4. Fresh Cilantro
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
    """Main function to add all fruit ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Fruit Ingredients for New Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Hass Avocado
        print("\n--- Step 1: Adding Hass Avocado ---")
        create_ingredient_with_conversions(
            name='Hass Avocado',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'cup', 'factor': 230/200},  # 230/200 = 1.15 whole/cup (mashed)
                {'from': 'gram', 'factor': 1/200},  # 1/200 = 0.005 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 150},
                {'size': 'medium', 'unit': 'gram', 'value': 200},
                {'size': 'large', 'unit': 'gram', 'value': 250},
            ],
            db=db
        )
        
        # Step 2: Add Mango (fresh)
        print("\n--- Step 2: Adding Mango (fresh) ---")
        create_ingredient_with_conversions(
            name='Mango',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'cup', 'factor': 175/300},  # 175/300 = 0.583 whole/cup (chopped)
                {'from': 'gram', 'factor': 1/300},  # 1/300 = 0.00333 whole/g (medium)
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 200},
                {'size': 'medium', 'unit': 'gram', 'value': 300},
                {'size': 'large', 'unit': 'gram', 'value': 400},
            ],
            db=db
        )
        
        # Step 3: Add Lime (Fresh Lime Juice)
        print("\n--- Step 3: Adding Lime ---")
        create_ingredient_with_conversions(
            name='Lime',
            type_name='Fruits',
            shopping_unit_name='whole',
            conversion_rules=[
                {'from': 'whole', 'factor': 1.0},
                {'from': 'tablespoon', 'factor': 2/15},  # 2/15 = 0.133 whole/tbsp (juice)
                {'from': 'teaspoon', 'factor': 1/7.5},  # 1/7.5 = 0.133 whole/tsp (juice)
                {'from': 'milliliter', 'factor': 30/30},  # 30ml/whole = 1.0 whole/ml
            ],
            size_rules=[
                {'size': 'small', 'unit': 'gram', 'value': 60},
                {'size': 'medium', 'unit': 'gram', 'value': 70},
                {'size': 'large', 'unit': 'gram', 'value': 80},
            ],
            db=db
        )
        
        # Step 4: Add Fresh Cilantro
        print("\n--- Step 4: Adding Fresh Cilantro ---")
        create_ingredient_with_conversions(
            name='Fresh Cilantro',
            type_name='Herbs',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},
                {'from': 'tablespoon', 'factor': 1/28.35},  # 1/28.35 = 0.0353 bunches/tbsp (chopped)
                {'from': 'cup', 'factor': 15/28.35},  # 15/28.35 = 0.529 bunches/cup (chopped)
                {'from': 'gram', 'factor': 1/28.35},  # 1/28.35 = 0.0353 bunches/g
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

