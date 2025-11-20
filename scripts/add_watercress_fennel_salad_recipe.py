#!/usr/bin/env python3
"""
Script to create the Watercress and Fennel Salad with Ginger-Pear Dressing recipe.
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

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Watercress and Fennel Salad with Ginger-Pear Dressing Recipe")
        print("=" * 60)
        
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Watercress and Fennel Salad with Ginger-Pear Dressing",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        serving_unit_id = get_unit_id("serving", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        bunch_unit_id = get_unit_id("bunch", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        stalk_unit_id = get_unit_id("whole", cursor)  # Use 'whole' for celery stalk
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Watercress and Fennel Salad with Ginger-Pear Dressing", False, 6, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        items = [
            # For the Dressing:
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pear", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "ripe, peeled, cored, coarsely chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Shallot", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Ginger", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Apple Cider Vinegar", cursor), "quantity": 1.5, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "or fresh lemon juice"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            # For the Salad:
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Watercress", cursor), "quantity": 2, "unit_id": bunch_unit_id, "size_qualifier": None, "preparation_notes": "tough stems removed and discarded, coarsely chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fennel Bulb", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "thinly sliced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Mixed Baby Greens", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "90g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Celery", cursor), "quantity": 1, "unit_id": stalk_unit_id, "size_qualifier": "small", "preparation_notes": "thinly sliced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Pecans", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "25g, pieces"},
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

