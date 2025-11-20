#!/usr/bin/env python3
"""
Script to add plant protein/canned ingredients for next batch recipes:
1. Salt-Free Black Beans
2. Salt-Free Crushed Tomatoes
3. Salt-Free Diced Tomatoes
4. Shelled Edamame
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
    """Main function to add all plant protein/canned ingredients."""
    db = get_db()
    
    try:
        print("=" * 60)
        print("Adding Plant Protein/Canned Ingredients for Next Batch Recipes")
        print("=" * 60)
        
        # Step 1: Add Salt-Free Black Beans
        print("\n--- Step 1: Adding Salt-Free Black Beans ---")
        create_ingredient_with_conversions(
            name='Salt-Free Black Beans',
            type_name='Plant Proteins',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'cup', 'factor': 165/425},  # 165/425 = 0.388 cans/cup
                {'from': 'gram', 'factor': 1/425},  # 1/425 cans/g
                {'from': 'ounce', 'factor': 1/15},  # 1/15 = 0.0667 cans/oz
            ],
            db=db
        )
        
        # Step 2: Add Salt-Free Crushed Tomatoes
        print("\n--- Step 2: Adding Salt-Free Crushed Tomatoes ---")
        create_ingredient_with_conversions(
            name='Salt-Free Crushed Tomatoes',
            type_name='Pantry Items',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'gram', 'factor': 1/411},  # 1/411 cans/g
                {'from': 'ounce', 'factor': 1/14.5},  # 1/14.5 = 0.0690 cans/oz
                {'from': 'cup', 'factor': 242/411},  # 242/411 = 0.589 cans/cup
            ],
            db=db
        )
        
        # Step 3: Add Salt-Free Diced Tomatoes
        print("\n--- Step 3: Adding Salt-Free Diced Tomatoes ---")
        create_ingredient_with_conversions(
            name='Salt-Free Diced Tomatoes',
            type_name='Pantry Items',
            shopping_unit_name='can',
            conversion_rules=[
                {'from': 'gram', 'factor': 1/411},  # 1/411 cans/g
                {'from': 'ounce', 'factor': 1/14.5},  # 1/14.5 = 0.0690 cans/oz
                {'from': 'cup', 'factor': 180/411},  # 180/411 = 0.438 cans/cup (drained)
            ],
            db=db
        )
        
        # Step 4: Add Shelled Edamame
        print("\n--- Step 4: Adding Shelled Edamame ---")
        create_ingredient_with_conversions(
            name='Shelled Edamame',
            type_name='Plant Proteins',
            shopping_unit_name='package',
            conversion_rules=[
                {'from': 'cup', 'factor': 120/340},  # 120/340 = 0.353 packages/cup
                {'from': 'gram', 'factor': 1/340},  # 1/340 packages/g
                {'from': 'ounce', 'factor': 1/12},  # 1/12 = 0.0833 packages/oz
            ],
            db=db
        )
        
        print("\n" + "=" * 60)
        print("✓ All plant protein/canned ingredients added successfully!")
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

