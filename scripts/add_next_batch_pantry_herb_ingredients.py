#!/usr/bin/env python3
"""
Script to add pantry/herb ingredients for next batch recipes:
1. Sherry Vinegar
2. Fresh Dill
3. Fresh Chives
4. Fresh Basil
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

def create_ingredient_with_conversions(name, type_name, shopping_unit_name, conversion_rules, db=None):
    """Create an ingredient with conversion rules."""
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
        
        db.commit()
        return ingredient_id
    
    finally:
        if close_after:
            db.close()

def main():
    """Main function to add all pantry/herb ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Pantry/Herb Ingredients for Next Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Sherry Vinegar
        print("\n--- Step 1: Adding Sherry Vinegar ---")
        create_ingredient_with_conversions(
            name='Sherry Vinegar',
            type_name='Pantry Items',
            shopping_unit_name='bottle',
            conversion_rules=[
                {'from': 'tablespoon', 'factor': 1/25},  # 1/25 = 0.04 bottles/tbsp
                {'from': 'teaspoon', 'factor': 1/75},  # 1/75 = 0.0133 bottles/tsp
                {'from': 'cup', 'factor': 1/1.56},  # 1/1.56 = 0.641 bottles/cup
                {'from': 'milliliter', 'factor': 1/375},  # 1/375 bottles/ml
                {'from': 'fluid_ounce', 'factor': 1/12.7},  # 1/12.7 = 0.0787 bottles/fl oz
            ],
            db=db
        )
        
        # Step 2: Add Fresh Dill
        print("\n--- Step 2: Adding Fresh Dill ---")
        create_ingredient_with_conversions(
            name='Fresh Dill',
            type_name='Herbs',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},
                {'from': 'tablespoon', 'factor': 1/14},  # 1/14 = 0.0714 bunches/tbsp (minced)
                {'from': 'cup', 'factor': 8.5/14},  # 8.5/14 = 0.607 bunches/cup (minced)
                {'from': 'gram', 'factor': 1/14},  # 1/14 = 0.0714 bunches/g
            ],
            db=db
        )
        
        # Step 3: Add Fresh Chives
        print("\n--- Step 3: Adding Fresh Chives ---")
        create_ingredient_with_conversions(
            name='Fresh Chives',
            type_name='Herbs',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},
                {'from': 'tablespoon', 'factor': 1/14},  # 1/14 = 0.0714 bunches/tbsp (minced)
                {'from': 'gram', 'factor': 1/14},  # 1/14 = 0.0714 bunches/g
            ],
            db=db
        )
        
        # Step 4: Add Fresh Basil
        print("\n--- Step 4: Adding Fresh Basil ---")
        create_ingredient_with_conversions(
            name='Fresh Basil',
            type_name='Herbs',
            shopping_unit_name='bunch',
            conversion_rules=[
                {'from': 'bunch', 'factor': 1.0},
                {'from': 'cup', 'factor': 20/50},  # 20/50 = 0.4 bunches/cup (chopped, lightly packed)
                {'from': 'tablespoon', 'factor': 2.5/50},  # 2.5/50 = 0.05 bunches/tbsp (chopped)
                {'from': 'gram', 'factor': 1/50},  # 1/50 = 0.02 bunches/g
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All pantry/herb ingredients added successfully!")
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

