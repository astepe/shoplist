/**
 * API client for ShopList backend
 */

const API_BASE = '';

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };
    
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }
    
    try {
        const response = await fetch(url, config);
        
        // Check if response is ok before parsing JSON
        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // If JSON parsing fails, use status text
                errorMessage = response.statusText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        // Parse JSON response
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Ingredient Types
async function getIngredientTypes() {
    return apiRequest('/api/ingredient-types');
}

// Unit Types
async function getUnitTypes(category = null) {
    const url = category ? `/api/unit-types?category=${category}` : '/api/unit-types';
    return apiRequest(url);
}

// Ingredients
async function getIngredients(typeId = null) {
    const url = typeId ? `/api/ingredients?type_id=${typeId}` : '/api/ingredients';
    return apiRequest(url);
}

async function createIngredient(ingredient) {
    return apiRequest('/api/ingredients', {
        method: 'POST',
        body: ingredient,
    });
}

// Recipes
async function getRecipes() {
    return apiRequest('/api/recipes');
}

async function getRecipe(recipeId) {
    return apiRequest(`/api/recipes/${recipeId}`);
}

async function createRecipe(recipe) {
    return apiRequest('/api/recipes', {
        method: 'POST',
        body: recipe,
    });
}

async function updateRecipe(recipeId, recipe) {
    return apiRequest(`/api/recipes/${recipeId}`, {
        method: 'PUT',
        body: recipe,
    });
}

async function deleteRecipeAPI(recipeId) {
    return apiRequest(`/api/recipes/${recipeId}`, {
        method: 'DELETE',
    });
}

// Shopping Lists
async function generateShoppingListAPI(recipeSelections) {
    const res = await apiRequest('/api/shopping-lists', {
        method: 'POST',
        body: { recipe_selections: recipeSelections },
    });
    // Backend may return { id, shopping_list } – unwrap for callers expecting an array
    if (Array.isArray(res)) return res;
    if (res && Array.isArray(res.shopping_list)) return res.shopping_list;
    return res;
}

async function getFormattedShoppingListText(recipeSelections, checkedItemIds = []) {
    return apiRequest('/api/shopping-list/formatted-text', {
        method: 'POST',
        body: {
            recipe_selections: recipeSelections,
            checked_item_ids: checkedItemIds
        },
    });
}


// Default Ingredients
async function getDefaultIngredients() {
    return apiRequest('/api/default-ingredients');
}

// Shopping list snapshots (audit history)
async function getShoppingListSnapshots() {
    return apiRequest('/api/shopping-lists');
}

async function getShoppingListSnapshot(snapshotId) {
    return apiRequest(`/api/shopping-lists/${snapshotId}`);
}

