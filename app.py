"""
Flask application entry point.
"""
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from backend.database import init_db, get_db
from backend.services import convert_to_shopping_unit, estimate_size_qualifier, check_circular_reference, generate_shopping_list, organize_shopping_list_by_sections, format_shopping_list_text
from backend.default_conversions import apply_default_conversions, get_available_default_ingredients
import json
from pathlib import Path

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Initialize database on startup
init_db()

# Serve frontend files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory."""
    # Don't serve files that start with 'api/' - those are API routes
    if filename.startswith('api/'):
        from flask import abort
        abort(404)
    
    # Serve HTML files
    if filename.endswith('.html'):
        return send_from_directory('frontend', filename)
    
    # Serve manifest.json with correct content type
    if filename == 'manifest.json':
        return send_from_directory('frontend', filename, mimetype='application/manifest+json')
    
    # Serve service worker with correct content type
    if filename == 'service-worker.js':
        return send_from_directory('frontend', filename, mimetype='application/javascript')
    
    # Serve other static files (CSS, JS, etc.)
    return send_from_directory('frontend', filename)

# API Routes
@app.route('/api/ingredient-types', methods=['GET'])
def get_ingredient_types():
    """Get all ingredient types."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM ingredient_types ORDER BY name")
    types = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(types)

@app.route('/api/unit-types', methods=['GET'])
def get_unit_types():
    """Get all unit types."""
    category = request.args.get('category')
    db = get_db()
    cursor = db.cursor()
    
    if category:
        cursor.execute("SELECT id, name, category FROM unit_types WHERE category = ? ORDER BY name", (category,))
    else:
        cursor.execute("SELECT id, name, category FROM unit_types ORDER BY name")
    
    units = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(units)

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Get all ingredients, optionally filtered by type."""
    type_id = request.args.get('type_id')
    db = get_db()
    cursor = db.cursor()
    
    if type_id:
        cursor.execute("""
            SELECT i.id, i.name, i.type_id, i.shopping_unit_id,
                   it.name as type_name, ut.name as shopping_unit_name
            FROM ingredients i
            JOIN ingredient_types it ON i.type_id = it.id
            JOIN unit_types ut ON i.shopping_unit_id = ut.id
            WHERE i.type_id = ?
            ORDER BY i.name
        """, (type_id,))
    else:
        cursor.execute("""
            SELECT i.id, i.name, i.type_id, i.shopping_unit_id,
                   it.name as type_name, ut.name as shopping_unit_name
            FROM ingredients i
            JOIN ingredient_types it ON i.type_id = it.id
            JOIN unit_types ut ON i.shopping_unit_id = ut.id
            ORDER BY i.name
        """)
    
    ingredients = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(ingredients)

