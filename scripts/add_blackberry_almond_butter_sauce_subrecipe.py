#!/usr/bin/env python3
"""
Script to create the Blackberry-Almond Butter Sauce sub-recipe.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db

def get_ingredient_id(name, cursor):
    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Ingredient '{name}' not found")
    return result['id']

def get_unit_id(name, cursor):
    cursor.execute("SELECT id FROM unit_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Unit '{name}' not found")
    return result['id']

def get_sub_recipe_id(name_pattern, cursor):
    cursor.execute("""
        SELECT id, name FROM recipes 
        WHERE (name LIKE ? OR name LIKE ?) AND is_sub_recipe = 1
        ORDER BY name
        LIMIT 1
    """, (f'%{name_pattern}%', f'%{name_pattern.split()[0]}%'))
    results = cursor.fetchall()
    if not results:
        raise ValueError(f"Sub-recipe '{name_pattern}' not found")
    for r in results:
        if name_pattern.lower() in r['name'].lower():
            return r['id'], r['name']
    return results[0]['id'], results[0]['name']

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Blackberry-Almond Butter Sauce Sub-Recipe")
        print("=" * 60)
        
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Blackberry-Almond Butter Sauce",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        cup_unit_id = get_unit_id("cup", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        date_syrup_id, _ = get_sub_recipe_id("Date Syrup", cursor)
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Blackberry-Almond Butter Sauce", True, 1, cup_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created sub-recipe (ID: {recipe_id})")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Blackberries", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "110g, fresh or thawed frozen, or Frozen Blackberries"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Unsweetened Soy Milk", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60ml"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Butter", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh lemon juice"},
        ]
        
        for item in items:
            cursor.execute("""
                INSERT INTO recipe_items 
                (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_id,
                item["item_type"],
                item.get("ingredient_id"),
                item.get("sub_recipe_id"),
                item["quantity"],
                item["unit_id"],
                item["size_qualifier"],
                item["preparation_notes"]
            ))
        
        db.commit()
        print(f"\n  ✓ Added {len(items)} items to sub-recipe")
        print("\n" + "=" * 60)
        print("✓ Sub-recipe created successfully!")
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

