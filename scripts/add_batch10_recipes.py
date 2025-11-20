#!/usr/bin/env python3
"""
Script to add all 10 main recipes for Batch 10:
1. Roasted Root Vegetables with Balsamic Syrup
2. Braised Red Cabbage with Apples and Walnuts
3. Garlicky Mashed Potatoes with Chard
4. Broccoli with Sesame-Miso Sauce
5. Green Beans and Grape Tomatoes with Garlic and Pine Nuts
6. Roasted Asparagus with Tahini Lemon Sauce
7. Indian-Inspired Spiced Cauliflower
8. Roasted Brussels Sprouts with Pecans and Shallots
9. Spaghetti Squash with Edamame and Basil Pistou
10. Mixed Berry Crumble
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

def create_recipe(name, is_sub_recipe, yield_quantity, yield_unit_name, items, cursor):
    """Create a recipe with items."""
    yield_unit_id = get_unit_id(yield_unit_name, cursor)
    
    # Check if recipe already exists
    cursor.execute("SELECT id FROM recipes WHERE name = ?", (name,))
    existing = cursor.fetchone()
    if existing:
        print(f"  ⚠ Recipe '{name}' already exists (ID: {existing['id']}) - skipping")
        return existing['id']
    
    cursor.execute("""
        INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
        VALUES (?, ?, ?, ?)
    """, (name, is_sub_recipe, yield_quantity, yield_unit_id))
    
    recipe_id = cursor.lastrowid
    print(f"  ✓ Created recipe '{name}' (ID: {recipe_id})")
    
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
            item.get("size_qualifier"),
            item.get("preparation_notes")
        ))
    
    print(f"    ✓ Added {len(items)} items")
    return recipe_id

def main():
    db = get_db()
    cursor = db.cursor()
    
    try:
        print("=" * 60)
        print("Creating Batch 10 Recipes")
        print("=" * 60)
        
        # Get common unit IDs
        cup_unit_id = get_unit_id("cup", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        clove_unit_id = get_unit_id("clove", cursor)
        serving_unit_id = get_unit_id("serving", cursor)
        pound_unit_id = get_unit_id("pound", cursor)
        
        # Recipe 1: Roasted Root Vegetables with Balsamic Syrup
        print("\n--- Recipe 1: Roasted Root Vegetables with Balsamic Syrup ---")
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        balsamic_syrup_id, _ = get_sub_recipe_id("Balsamic Syrup", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Carrot", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Parsnip", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Purple Sweet Potatoes", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sweet Potato", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Beets", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 3, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "crushed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Marjoram", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Thyme", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "dried thyme"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "sub_recipe", "sub_recipe_id": balsamic_syrup_id, "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60ml"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Parsley", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "minced, or Fresh Thyme or other fresh herb"},
        ]
        
        create_recipe("Roasted Root Vegetables with Balsamic Syrup", False, 4, "serving", items, cursor)
        
        # Recipe 2: Braised Red Cabbage with Apples and Walnuts
        print("\n--- Recipe 2: Braised Red Cabbage with Apples and Walnuts ---")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Purple Cabbage", cursor), "quantity": 1.5, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "700g, shredded"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Apple", cursor), "quantity": 2, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "Granny Smith, cored and diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Ginger", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Apple Cider Vinegar", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60ml"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Date Sugar", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper, to taste"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Walnuts", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "35g, walnut pieces"},
        ]
        
        create_recipe("Braised Red Cabbage with Apples and Walnuts", False, 4, "serving", items, cursor)
        
        # Recipe 3: Garlicky Mashed Potatoes with Chard
        print("\n--- Recipe 3: Garlicky Mashed Potatoes with Chard ---")
        roasted_garlic_id, _ = get_sub_recipe_id("Roasted Garlic", cursor)
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Yukon Gold Potatoes", cursor), "quantity": 2.5, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "1kg, peeled and cut into chunks, or Russet Potatoes"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rainbow Chard", cursor), "quantity": 4, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "180g, finely chopped Swiss chard"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Unsweetened Soy Milk", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "80ml, warm"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "sub_recipe", "sub_recipe_id": roasted_garlic_id, "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "1 head"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 1.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper, to taste"},
        ]
        
        create_recipe("Garlicky Mashed Potatoes with Chard", False, 4, "serving", items, cursor)
        
        # Recipe 4: Broccoli with Sesame-Miso Sauce
        print("\n--- Recipe 4: Broccoli with Sesame-Miso Sauce ---")
        roasted_garlic_id, _ = get_sub_recipe_id("Roasted Garlic", cursor)
        
        items = [
            {"item_type": "sub_recipe", "sub_recipe_id": roasted_garlic_id, "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tahini", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rice Vinegar", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Date Sugar", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "implied in instructions"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Broccoli Florets", cursor), "quantity": 4.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "360 to 450g, small florets"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Sesame Seeds", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "or Black Sesame Seeds, for garnish"},
        ]
        
        create_recipe("Broccoli with Sesame-Miso Sauce", False, 4, "serving", items, cursor)
        
        # Recipe 5: Green Beans and Grape Tomatoes with Garlic and Pine Nuts
        print("\n--- Recipe 5: Green Beans and Grape Tomatoes with Garlic and Pine Nuts ---")
        roasted_garlic_id, _ = get_sub_recipe_id("Roasted Garlic", cursor)
        balsamic_syrup_id, _ = get_sub_recipe_id("Balsamic Syrup", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pine Nuts", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "35g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Grape Tomatoes", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "150g, halved lengthwise"},
            {"item_type": "sub_recipe", "sub_recipe_id": roasted_garlic_id, "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "1 head"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Green Beans", cursor), "quantity": 1, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "450g, trimmed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Basil", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "torn fresh basil leaves"},
            {"item_type": "sub_recipe", "sub_recipe_id": balsamic_syrup_id, "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper, to taste"},
        ]
        
        create_recipe("Green Beans and Grape Tomatoes with Garlic and Pine Nuts", False, 4, "serving", items, cursor)
        
        # Recipe 6: Roasted Asparagus with Tahini Lemon Sauce
        print("\n--- Recipe 6: Roasted Asparagus with Tahini Lemon Sauce ---")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Asparagus", cursor), "quantity": 1.5, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "680g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh lemon juice"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tahini", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "as needed, for sauce consistency"},
        ]
        
        create_recipe("Roasted Asparagus with Tahini Lemon Sauce", False, 4, "serving", items, cursor)
        
        # Recipe 7: Indian-Inspired Spiced Cauliflower
        print("\n--- Recipe 7: Indian-Inspired Spiced Cauliflower ---")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Cauliflower Florets", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "1 large head equivalent, cut into small florets"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "50g, grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Ginger", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tomato Puree", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Coriander", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Yellow Curry Powder", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "curry powder"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Black Cumin (Nigella Seeds)", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Turmeric", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Fenugreek Seeds", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Cayenne", cursor), "quantity": 0.125, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "or more to taste"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Cashews", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "30g, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Cilantro", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "chopped"},
        ]
        
        create_recipe("Indian-Inspired Spiced Cauliflower", False, 4, "serving", items, cursor)
        
        # Recipe 8: Roasted Brussels Sprouts with Pecans and Shallots
        print("\n--- Recipe 8: Roasted Brussels Sprouts with Pecans and Shallots ---")
        date_syrup_id, _ = get_sub_recipe_id("Date Syrup", cursor)
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pecan Halves", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "50g"},
            {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Brussels Sprouts", cursor), "quantity": 1, "unit_id": pound_unit_id, "size_qualifier": None, "preparation_notes": "450g, trimmed and halved lengthwise"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Shallot", cursor), "quantity": 3.5, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "3 or 4 small, quartered lengthwise"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh lemon juice"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
        ]
        
        create_recipe("Roasted Brussels Sprouts with Pecans and Shallots", False, 4, "serving", items, cursor)
        
        # Recipe 9: Spaghetti Squash with Edamame and Basil Pistou
        print("\n--- Recipe 9: Spaghetti Squash with Edamame and Basil Pistou ---")
        roasted_garlic_id, _ = get_sub_recipe_id("Roasted Garlic", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Spaghetti Squash", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "about 4 pounds / 2kg"},
            {"item_type": "sub_recipe", "sub_recipe_id": roasted_garlic_id, "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "1 head"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Basil", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "90g, fresh basil leaves"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "as needed, for pistou consistency"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Shelled Edamame", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "180g, cooked"},
        ]
        
        create_recipe("Spaghetti Squash with Edamame and Basil Pistou", False, 4, "serving", items, cursor)
        
        # Recipe 10: Mixed Berry Crumble
        print("\n--- Recipe 10: Mixed Berry Crumble ---")
        date_syrup_id, _ = get_sub_recipe_id("Date Syrup", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Mixed Berries", cursor), "quantity": 2.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "400g, fresh or frozen"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "lemon juice"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Date Sugar", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chia Seeds", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rolled Oats", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "100g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Flour", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "55g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Butter", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "75g"},
            {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60ml"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Walnuts", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "25g, walnut pieces, optional"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "grated lemon zest, for garnish, optional"},
        ]
        
        create_recipe("Mixed Berry Crumble", False, 4, "serving", items, cursor)
        
        db.commit()
        print("\n" + "=" * 60)
        print("✓ All 10 recipes created successfully!")
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

