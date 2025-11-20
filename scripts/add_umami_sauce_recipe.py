#!/usr/bin/env python3
"""
Script to create the Umami Sauce 2.0 recipe.
"""

import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import get_db
from backend.services import check_circular_reference

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
        WHERE name LIKE ? AND is_sub_recipe = 1
        ORDER BY name
        LIMIT 1
    """, (f'%{name_pattern}%',))
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
        print("Creating Umami Sauce 2.0 Recipe")
        print("=" * 60)
        
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Umami Sauce 2.0",))
        existing = cursor.fetchone()
        if existing:
            print(f"  ⚠ Recipe already exists (ID: {existing['id']}) - skipping")
            return
        
        # Get Vegetable Broth 2.0 sub-recipe
        try:
            broth_id, broth_name = get_sub_recipe_id("Vegetable Broth", cursor)
            print(f"  ✓ Found sub-recipe: {broth_name} (ID: {broth_id})")
        except ValueError as e:
            print(f"  ✗ {e}")
            print("  Please create Vegetable Broth 2.0 recipe first")
            return
        
        # Get unit IDs
        cup_unit_id = get_unit_id("cup", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        
        # Create recipe
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Umami Sauce 2.0", True, 1.25, cup_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        # Add recipe items
        items = [
            # 1. 1 cup Vegetable Broth 2.0 (sub-recipe)
            {
                "item_type": "sub_recipe",
                "sub_recipe_id": broth_id,
                "quantity": 1,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 2. 2 teaspoons minced garlic
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Garlic", cursor),
                "quantity": 2,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "minced"
            },
            # 3. 1 teaspoon grated fresh ginger
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Fresh Ginger", cursor),
                "quantity": 1,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "grated"
            },
            # 4. 1.5 tablespoons blackstrap molasses
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Blackstrap Molasses", cursor),
                "quantity": 1.5,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 5. 1 teaspoon salt-free tomato paste
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Salt-Free Tomato Paste", cursor),
                "quantity": 1,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 6. 0.5 teaspoon ground black pepper
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Black Pepper", cursor),
                "quantity": 0.5,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "ground"
            },
            # 7. 2 teaspoons white miso paste (blended with 2 tablespoons hot water)
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("White Miso Paste", cursor),
                "quantity": 2,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "blended with 2 tablespoons hot water"
            },
            # 8. 1 tablespoon apple cider vinegar
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Apple Cider Vinegar", cursor),
                "quantity": 1,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 9. 1 tablespoon fresh lemon juice
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Lemon", cursor),
                "quantity": 1,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "fresh lemon juice"
            },
        ]
        
        # Add each item
        for item in items:
            # Check for circular reference if adding sub-recipe
            if item['item_type'] == 'sub_recipe':
                if check_circular_reference(recipe_id, item['sub_recipe_id'], db):
                    raise ValueError("Cannot add sub-recipe: it would create a circular reference")
            
            cursor.execute("""
                INSERT INTO recipe_items (recipe_id, item_type, ingredient_id, sub_recipe_id,
                                         quantity, unit_id, size_qualifier, preparation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_id,
                item['item_type'],
                item.get('ingredient_id'),
                item.get('sub_recipe_id'),
                item['quantity'],
                item['unit_id'],
                item.get('size_qualifier'),
                item.get('preparation_notes')
            ))
        
        db.commit()
        print(f"\n  ✓ Added {len(items)} recipe items")
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

