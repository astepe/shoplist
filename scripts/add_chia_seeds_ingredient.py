#!/usr/bin/env python3
"""
Script to add Chia Seeds ingredient.
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

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Adding Chia Seeds Ingredient")
        print("=" * 60)
        
        # Check if ingredient already exists
        cursor.execute("SELECT id FROM ingredients WHERE name = ?", ("Chia Seeds",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Chia Seeds already exists (ID: {existing['id']}) - skipping")
            return existing['id']
        
        # Get IDs
        type_id = get_type_id("Nuts & Seeds", cursor)
        shopping_unit_id = get_unit_id("package", cursor)
        
        # Create ingredient
        cursor.execute("""
            INSERT INTO ingredients (name, type_id, shopping_unit_id)
            VALUES (?, ?, ?)
        """, ("Chia Seeds", type_id, shopping_unit_id))
        
        ingredient_id = cursor.lastrowid
        print(f"  ✓ Created Chia Seeds (ID: {ingredient_id})")
        
        # Add conversion rules
        # Chia seeds typically come in packages (estimate 12 oz / 340g package)
        conversion_rules = [
            {'from': 'package', 'factor': 1.0},  # 1.0 (12 oz / 340g package)
            {'from': 'tablespoon', 'factor': 10/340},  # 0.0294 packages/tbsp (1 tbsp ≈ 10g)
            {'from': 'cup', 'factor': 180/340},  # 0.529 packages/cup (estimate 1 cup = 180g)
            {'from': 'gram', 'factor': 1/340},  # 0.00294 packages/g
            {'from': 'ounce', 'factor': 1/12},  # 0.0833 packages/oz
        ]
        
        for rule in conversion_rules:
            from_unit_id = get_unit_id(rule['from'], cursor)
            cursor.execute("""
                INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, from_unit_id, shopping_unit_id, rule['factor']))
            print(f"    ✓ Conversion: {rule['from']} → package: {rule['factor']:.6f}")
        
        db.commit()
        print("\n" + "=" * 60)
        print("✓ Chia Seeds added successfully!")
        print("=" * 60)
        
        return ingredient_id
        
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

