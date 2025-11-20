#!/usr/bin/env python3
"""
Script to add all 10 main recipes for Batch 8:
1. Pinto Bean and Sweet Potato Enchiladas
2. Chickpea and Bulgur Loaf
3. Red Bean and Tempeh Jambalaya
4. Roasted Butternut Squash with Pinto Beans and Corn
5. Sambal-Topped Soy Curls and Vegetable Stir-Fry
6. Black Bean Stew with Purple Sweet Potatoes
7. White Bean Cassoulet
8. Tempeh Satay with Spicy Peanut Sauce
9. Tempeh and Mushroom Chili with Corn and Cilantro
10. Two-Lentil Dal
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
        print("Creating Batch 8 Recipes")
        print("=" * 60)
        
        # Get common unit IDs
        cup_unit_id = get_unit_id("cup", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        clove_unit_id = get_unit_id("clove", cursor)
        serving_unit_id = get_unit_id("serving", cursor)
        ounce_unit_id = get_unit_id("ounce", cursor)
        can_unit_id = get_unit_id("can", cursor)
        
        # Recipe 1: Pinto Bean and Sweet Potato Enchiladas
        print("\n--- Recipe 1: Pinto Bean and Sweet Potato Enchiladas ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        cheesy_sauce_id, _ = get_sub_recipe_id("Cheesy Sauce", cursor)
        
        items = [
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60ml, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "cored, seeded, and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Tomato Sauce", cursor), "quantity": 1, "unit_id": can_unit_id, "size_qualifier": None, "preparation_notes": "15 oz / 400g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chili Powder", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "hot or mild, or to taste"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Black Cumin (Nigella Seeds)", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Oregano", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Onion Powder", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Sodium-Free Salt Substitute", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Pinto Beans", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "375g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Purple Sweet Potatoes", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "cooked and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chili Powder", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "hot or mild"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Corn Kernels", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "165g, fresh or thawed frozen"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Scallions", cursor), "quantity": 3, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "green and white parts, minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Cilantro", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "30g, minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Whole-Grain Salt-Free Tortillas", cursor), "quantity": 8, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "8-inch/20-cm"},
            {"item_type": "sub_recipe", "sub_recipe_id": cheesy_sauce_id, "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "optional, to serve"},
        ]
        
        create_recipe("Pinto Bean and Sweet Potato Enchiladas", False, 4, "serving", items, cursor)
        
        # Recipe 2: Chickpea and Bulgur Loaf
        print("\n--- Recipe 2: Chickpea and Bulgur Loaf ---")
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        umami_sauce_id, _ = get_sub_recipe_id("Umami Sauce", cursor)
        bulgur_id = get_ingredient_id("Medium Bulgur", cursor)  # Use existing Medium Bulgur
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 0.75, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "90g, minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Carrot", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "55g, minced or grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Celery", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g, minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Mushrooms", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "35g, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": bulgur_id, "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "85g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Flaxseeds", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Chickpeas", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "370g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Nutritional Yeast", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tomato Paste", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chickpea Flour", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Whole-Grain Bread Crumbs", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 1.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "sub_recipe", "sub_recipe_id": umami_sauce_id, "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "optional, to serve"},
        ]
        
        create_recipe("Chickpea and Bulgur Loaf", False, 4, "serving", items, cursor)
        
        # Recipe 3: Red Bean and Tempeh Jambalaya
        print("\n--- Recipe 3: Red Bean and Tempeh Jambalaya ---")
        umami_sauce_id, _ = get_sub_recipe_id("Umami Sauce", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tempeh", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "8 oz / 230g package"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Celery", cursor), "quantity": 2, "unit_id": get_unit_id("rib", cursor), "size_qualifier": None, "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Green Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "cored, seeded, and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Red Kidney Beans", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "810g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Diced Tomatoes", cursor), "quantity": 1, "unit_id": can_unit_id, "size_qualifier": None, "preparation_notes": "14.5 oz / 400g, drained"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Crushed Tomatoes", cursor), "quantity": 1, "unit_id": can_unit_id, "size_qualifier": None, "preparation_notes": "14.5 oz / 400g, undrained"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.5 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Thyme", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "dried thyme"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Marjoram", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "sub_recipe", "sub_recipe_id": umami_sauce_id, "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Pepper Flakes", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "or to taste"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Cayenne", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "or to taste"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Filé Powder", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
            # Note: Cooked brown rice is typically prepared separately and mixed in at the end
            # For now, skipping this as it's a prepared item, not a raw ingredient
            # {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Brown Rice (cooked)", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "600g, cooked, or other favorite cooked whole grain"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Parsley", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "chopped"},
        ]
        
        create_recipe("Red Bean and Tempeh Jambalaya", False, 6, "serving", items, cursor)
        
        # Recipe 4: Roasted Butternut Squash with Pinto Beans and Corn
        print("\n--- Recipe 4: Roasted Butternut Squash with Pinto Beans and Corn ---")
        savory_spice_id, _ = get_sub_recipe_id("Savory Spice Blend", cursor)
        balsamic_syrup_id, _ = get_sub_recipe_id("Balsamic Syrup", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Butternut Squash", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "cored, seeded, and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Corn Kernels", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "240g, fresh or frozen"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chile Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "hot or mild, seeded and minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Pinto Beans", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "375g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Green Cabbage", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "95g, shredded"},
            {"item_type": "sub_recipe", "sub_recipe_id": savory_spice_id, "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Cilantro", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "or Fresh Parsley, minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pepitas (Pumpkin Seeds)", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lime", cursor), "quantity": 1.5, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh lime juice, 1 to 2 tablespoons"},
            {"item_type": "sub_recipe", "sub_recipe_id": balsamic_syrup_id, "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
        ]
        
        create_recipe("Roasted Butternut Squash with Pinto Beans and Corn", False, 4, "serving", items, cursor)
        
        # Recipe 5: Sambal-Topped Soy Curls and Vegetable Stir-Fry
        print("\n--- Recipe 5: Sambal-Topped Soy Curls and Vegetable Stir-Fry ---")
        date_syrup_id, _ = get_sub_recipe_id("Date Syrup", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "cored, seeded, and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chile Pepper", cursor), "quantity": 1.5, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "1 or 2 hot red chile peppers, cored, seeded, and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 1, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "smashed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Turmeric", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "0.5-inch/1-cm piece, grated, or 0.5 teaspoon Ground Turmeric"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "or Date Sugar"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rice Vinegar", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Soy Curls", cursor), "quantity": 4, "unit_id": ounce_unit_id, "size_qualifier": None, "preparation_notes": "115g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Broccoli Florets", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "250g, small florets"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "or Yellow Bell Pepper, cored, seeded, and thinly sliced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Mushrooms", cursor), "quantity": 8, "unit_id": ounce_unit_id, "size_qualifier": None, "preparation_notes": "225g, sliced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Scallions", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "minced, green and white parts"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Ginger", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "grated"},
        ]
        
        create_recipe("Sambal-Topped Soy Curls and Vegetable Stir-Fry", False, 4, "serving", items, cursor)
        
        # Recipe 6: Black Bean Stew with Purple Sweet Potatoes
        print("\n--- Recipe 6: Black Bean Stew with Purple Sweet Potatoes ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Purple Sweet Potatoes", cursor), "quantity": 2, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "peeled and cut into 0.5-inch/1-cm dice, about 4 cups/440g diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "cored, seeded, and diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Jalapeño", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "small", "preparation_notes": "seeded and minced, optional"},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 2, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "470ml, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Black Beans", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "750g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Diced Tomatoes", cursor), "quantity": 1, "unit_id": can_unit_id, "size_qualifier": None, "preparation_notes": "14.5 oz / 400g, undrained"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Mango", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "ripe, peeled, pitted, and diced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Cilantro", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "30g, chopped"},
        ]
        
        create_recipe("Black Bean Stew with Purple Sweet Potatoes", False, 4, "serving", items, cursor)
        
        # Recipe 7: White Bean Cassoulet
        print("\n--- Recipe 7: White Bean Cassoulet ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Carrot", cursor), "quantity": 2, "unit_id": whole_unit_id, "size_qualifier": "large", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Celery", cursor), "quantity": 1, "unit_id": get_unit_id("rib", cursor), "size_qualifier": None, "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 3, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Great Northern Beans", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "740g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Cannellini Beans", cursor), "quantity": 1.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "375g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Crushed Tomatoes", cursor), "quantity": 1, "unit_id": can_unit_id, "size_qualifier": None, "preparation_notes": "14.5 oz / 400g, undrained"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Parsley", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Thyme", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "dried thyme"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Savory", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.5 cup / 120ml hot water or Vegetable Broth 2.0"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Whole-Grain Bread Crumbs", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "60g"},
        ]
        
        create_recipe("White Bean Cassoulet", False, 4, "serving", items, cursor)
        
        # Recipe 8: Tempeh Satay with Spicy Peanut Sauce
        print("\n--- Recipe 8: Tempeh Satay with Spicy Peanut Sauce ---")
        date_syrup_id, _ = get_sub_recipe_id("Date Syrup", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 1, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Creamy Peanut Butter", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rice Vinegar", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Cayenne", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "or to taste"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tempeh", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "8 oz / 230g package"},
            {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Ginger", cursor), "quantity": 1.5, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lime", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "fresh lime juice"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rice Vinegar", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 1, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Coriander", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Black Cumin (Nigella Seeds)", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Turmeric", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            # Serving ingredients (optional - skip as they're for presentation)
            # {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lettuce", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "shredded, or cooked grains and dark leafy greens (optional serving ingredient)"},
            # {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lime", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "for wedges"},
            # {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Cilantro", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "for sprigs"},
        ]
        
        create_recipe("Tempeh Satay with Spicy Peanut Sauce", False, 4, "serving", items, cursor)
        
        # Recipe 9: Tempeh and Mushroom Chili with Corn and Cilantro
        print("\n--- Recipe 9: Tempeh and Mushroom Chili with Corn and Cilantro ---")
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Tempeh", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": None, "preparation_notes": "8 oz / 230g package"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Bell Pepper", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "cored, seeded, and chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 0.25 cup / 60ml hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 3, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Cremini Mushrooms", cursor), "quantity": 8, "unit_id": ounce_unit_id, "size_qualifier": None, "preparation_notes": "225g, chopped"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chili Powder", cursor), "quantity": 2.5, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "2 to 3 tablespoons, mild or hot"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Oregano", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Black Cumin (Nigella Seeds)", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Crushed Tomatoes", cursor), "quantity": 2, "unit_id": can_unit_id, "size_qualifier": None, "preparation_notes": "2 cans (14.5 oz each / 800g total), drained"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Red Kidney Beans", cursor), "quantity": 3, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "810g, drained and rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Corn Kernels", cursor), "quantity": 1, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "160g, fresh or thawed frozen"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Cilantro", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "30g, chopped"},
        ]
        
        create_recipe("Tempeh and Mushroom Chili with Corn and Cilantro", False, 6, "serving", items, cursor)
        
        # Recipe 10: Two-Lentil Dal
        print("\n--- Recipe 10: Two-Lentil Dal ---")
        vegetable_broth_id, _ = get_sub_recipe_id("Vegetable Broth", cursor)
        
        items = [
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Green Lentils", cursor), "quantity": 0.75, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "145g, well rinsed"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Brown Lentils", cursor), "quantity": 0.75, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "130g, well rinsed"},
            {"item_type": "sub_recipe", "sub_recipe_id": vegetable_broth_id, "quantity": 4.25, "unit_id": cup_unit_id, "size_qualifier": None, "preparation_notes": "1L, or water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Red Onion", cursor), "quantity": 1, "unit_id": whole_unit_id, "size_qualifier": "medium", "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Garlic", cursor), "quantity": 2, "unit_id": clove_unit_id, "size_qualifier": None, "preparation_notes": "minced"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Ginger", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "grated"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("White Miso Paste", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": "blended with 2 tablespoons hot water"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Yellow Curry Powder", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Black Cumin (Nigella Seeds)", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Coriander", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": None},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Black Pepper", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "ground pippali or black pepper"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Salt-Free Crushed Tomatoes", cursor), "quantity": 1, "unit_id": can_unit_id, "size_qualifier": None, "preparation_notes": "14.5 oz / 400g"},
            {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Fenugreek Seeds", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "size_qualifier": None, "preparation_notes": "optional"},
        ]
        
        create_recipe("Two-Lentil Dal", False, 4, "serving", items, cursor)
        
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

