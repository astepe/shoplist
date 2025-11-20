#!/usr/bin/env python3
"""
Script to create the Baked Carrot Cake Oatmeal recipe.
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

def main():
    """Main function to create the recipe."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Baked Carrot Cake Oatmeal Recipe")
        print("=" * 60)
        
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Baked Carrot Cake Oatmeal",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
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
        """, ("Baked Carrot Cake Oatmeal", False, 4, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        # Add recipe items
        items = [
            # 1. Rolled Oats - 2 cups
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Rolled Oats", cursor),
                "quantity": 2,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 2. Ground Chia Seeds - 2 tablespoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Chia Seeds", cursor),
                "quantity": 2,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 3. Ground Flaxseeds - 2 tablespoons
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Flaxseeds", cursor),
                "quantity": 2,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 4. Unsweetened Soy Milk - 2.5 cups
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Unsweetened Soy Milk", cursor),
                "quantity": 2.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 5. Pure Vanilla Extract - 1 teaspoon
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor),
                "quantity": 1,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 6. Ground Cinnamon - 1 teaspoon
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Ground Cinnamon", cursor),
                "quantity": 1,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 7. Raw Pecans - 0.25 cup
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Raw Pecans", cursor),
                "quantity": 0.25,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 8. Carrot - 1 cup grated
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Carrot", cursor),
                "quantity": 1,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "grated"
            },
            # 9. Pitted Dates - 0.5 cup (softened)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Pitted Dates", cursor),
                "quantity": 0.5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "softened"
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

