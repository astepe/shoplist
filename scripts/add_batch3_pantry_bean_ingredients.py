#!/usr/bin/env python3
"""
Script to add pantry/bean ingredients for batch 3 recipes:
1. Rice Vinegar
2. Salt-Free Red Kidney Beans
3. Salt-Free White Beans
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
    """Main function to add all pantry/bean ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Pantry/Bean Ingredients for Batch 3 Recipes")
        print("=" * 60)
        
        # Step 1: Add Rice Vinegar
        print("\n--- Step 1: Adding Rice Vinegar ---")
        create_ingredient_with_conversions(
            name='Rice Vinegar',
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
        
        # Step 2: Add Salt-Free Red Kidney Beans
        print("\n--- Step 2: Adding Salt-Free Red Kidney Beans ---")
        create_ingredient_with_conversions(
            name='Salt-Free Red Kidney Beans',
            type_name='Plant Proteins',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'cup', 'factor': 165/425},  # 165/425 = 0.388 cans/cup
                {'from': 'gram', 'factor': 1/425},  # 1/425 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 1/15 = 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 3: Add Salt-Free White Beans
        print("\n--- Step 3: Adding Salt-Free White Beans ---")
        create_ingredient_with_conversions(
            name='Salt-Free White Beans',
            type_name='Plant Proteins',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'cup', 'factor': 165/425},  # 165/425 = 0.388 cans/cup
                {'from': 'gram', 'factor': 1/425},  # 1/425 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 1/15 = 0.0667 cans/oz
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All pantry/bean ingredients added successfully!")
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

