#!/usr/bin/env python3
"""
Script to create the Buckwheat Noodles with Cabbage and Creamy Cashew Sauce recipe.
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
    # Find best match
    for r in results:
        if name_pattern.lower() in r['name'].lower():
            return r['id'], r['name']
    return results[0]['id'], results[0]['name']

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Buckwheat Noodles with Cabbage and Creamy Cashew Sauce Recipe")
        print("=" * 60)
        
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Buckwheat Noodles with Cabbage and Creamy Cashew Sauce",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        # Get sub-recipes
        creamy_cashew_id, creamy_cashew_name = get_sub_recipe_id("Creamy Cashew Sauce", cursor)
        nutty_parm_id, nutty_parm_name = get_sub_recipe_id("Nutty Parm", cursor)
        print(f"  ✓ Found sub-recipe: {creamy_cashew_name} (ID: {creamy_cashew_id})")
        print(f"  ✓ Found sub-recipe: {nutty_parm_name} (ID: {nutty_parm_id})")
        
        serving_unit_id = get_unit_id("serving", cursor)
        pound_unit_id = get_unit_id("pound", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        clove_unit_id = get_unit_id("clove", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        ounce_unit_id = get_unit_id("ounce", cursor)
        fluid_ounce_unit_id = get_unit_id("fluid_ounce", cursor)
        package_unit_id = get_unit_id("package", cursor)
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Buckwheat Noodles with Cabbage and Creamy Cashew Sauce", False, 4, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Savoy Cabbage", cursor), "quantity": 1, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "450g, shredded"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "cored, seeded, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Sage", cursor), "quantity": 6, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "6 fresh sage leaves, or ½ teaspoon dried or ground sage, plus more for garnish"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Buckwheat Noodles", cursor), "quantity": 8, "unit_id": ounce_unit_id, "size_qualifier": None, "preparation_notes": "225g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Frozen Green Peas", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "125g, frozen or fresh"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with ¼ cup hot water, 60ml"},
            {"item_type": "sub_recipe", "sub_recipe_id": creamy_cashew_id, "quantity": 1, "unit_id": package_unit_id, "size_qualifier": None, "preparation_notes": "as needed"},
            {"item_type": "sub_recipe", "sub_recipe_id": nutty_parm_id, "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": None},
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
        print(f"\n  ✓ Added {len(items)} items to recipe")
        print("\n" + "=" * 60)
        print("✓ Recipe created successfully!")
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

