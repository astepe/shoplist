#!/usr/bin/env python3
"""
Script to create the Curried Butternut Soup with Rainbow Chard recipe.
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
        WHERE (name LIKE ? OR name LIKE ?) AND is_sub_recipe = 1
        ORDER BY name
        LIMIT 1
    """, (f'%{name_pattern}%', f'%Broth%'))
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
        print("Creating Curried Butternut Soup with Rainbow Chard Recipe")
        print("=" * 60)
        
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE name = ?", 
                      ("Curried Butternut Soup with Rainbow Chard",))
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
        serving_unit_id = get_unit_id("serving", cursor)
        cup_unit_id = get_unit_id("cup", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        clove_unit_id = get_unit_id("clove", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        package_unit_id = get_unit_id("package", cursor)
        
        # Create recipe
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
            VALUES (?, ?, ?, ?)
        """, ("Curried Butternut Soup with Rainbow Chard", False, 4, serving_unit_id))
        
        recipe_id = cursor.lastrowid
        print(f"\n  ✓ Created recipe (ID: {recipe_id})")
        
        # Add recipe items
        items = [
            # 1. 5 cups Vegetable Broth 2.0 (sub-recipe)
            {
                "item_type": "sub_recipe",
                "sub_recipe_id": broth_id,
                "quantity": 5,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 2. 1 small yellow onion, chopped
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Yellow Onion", cursor),
                "quantity": 1,
                "unit_id": whole_unit_id,
                "size_qualifier": "small",
                "preparation_notes": "chopped"
            },
            # 3. 1 large butternut squash, peeled, seeded, and diced
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Butternut Squash", cursor),
                "quantity": 1,
                "unit_id": whole_unit_id,
                "size_qualifier": "large",
                "preparation_notes": "peeled, seeded, and diced"
            },
            # 4. 1 large garlic clove, minced
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Garlic", cursor),
                "quantity": 1,
                "unit_id": clove_unit_id,
                "size_qualifier": "large",
                "preparation_notes": "minced"
            },
            # 5. 1½ tablespoons curry powder
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Curry Powder", cursor),
                "quantity": 1.5,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 6. 1 tablespoon finely grated fresh ginger
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Fresh Ginger", cursor),
                "quantity": 1,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "finely grated"
            },
            # 7. 1 (14.5-ounce) can crushed tomatoes
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Crushed Tomatoes", cursor),
                "quantity": 1,
                "unit_id": package_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
            },
            # 8. ½ teaspoon ground black pepper
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Black Pepper", cursor),
                "quantity": 0.5,
                "unit_id": teaspoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": "ground"
            },
            # 9. 4 cups chopped rainbow chard
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("Rainbow Chard", cursor),
                "quantity": 4,
                "unit_id": cup_unit_id,
                "size_qualifier": None,
                "preparation_notes": "chopped"
            },
            # 10. 2 tablespoons white miso paste
            {
                "item_type": "ingredient",
                "ingredient_id": get_ingredient_id("White Miso Paste", cursor),
                "quantity": 2,
                "unit_id": tablespoon_unit_id,
                "size_qualifier": None,
                "preparation_notes": None
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
        
        # Display recipe summary
        cursor.execute("""
            SELECT ri.item_type, ri.quantity, ut.name as unit_name,
                   ri.size_qualifier, ri.preparation_notes,
                   i.name as ingredient_name, r.name as sub_recipe_name
            FROM recipe_items ri
            LEFT JOIN ingredients i ON ri.ingredient_id = i.id
            LEFT JOIN recipes r ON ri.sub_recipe_id = r.id
            JOIN unit_types ut ON ri.unit_id = ut.id
            WHERE ri.recipe_id = ?
            ORDER BY ri.id
        """, (recipe_id,))
        
        print("\n=== Recipe Items ===")
        for idx, item in enumerate(cursor.fetchall(), 1):
            if item['item_type'] == 'sub_recipe':
                name = item['sub_recipe_name']
            else:
                name = item['ingredient_name']
            
            size_str = f" {item['size_qualifier']}" if item['size_qualifier'] else ""
            prep_str = f" ({item['preparation_notes']})" if item['preparation_notes'] else ""
            
            print(f"  {idx}. {item['quantity']} {item['unit_name']}{size_str} {name}{prep_str}")
        
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

