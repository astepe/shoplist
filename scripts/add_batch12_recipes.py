#!/usr/bin/env python3
"""
Script to create all Batch 12 recipes (7 main recipes).
Recipes: Blueberry Chia Pie, Molasses Spice Cookies, Better Pecan Squares,
         Mocha Chia Pudding, Cocoa-Almond Butter Cookies, Coffee Granita,
         Quinoa Pudding with Mango
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
        print("Creating Batch 12 Recipes")
        print("=" * 60)
        
        # Get unit IDs
        serving_unit_id = get_unit_id("serving", cursor)
        # Use "serving" for cookie and square yields (unit types don't include cookie/square)
        cup_unit_id = get_unit_id("cup", cursor)
        tablespoon_unit_id = get_unit_id("tablespoon", cursor)
        teaspoon_unit_id = get_unit_id("teaspoon", cursor)
        whole_unit_id = get_unit_id("whole", cursor)
        
        # Get sub-recipe IDs
        date_syrup_id, _ = get_sub_recipe_id("Date Syrup", cursor)
        
        # Recipe 1: Blueberry Chia Pie
        print("\n1. Blueberry Chia Pie")
        cursor.execute("SELECT id FROM recipes WHERE name = ?", ("Blueberry Chia Pie",))
        if cursor.fetchone():
            print("  ⚠ Already exists - skipping")
        else:
            cursor.execute("""
                INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
                VALUES (?, ?, ?, ?)
            """, ("Blueberry Chia Pie", False, 6, serving_unit_id))
            recipe_id = cursor.lastrowid
            print(f"  ✓ Created (ID: {recipe_id})")
            
            items = [
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pitted Dates", cursor), "quantity": 0.75, "unit_id": cup_unit_id, "preparation_notes": "190g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Walnuts", cursor), "quantity": 1.25, "unit_id": cup_unit_id, "preparation_notes": "150g, walnut pieces"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Blueberries", cursor), "quantity": 4, "unit_id": cup_unit_id, "preparation_notes": "600g, fresh or frozen (620g if frozen)"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Date Sugar", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "preparation_notes": "55g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chia Seeds", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Lemon", cursor), "quantity": 2, "unit_id": teaspoon_unit_id, "preparation_notes": "fresh lemon juice"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "preparation_notes": "80ml"},
            ]
            
            for item in items:
                cursor.execute("""
                    INSERT INTO recipe_items 
                    (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, item["item_type"], item.get("ingredient_id"), None, item["quantity"], item["unit_id"], None, item["preparation_notes"]))
            print(f"    ✓ Added {len(items)} items")
        
        # Recipe 2: Molasses Spice Cookies
        print("\n2. Molasses Spice Cookies")
        cursor.execute("SELECT id FROM recipes WHERE name = ?", ("Molasses Spice Cookies",))
        if cursor.fetchone():
            print("  ⚠ Already exists - skipping")
        else:
            cursor.execute("""
                INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
                VALUES (?, ?, ?, ?)
            """, ("Molasses Spice Cookies", False, 12, serving_unit_id))
            recipe_id = cursor.lastrowid
            print(f"  ✓ Created (ID: {recipe_id})")
            
            items = [
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Blackstrap Molasses", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "preparation_notes": "80ml, dark molasses"},
                {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 0.33, "unit_id": cup_unit_id, "preparation_notes": "80ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Butter", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor), "quantity": 0.5, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Flour", cursor), "quantity": 1, "unit_id": cup_unit_id, "preparation_notes": "110g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Oat Flour", cursor), "quantity": 1, "unit_id": cup_unit_id, "preparation_notes": "120g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Aluminum- and Sodium-Free Baking Powder", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Ginger", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Cinnamon", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Allspice", cursor), "quantity": 0.25, "unit_id": teaspoon_unit_id, "preparation_notes": None},
            ]
            
            for item in items:
                cursor.execute("""
                    INSERT INTO recipe_items 
                    (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, item["item_type"], item.get("ingredient_id"), item.get("sub_recipe_id"), item["quantity"], item["unit_id"], None, item["preparation_notes"]))
            print(f"    ✓ Added {len(items)} items")
        
        # Recipe 3: Better Pecan Squares
        print("\n3. Better Pecan Squares")
        cursor.execute("SELECT id FROM recipes WHERE name = ?", ("Better Pecan Squares",))
        if cursor.fetchone():
            print("  ⚠ Already exists - skipping")
        else:
            cursor.execute("""
                INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
                VALUES (?, ?, ?, ?)
            """, ("Better Pecan Squares", False, 9, serving_unit_id))
            recipe_id = cursor.lastrowid
            print(f"  ✓ Created (ID: {recipe_id})")
            
            items = [
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ripe Bananas", cursor), "quantity": 2, "unit_id": whole_unit_id, "preparation_notes": "very ripe, cut into chunks", "size_qualifier": "medium"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Butter", cursor), "quantity": 1, "unit_id": tablespoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Date Sugar", cursor), "quantity": 1.5, "unit_id": tablespoon_unit_id, "preparation_notes": "or Date Syrup 2.0"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 2, "unit_id": tablespoon_unit_id, "preparation_notes": "30ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Rolled Oats", cursor), "quantity": 2, "unit_id": cup_unit_id, "preparation_notes": "200g, old-fashioned rolled oats"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Aluminum- and Sodium-Free Baking Powder", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pecan Halves", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "preparation_notes": "35g, coarsely chopped pecans"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Dried Goji Berries", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pecan Halves", cursor), "quantity": 9, "unit_id": whole_unit_id, "preparation_notes": "optional, for topping"},
            ]
            
            for item in items:
                cursor.execute("""
                    INSERT INTO recipe_items 
                    (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, item["item_type"], item.get("ingredient_id"), None, item["quantity"], item["unit_id"], item.get("size_qualifier"), item["preparation_notes"]))
            print(f"    ✓ Added {len(items)} items")
        
        # Recipe 4: Mocha Chia Pudding
        print("\n4. Mocha Chia Pudding")
        cursor.execute("SELECT id FROM recipes WHERE name = ?", ("Mocha Chia Pudding",))
        if cursor.fetchone():
            print("  ⚠ Already exists - skipping")
        else:
            cursor.execute("""
                INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
                VALUES (?, ?, ?, ?)
            """, ("Mocha Chia Pudding", False, 4, serving_unit_id))
            recipe_id = cursor.lastrowid
            print(f"  ✓ Created (ID: {recipe_id})")
            
            items = [
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Unsweetened Cocoa Powder", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "preparation_notes": "20g"},
                {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 0.5, "unit_id": cup_unit_id, "preparation_notes": "120ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Unsweetened Soy Milk", cursor), "quantity": 0.75, "unit_id": cup_unit_id, "preparation_notes": "180ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Strong Brewed Coffee", cursor), "quantity": 0.75, "unit_id": cup_unit_id, "preparation_notes": "180ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Chia Seeds", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "preparation_notes": "80g"},
            ]
            
            for item in items:
                cursor.execute("""
                    INSERT INTO recipe_items 
                    (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, item["item_type"], item.get("ingredient_id"), item.get("sub_recipe_id"), item["quantity"], item["unit_id"], None, item["preparation_notes"]))
            print(f"    ✓ Added {len(items)} items")
        
        # Recipe 5: Cocoa-Almond Butter Cookies
        print("\n5. Cocoa-Almond Butter Cookies")
        cursor.execute("SELECT id FROM recipes WHERE name = ?", ("Cocoa-Almond Butter Cookies",))
        if cursor.fetchone():
            print("  ⚠ Already exists - skipping")
        else:
            cursor.execute("""
                INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
                VALUES (?, ?, ?, ?)
            """, ("Cocoa-Almond Butter Cookies", False, 12, serving_unit_id))
            recipe_id = cursor.lastrowid
            print(f"  ✓ Created (ID: {recipe_id})")
            
            items = [
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ripe Bananas", cursor), "quantity": 1, "unit_id": whole_unit_id, "preparation_notes": "very ripe, mashed well", "size_qualifier": "large"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Oat Flour", cursor), "quantity": 1, "unit_id": cup_unit_id, "preparation_notes": "120g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Flour", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "preparation_notes": "30g"},
                {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 0.25, "unit_id": cup_unit_id, "preparation_notes": "60ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Almond Butter", cursor), "quantity": 0.25, "unit_id": cup_unit_id, "preparation_notes": "75g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Unsweetened Cocoa Powder", cursor), "quantity": 3, "unit_id": tablespoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Walnuts", cursor), "quantity": 12, "unit_id": whole_unit_id, "preparation_notes": "walnut halves, optional"},
            ]
            
            for item in items:
                cursor.execute("""
                    INSERT INTO recipe_items 
                    (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, item["item_type"], item.get("ingredient_id"), item.get("sub_recipe_id"), item["quantity"], item["unit_id"], item.get("size_qualifier"), item["preparation_notes"]))
            print(f"    ✓ Added {len(items)} items")
        
        # Recipe 6: Coffee Granita
        print("\n6. Coffee Granita")
        cursor.execute("SELECT id FROM recipes WHERE name = ?", ("Coffee Granita",))
        if cursor.fetchone():
            print("  ⚠ Already exists - skipping")
        else:
            cursor.execute("""
                INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
                VALUES (?, ?, ?, ?)
            """, ("Coffee Granita", False, 4, serving_unit_id))
            recipe_id = cursor.lastrowid
            print(f"  ✓ Created (ID: {recipe_id})")
            
            items = [
                {"item_type": "sub_recipe", "sub_recipe_id": date_syrup_id, "quantity": 0.5, "unit_id": cup_unit_id, "preparation_notes": "120ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 0.33, "unit_id": cup_unit_id, "preparation_notes": "80ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Strong Brewed Coffee", cursor), "quantity": 2, "unit_id": cup_unit_id, "preparation_notes": "470ml, cooled"},
            ]
            
            for item in items:
                cursor.execute("""
                    INSERT INTO recipe_items 
                    (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, item["item_type"], item.get("ingredient_id"), item.get("sub_recipe_id"), item["quantity"], item["unit_id"], None, item["preparation_notes"]))
            print(f"    ✓ Added {len(items)} items")
        
        # Recipe 7: Quinoa Pudding with Mango
        print("\n7. Quinoa Pudding with Mango")
        cursor.execute("SELECT id FROM recipes WHERE name = ?", ("Quinoa Pudding with Mango",))
        if cursor.fetchone():
            print("  ⚠ Already exists - skipping")
        else:
            cursor.execute("""
                INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id)
                VALUES (?, ?, ?, ?)
            """, ("Quinoa Pudding with Mango", False, 6, serving_unit_id))
            recipe_id = cursor.lastrowid
            print(f"  ✓ Created (ID: {recipe_id})")
            
            items = [
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Quinoa", cursor), "quantity": 1, "unit_id": cup_unit_id, "preparation_notes": "180g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Unsweetened Soy Milk", cursor), "quantity": 3, "unit_id": cup_unit_id, "preparation_notes": "700ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Water", cursor), "quantity": 1, "unit_id": cup_unit_id, "preparation_notes": "235ml"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Date Sugar", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "preparation_notes": "110g"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Ground Cinnamon", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Pure Vanilla Extract", cursor), "quantity": 1, "unit_id": teaspoon_unit_id, "preparation_notes": None},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raw Almonds", cursor), "quantity": 0.5, "unit_id": cup_unit_id, "preparation_notes": "40g, slivered or sliced almonds"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Mango", cursor), "quantity": 1, "unit_id": whole_unit_id, "preparation_notes": "ripe, peeled, pitted, and chopped"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Raspberries", cursor), "quantity": 6, "unit_id": whole_unit_id, "preparation_notes": "for garnish, optional"},
                {"item_type": "ingredient", "ingredient_id": get_ingredient_id("Fresh Mint Leaves", cursor), "quantity": 6, "unit_id": whole_unit_id, "preparation_notes": "for garnish, optional"},
            ]
            
            for item in items:
                cursor.execute("""
                    INSERT INTO recipe_items 
                    (recipe_id, item_type, ingredient_id, sub_recipe_id, quantity, unit_id, size_qualifier, preparation_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (recipe_id, item["item_type"], item.get("ingredient_id"), None, item["quantity"], item["unit_id"], None, item["preparation_notes"]))
            print(f"    ✓ Added {len(items)} items")
        
        db.commit()
        print("\n" + "=" * 60)
        print("✓ All Batch 12 recipes created successfully!")
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

