#!/usr/bin/env python3
"""
Script to create the Banana-Almond French Toast with Blueberries recipe.
"""

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import get_db

def get_ingredient_id(name, cursor):
    """Get ingredient ID by name."""
    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Ingredient '{name}' not found")
    return result['id']

def get_unit_id(name, cursor):
    """Get unit type ID by name."""
    cursor.execute("SELECT id FROM unit_types WHERE name = ?", (name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Unit '{name}' not found")
    return result['id']

def get_sub_recipe_id(name_pattern, cursor):
    """Get sub-recipe ID by name pattern."""
    cursor.execute("""
        SELECT id, name FROM recipes 
        WHERE (name LIKE ? OR name LIKE ?) AND is_sub_recipe = 1
        ORDER BY name
        LIMIT 1
    """, (f'%{name_pattern}%', f'%Date Syrup%'))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Sub-recipe '{name_pattern}' not found")
    return result['id'], result['name']

def main():
    """Main function to create the recipe."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Banana-Almond French Toast with Blueberries Recipe")
        print("=" * 60)
        
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Banana-Almond French Toast with Blueberries",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        # Get Date Syrup 2.0 sub-recipe
        try:
            date_syrup_id, date_syrup_name = get_sub_recipe_id("Date Syrup", cursor)
            print(f"  ✓ Found sub-recipe: {date_syrup_name} (ID: {date_syrup_id})")
        except ValueError as e:
            print(f"  ✗ {e}")
            print("  Please create Date Syrup 2.0 recipe first")
            return
        
        # Get unit IDs
        serving_unit_id = get_unit_id("serving", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        
        # Create recipe
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Banana-Almond French Toast with Blueberries", False, 4, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        # Add recipe items
        items = [
            # 1. Banana - 4 whole (medium, 3 blended, 1 sliced)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Banana", cursor),
                "quantity": 4,
                "unit_id": whole_unit_id,
                "size_qualifier": "medium",
                "preparation_notes": "3 blended, 1 sliced"
            },
            # 2. Almond Butter - 0.5 cup
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Almond Butter", cursor),
                "quantity": 0.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 3. Unsweetened Soy Milk - 1.5 cups
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Unsweetened Soy Milk", cursor),
                "quantity": 1.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 4. Pure Vanilla Extract - 1.5 teaspoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor),
                "quantity": 1.5,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 5. Ground Cinnamon - 0.5 teaspoon
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Cinnamon", cursor),
                "quantity": 0.5,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 6. Salt-Free Whole-Grain Sprouted Bread - 8 slices (0.5 package)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Salt-Free Whole-Grain Sprouted Bread", cursor),
                "quantity": 0.5,
                "unit_id": whole_unit_id,  # Using "whole" to represent 0.5 loaf/package
                "size_qualifier": None,
                "preparation_notes": "8 slices"
            },
            # 7. Blueberries - 1 cup
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Blueberries", cursor),
                "quantity": 1,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 8. Date Syrup 2.0 - 0.5 cup
            {
                "item_type": "sub_recipe",
                "sub_recipe_id": date_syrup_id,
                "quantity": 0.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
        ]
        
        # Insert items
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

