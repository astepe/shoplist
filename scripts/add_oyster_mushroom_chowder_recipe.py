#!/usr/bin/env python3
"""
Script to create the Oyster Mushroom Chowder recipe.
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
    """, (f'%{name_pattern}%', f'%Broth%'))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Sub-recipe '{name_pattern}' not found")
    return result['id'], result['name']

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Oyster Mushroom Chowder Recipe")
        print("=" * 60)
        
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Oyster Mushroom Chowder",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        # Get sub-recipe
        broth_id, broth_name = get_sub_recipe_id("Vegetable Broth", cursor)
        print(f"  ✓ Found sub-recipe: {broth_name} (ID: {broth_id})")
        
        serving_unit_id = get_unit_id("serving", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        rib_unit_id = get_unit_id("rib", cursor)
        clove_unit_id = get_unit_id("clove", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        ounce_unit_id = get_unit_id("ounce", cursor)
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Oyster Mushroom Chowder", False, 4, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        items = [
            {"item_type": "sub_recipe", "sub_recipe_id": broth_id, "quantity": 5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "1.2L, or use water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Yellow Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Carrot", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Celery", cursor), "quantity": 1, "unit_id": rib_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Yellow Potatoes", cursor), "quantity": 3, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Oyster Mushrooms", cursor), "quantity": 8, "unit_id": ounce_unit_id, "size_qualifier": None, "preparation_notes": "225g, fresh, coarsely chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Mushrooms", cursor), "quantity": 8, "unit_id": ounce_unit_id, "size_qualifier": None, "preparation_notes": "225g, coarsely chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Parsley", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "15g, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Thyme", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "minced, or ½ teaspoon dried"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sherry Vinegar", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "or apple cider vinegar"},
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