@app.route('/api/ingredients', methods=['POST'])
def create_ingredient():
    """Create a new ingredient."""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if user provided conversion rules or wants to use defaults
        provided_rules = data.get('conversion_rules', [])
        use_defaults = data.get('use_default_conversions', False)
        
        # If no rules provided and defaults available, apply them
        if len(provided_rules) == 0 and use_defaults:
            default_conversions, default_sizes = apply_default_conversions(
                data['name'],
                data['shopping_unit_id'],
                db
            )
            if default_conversions:
                provided_rules = default_conversions
                data['size_estimation_rules'] = default_sizes
                # Update shopping unit to match default if not specified
                # (Defaults will match the user's selection, so this is fine)
        
        if len(provided_rules) == 0:
            return jsonify({'error': 'No conversion rules provided. Add rules manually or enable default conversions.'}), 400
        
        cursor.execute("""
            INSERT INTO ingredients (name, type_id, shopping_unit_id)
            VALUES (?, ?, ?)
        """, (data['name'], data['type_id'], data['shopping_unit_id']))
        
        ingredient_id = cursor.lastrowid
        
        # Add conversion rules
        for rule in provided_rules:
            cursor.execute("""
                INSERT INTO conversion_rules (ingredient_id, from_unit_id, to_unit_id, conversion_factor)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, rule['from_unit_id'], rule['to_unit_id'], rule['conversion_factor']))
        
        # Add size estimation rules if provided
        for size_rule in data.get('size_estimation_rules', []):
            cursor.execute("""
                INSERT INTO size_estimation_rules (ingredient_id, size_qualifier, reference_unit_id, reference_value)
                VALUES (?, ?, ?, ?)
            """, (ingredient_id, size_rule['size_qualifier'], size_rule['reference_unit_id'], size_rule['reference_value']))
        
        db.commit()
        db.close()
        return jsonify({'id': ingredient_id}), 201
    
    except Exception as e:
        db.rollback()
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/default-ingredients', methods=['GET'])
def get_default_ingredients():
    """Get list of ingredients with default conversion rules available."""
    return jsonify(get_available_default_ingredients())

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes, optionally filtered by ingredients."""
    # Check for ingredient search parameter
    ingredient_query = request.args.get('ingredients', '').strip()
    
    db = get_db()
    cursor = db.cursor()
    
    if ingredient_query:
        # Search recipes by ingredient names
        # Split by comma or space to allow multiple ingredients
        ingredient_terms = [term.strip().lower() for term in ingredient_query.replace(',', ' ').split() if term.strip()]
        
        if not ingredient_terms:
            # Empty search, return all recipes
            cursor.execute("""
                SELECT r.id, r.name, r.is_sub_recipe, r.yield_quantity, r.yield_unit_id, r.page_number,
                       ut.name as yield_unit_name
                FROM recipes r
                JOIN unit_types ut ON r.yield_unit_id = ut.id
                ORDER BY r.name
            """)
        else:
            # Build query to find recipes containing any of the ingredient terms
            # Use LIKE for partial matching (case-insensitive via LOWER)
            # SQLite doesn't support LIKE ANY, so we use OR conditions
            like_patterns = [f'%{term}%' for term in ingredient_terms]
            
            # Build WHERE clause with OR conditions for each term
            ingredient_conditions = []
            sub_recipe_conditions = []
            all_params = []
            
            for pattern in like_patterns:
                ingredient_conditions.append("(ri.item_type = 'ingredient' AND LOWER(i.name) LIKE ?)")
                sub_recipe_conditions.append("(ri.item_type = 'sub_recipe' AND LOWER(sr.name) LIKE ?)")
                all_params.extend([pattern, pattern])
            
            where_clause = "(" + " OR ".join(ingredient_conditions) + ") OR (" + " OR ".join(sub_recipe_conditions) + ")"
            
            query = f"""
                SELECT DISTINCT r.id, r.name, r.is_sub_recipe, r.yield_quantity, r.yield_unit_id, r.page_number,
                       ut.name as yield_unit_name
                FROM recipes r
                JOIN unit_types ut ON r.yield_unit_id = ut.id
                JOIN recipe_items ri ON r.id = ri.recipe_id
                LEFT JOIN ingredients i ON ri.ingredient_id = i.id
                LEFT JOIN recipes sr ON ri.sub_recipe_id = sr.id
                WHERE {where_clause}
                ORDER BY r.name
            """
            
            cursor.execute(query, all_params)
    else:
        # No ingredient filter, return all recipes
        cursor.execute("""
            SELECT r.id, r.name, r.is_sub_recipe, r.yield_quantity, r.yield_unit_id, r.page_number,
                   ut.name as yield_unit_name
            FROM recipes r
            JOIN unit_types ut ON r.yield_unit_id = ut.id
            ORDER BY r.name
        """)
    
    recipes = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(recipes)

@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a single recipe with its items."""
    db = get_db()
    cursor = db.cursor()
    
    # Get recipe
    cursor.execute("""
        SELECT r.id, r.name, r.is_sub_recipe, r.yield_quantity, r.yield_unit_id,
               ut.name as yield_unit_name
        FROM recipes r
        JOIN unit_types ut ON r.yield_unit_id = ut.id
        WHERE r.id = ?
    """, (recipe_id,))
    
    recipe = cursor.fetchone()
    if not recipe:
        db.close()
        return jsonify({'error': 'Recipe not found'}), 404
    
    # Get recipe items with names and unit names
    cursor.execute("""
        SELECT ri.item_type, ri.ingredient_id, ri.sub_recipe_id, ri.quantity, ri.unit_id,
               ri.size_qualifier, ri.preparation_notes,
               i.name as ingredient_name,
               r.name as sub_recipe_name,
               ut.name as unit_name,
               r2.yield_quantity as sub_recipe_yield_quantity,
               ut2.name as sub_recipe_yield_unit_name
        FROM recipe_items ri
        LEFT JOIN ingredients i ON ri.ingredient_id = i.id
        LEFT JOIN recipes r ON ri.sub_recipe_id = r.id
        LEFT JOIN unit_types ut ON ri.unit_id = ut.id
        LEFT JOIN recipes r2 ON ri.sub_recipe_id = r2.id
        LEFT JOIN unit_types ut2 ON r2.yield_unit_id = ut2.id
        WHERE ri.recipe_id = ?
        ORDER BY ri.id
    """, (recipe_id,))
    
    items = []
    for item in cursor.fetchall():
        item_data = {
            'item_type': item['item_type'],
            'ingredient_id': item['ingredient_id'],
            'sub_recipe_id': item['sub_recipe_id'],
            'quantity': item['quantity'],
            'unit_id': item['unit_id'],
            'unit_name': item['unit_name'] if item['unit_name'] else '',
            'size_qualifier': item['size_qualifier'],
            'preparation_notes': item['preparation_notes']
        }
        
        # Add name based on item type
        if item['item_type'] == 'ingredient':
            item_data['ingredient_name'] = item['ingredient_name'] if item['ingredient_name'] else ''
        else:
            item_data['sub_recipe_name'] = item['sub_recipe_name'] if item['sub_recipe_name'] else ''
            item_data['sub_recipe_yield_quantity'] = item['sub_recipe_yield_quantity'] if item['sub_recipe_yield_quantity'] else None
            item_data['sub_recipe_yield_unit_name'] = item['sub_recipe_yield_unit_name'] if item['sub_recipe_yield_unit_name'] else ''
        
        items.append(item_data)
    
    recipe_data = dict(recipe)
    recipe_data['items'] = items
    
    db.close()
    return jsonify(recipe_data)

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """Create a new recipe."""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Validate sub-recipe yield unit (must be standard unit, not "servings")
        if data.get('is_sub_recipe'):
            cursor.execute("SELECT category FROM unit_types WHERE id = ?", (data['yield_unit_id'],))
            unit = cursor.fetchone()
            if unit and unit['category'] == 'special':
                return jsonify({'error': 'Sub-recipes cannot have "servings" as yield unit'}), 400
        
        cursor.execute("""
            INSERT INTO recipes (name, is_sub_recipe, yield_quantity, yield_unit_id, page_number)
            VALUES (?, ?, ?, ?, ?)
        """, (data['name'], int(data['is_sub_recipe']), data['yield_quantity'], data['yield_unit_id'], data.get('page_number')))
        
        recipe_id = cursor.lastrowid
        
        # Add recipe items
        for item in data.get('items', []):
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
        db.close()
        return jsonify({'id': recipe_id}), 201
    
    except Exception as e:
        db.rollback()
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    """Update an existing recipe."""
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if recipe exists
        cursor.execute("SELECT is_sub_recipe FROM recipes WHERE id = ?", (recipe_id,))
        existing = cursor.fetchone()
        if not existing:
            db.close()
            return jsonify({'error': 'Recipe not found'}), 404
        
        # is_sub_recipe is immutable - use existing value
        is_sub_recipe = existing['is_sub_recipe']
        
        # Validate yield unit if this is a sub-recipe
        if is_sub_recipe:
            cursor.execute("SELECT category FROM unit_types WHERE id = ?", (data['yield_unit_id'],))
            unit = cursor.fetchone()
            if unit and unit['category'] == 'special':
                return jsonify({'error': 'Sub-recipes cannot have "servings" as yield unit'}), 400
        
        # Update recipe
        cursor.execute("""
            UPDATE recipes 
            SET name = ?, yield_quantity = ?, yield_unit_id = ?, page_number = ?
            WHERE id = ?
        """, (data['name'], data['yield_quantity'], data['yield_unit_id'], data.get('page_number'), recipe_id))
        
        # Delete existing items
        cursor.execute("DELETE FROM recipe_items WHERE recipe_id = ?", (recipe_id,))
        
        # Add new items
        for item in data.get('items', []):
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
        db.close()
        return jsonify({'id': recipe_id}), 200
    
    except Exception as e:
        db.rollback()
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    """Delete a recipe."""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if recipe exists
        cursor.execute("SELECT id, name, is_sub_recipe FROM recipes WHERE id = ?", (recipe_id,))
        recipe = cursor.fetchone()
        if not recipe:
            db.close()
            return jsonify({'error': 'Recipe not found'}), 404
        
        # If this is a sub-recipe, check which recipes reference it
        referencing_recipes = []
        if recipe['is_sub_recipe']:
            cursor.execute("""
                SELECT DISTINCT r.id, r.name
                FROM recipes r
                JOIN recipe_items ri ON r.id = ri.recipe_id
                WHERE ri.item_type = 'sub_recipe' AND ri.sub_recipe_id = ?
            """, (recipe_id,))
            referencing_recipes = [dict(row) for row in cursor.fetchall()]
        
        # Delete the recipe (CASCADE DELETE will remove recipe_items that reference it as sub-recipe)
        cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        
        db.commit()
        db.close()
        
        # Return info about what was deleted
        return jsonify({
            'id': recipe_id,
            'name': recipe['name'],
            'was_sub_recipe': bool(recipe['is_sub_recipe']),
            'referencing_recipes': referencing_recipes
        }), 200
    
    except Exception as e:
        db.rollback()
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/shopping-lists', methods=['POST'])
def generate_shopping_list_endpoint():
    """Generate a shopping list from selected recipes."""
    data = request.json
    recipe_selections = data.get('recipe_selections', [])
    
    try:
        # Generate shopping list
        shopping_list = generate_shopping_list(recipe_selections)
        
        # Store in history
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO shopping_lists (recipe_selections, shopping_list_data)
            VALUES (?, ?)
        """, (json.dumps(recipe_selections), json.dumps(shopping_list)))
        db.commit()
        db.close()
        
        # Return id with shopping list for auditing references
        return jsonify({
            'id': cursor.lastrowid,
            'shopping_list': shopping_list
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/shopping-lists', methods=['GET'])
def list_shopping_list_snapshots():
    """List saved shopping list snapshots (audit history)."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, created_at
        FROM shopping_lists
        ORDER BY id DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(rows)

@app.route('/api/shopping-lists/<int:snapshot_id>', methods=['GET'])
def get_shopping_list_snapshot(snapshot_id):
    """Get a specific shopping list snapshot with recipe selections and data."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, created_at, recipe_selections, shopping_list_data
        FROM shopping_lists
        WHERE id = ?
    """, (snapshot_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'Snapshot not found'}), 404
    return jsonify({
        'id': row['id'],
        'created_at': row['created_at'],
        'recipe_selections': json.loads(row['recipe_selections']),
        'shopping_list': json.loads(row['shopping_list_data'])
    })

@app.route('/api/shopping-list/formatted-text', methods=['POST'])
def get_formatted_shopping_list_text():
    """Get formatted shopping list text for copying."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    recipe_selections = data.get('recipe_selections', [])
    checked_item_ids = data.get('checked_item_ids', [])
    
    if not recipe_selections:
        return jsonify({'error': 'No recipe selections provided'}), 400
    
    # Generate shopping list
    db = get_db()
    try:
        shopping_list = generate_shopping_list(recipe_selections, db)
        
        # Organize by sections
        organized_list = organize_shopping_list_by_sections(shopping_list, db)
        
        # Build recipes info list (name + page number) for the footer
        recipes_info = []
        if recipe_selections:
            cursor = db.cursor()
            ids = [sel.get('recipe_id') for sel in recipe_selections if sel.get('recipe_id')]
            if ids:
                placeholders = ','.join(['?'] * len(ids))
                cursor.execute(f"SELECT id, name, page_number FROM recipes WHERE id IN ({placeholders})", ids)
                for row in cursor.fetchall():
                    recipes_info.append({'id': row['id'], 'name': row['name'], 'page_number': row['page_number']})

        # Format as text with checked items separated
        formatted_text = format_shopping_list_text(organized_list, recipes_info, checked_item_ids, shopping_list)
        
        return jsonify({'formatted_text': formatted_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    # Run on 0.0.0.0 to allow access from iPad on same network
    # Change to '127.0.0.1' if you only want local access
    app.run(debug=True, host='0.0.0.0', port=5000)

