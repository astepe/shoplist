/**
 * Recipe Management Page Logic
 */

let recipes = [];
let ingredients = [];
let unitTypes = [];
let subRecipes = [];
let currentRecipe = null;
let recipeItems = [];
let isEditing = false;

// Initialize page
async function initRecipesPage() {
    try {
        console.log('Initializing recipes page...');
        
        // Load data
        console.log('Loading recipes...');
        recipes = await getRecipes();
        console.log(`Loaded ${recipes.length} recipes`);
        
        console.log('Loading ingredients...');
        ingredients = await getIngredients();
        console.log(`Loaded ${ingredients.length} ingredients`);
        
        console.log('Loading unit types...');
        unitTypes = await getUnitTypes();
        console.log(`Loaded ${unitTypes.length} unit types`);
        
        // Filter sub-recipes
        subRecipes = recipes.filter(r => r.is_sub_recipe);
        console.log(`Found ${subRecipes.length} sub-recipes`);
        
        // Populate unit types for yield
        populateYieldUnits();
        populateQuickYieldUnits();
        
        // Populate ingredient and sub-recipe selectors
        populateIngredientSelector();
        populateSubRecipeSelector();
        populateUnitSelector();
        
        // Display recipes
        displayRecipes();
        
        // Setup search functionality
        setupSearch();
        
        // Setup form handlers
        setupFormHandlers();
        
        // Setup quick add handler
        setupQuickAdd();
        
        console.log('Recipes page initialized successfully');
        
    } catch (error) {
        console.error('Error initializing recipes page:', error);
        showError('Failed to load data: ' + error.message);
    }
}

function setupSearch() {
    const searchInput = document.getElementById('recipe-search');
    if (searchInput) {
        // Add event listener for real-time search
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            filterRecipes(query);
        });
    }
    
    // Setup ingredient search
    const ingredientSearchInput = document.getElementById('ingredient-search');
    if (ingredientSearchInput) {
        ingredientSearchInput.addEventListener('input', function() {
            searchByIngredients();
        });
    }
}

function filterRecipes(query = '') {
    const searchInput = document.getElementById('recipe-search');
    const ingredientSearchInput = document.getElementById('ingredient-search');
    
    if (!searchInput && query === '') {
        // If called without query and search input doesn't exist, use empty string
        query = '';
    } else if (!query && searchInput) {
        // Get query from input if not provided
        query = searchInput.value.trim();
    }
    
    // If ingredient search is active, use that instead
    const ingredientQuery = ingredientSearchInput?.value.trim() || '';
    if (ingredientQuery) {
        searchByIngredients();
        return;
    }
    
    // Otherwise, just filter by name
    displayRecipes(query);
}

// Make filterRecipes available globally for inline event handlers
window.filterRecipes = filterRecipes;

async function searchByIngredients() {
    const ingredientSearchInput = document.getElementById('ingredient-search');
    if (!ingredientSearchInput) return;
    
    const ingredientQuery = ingredientSearchInput.value.trim();
    const nameQuery = document.getElementById('recipe-search')?.value.trim() || '';
    
    try {
        // If ingredient search is empty, just use name filter on all recipes
        if (!ingredientQuery) {
            filterRecipes(nameQuery);
            return;
        }
        
        // Build URL with ingredient parameter
        let url = '/api/recipes';
        const params = new URLSearchParams();
        if (ingredientQuery) {
            params.append('ingredients', ingredientQuery);
        }
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        // Fetch recipes filtered by ingredients
        const filteredRecipes = await apiRequest(url);
        
        // Also filter by name if name search is active
        let finalRecipes = filteredRecipes;
        if (nameQuery) {
            finalRecipes = filteredRecipes.filter(recipe => 
                recipe.name.toLowerCase().includes(nameQuery.toLowerCase())
            );
        }
        
        // Display the filtered recipes
        const container = document.getElementById('recipes-list');
        if (!container) return;
        
        if (finalRecipes.length === 0) {
            container.innerHTML = `<p>No recipes found with ingredients matching "${ingredientQuery}"${nameQuery ? ` and name matching "${nameQuery}"` : ''}.</p>`;
            return;
        }
        
        // Temporarily replace recipes array for display
        const originalRecipes = recipes;
        recipes = finalRecipes;
        displayRecipes('');
        recipes = originalRecipes; // Restore original
        
    } catch (error) {
        console.error('Error searching by ingredients:', error);
        showError('Failed to search recipes: ' + error.message);
    }
}

// Make searchByIngredients available globally
window.searchByIngredients = searchByIngredients;

function populateYieldUnits() {
    const yieldUnitSelect = document.getElementById('yield-unit-select');
    if (!yieldUnitSelect) return;
    
    yieldUnitSelect.innerHTML = '<option value="">Select unit...</option>';
    unitTypes.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.id;
        option.textContent = `${unit.name} (${unit.category})`;
        yieldUnitSelect.appendChild(option);
    });
}

function populateQuickYieldUnits() {
    const quickYieldUnit = document.getElementById('quick-yield-unit');
    if (!quickYieldUnit) return;
    
    // Default to "serving" for quick add
    quickYieldUnit.innerHTML = '<option value="">servings</option>';
    unitTypes.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.id;
        option.textContent = unit.name;
        // Pre-select "serving" if available
        if (unit.name === 'serving') {
            option.selected = true;
        }
        quickYieldUnit.appendChild(option);
    });
}

function populateIngredientSelector() {
    const select = document.getElementById('ingredient-select');
    if (!select) return;
    
    // Group by type
    const grouped = {};
    ingredients.forEach(ing => {
        const typeName = ing.type_name || 'Unknown';
        if (!grouped[typeName]) {
            grouped[typeName] = [];
        }
        grouped[typeName].push(ing);
    });
    
    select.innerHTML = '<option value="">Select ingredient...</option>';
    Object.keys(grouped).sort().forEach(typeName => {
        const optgroup = document.createElement('optgroup');
        optgroup.label = typeName;
        grouped[typeName].forEach(ing => {
            const option = document.createElement('option');
            option.value = ing.id;
            option.textContent = ing.name;
            optgroup.appendChild(option);
        });
        select.appendChild(optgroup);
    });
}

function populateSubRecipeSelector() {
    const select = document.getElementById('sub-recipe-select');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select sub-recipe...</option>';
    subRecipes.forEach(recipe => {
        const option = document.createElement('option');
        option.value = recipe.id;
        option.textContent = `${recipe.name} (makes ${recipe.yield_quantity} ${recipe.yield_unit_name})`;
        select.appendChild(option);
    });
}

function populateUnitSelector() {
    const select = document.getElementById('item-unit-select');
    if (!select) return;
    
    // Include volume, weight, and count units (not special)
    const recipeUnits = unitTypes.filter(u => u.category !== 'special');
    
    select.innerHTML = '<option value="">Select unit...</option>';
    recipeUnits.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.id;
        option.textContent = `${unit.name} (${unit.category})`;
        select.appendChild(option);
    });
}

function displayRecipes(searchQuery = '') {
    const container = document.getElementById('recipes-list');
    if (!container) return;
    
    // Filter recipes by search query
    const filteredRecipes = searchQuery.trim() === '' 
        ? recipes 
        : recipes.filter(recipe => 
            recipe.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
    
    if (filteredRecipes.length === 0 && recipes.length > 0) {
        container.innerHTML = `<p>No recipes found matching "${searchQuery}".</p>`;
        return;
    }
    
    if (recipes.length === 0) {
        container.innerHTML = '<p>No recipes yet. Add your first recipe below.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    filteredRecipes.forEach(recipe => {
        const recipeDiv = document.createElement('div');
        recipeDiv.className = 'recipe-item';
        recipeDiv.setAttribute('data-recipe-id', recipe.id);
        
        const subRecipeBadge = recipe.is_sub_recipe ? '<span class="badge">Sub-Recipe</span>' : '';
        const expandIcon = '<span class="expand-icon">▶</span>';
        
        recipeDiv.innerHTML = `
            <div class="recipe-header">
                <div class="recipe-header-content clickable" onclick="toggleRecipeDetails(${recipe.id}, event)">
                    ${expandIcon}
                    <h3>${recipe.name}${subRecipeBadge}</h3>
                    <span class="recipe-yield">Makes: ${recipe.yield_quantity} ${recipe.yield_unit_name}</span>
                </div>
                <div class="recipe-actions">
                    <button class="btn-small" onclick="event.stopPropagation(); editRecipe(${recipe.id})">Edit</button>
                    <button class="btn-small btn-danger" onclick="event.stopPropagation(); deleteRecipe(${recipe.id})">Delete</button>
                </div>
            </div>
            <div class="recipe-details" id="recipe-details-${recipe.id}" style="display: none;">
                <div class="recipe-items-loading">Loading ingredients...</div>
            </div>
        `;
        
        container.appendChild(recipeDiv);
    });
}

async function toggleRecipeDetails(recipeId, event) {
    // Prevent event from bubbling to parent
    if (event) {
        event.stopPropagation();
    }
    
    const detailsDiv = document.getElementById(`recipe-details-${recipeId}`);
    if (!detailsDiv) {
        console.error(`Recipe details div not found for recipe ${recipeId}`);
        return;
    }
    
    const recipeDiv = detailsDiv.closest('.recipe-item');
    if (!recipeDiv) {
        console.error(`Recipe item div not found for recipe ${recipeId}`);
        return;
    }
    
    const expandIcon = recipeDiv.querySelector('.expand-icon');
    if (!expandIcon) {
        console.error(`Expand icon not found for recipe ${recipeId}`);
        return;
    }
    
    // Check if currently hidden (check both style.display and computed style)
    const isHidden = detailsDiv.style.display === 'none' || 
                    window.getComputedStyle(detailsDiv).display === 'none';
    
    if (isHidden) {
        // Expand - load recipe details
        detailsDiv.style.display = 'block';
        expandIcon.textContent = '▼';
        
        // Check if already loaded (check for items list, not loading div)
        const itemsList = detailsDiv.querySelector('.recipe-items-list');
        if (!itemsList) {
            // Not loaded yet - show loading and fetch
            detailsDiv.innerHTML = '<div class="recipe-items-loading">Loading ingredients...</div>';
            try {
                console.log(`Loading recipe ${recipeId}...`);
                const recipe = await getRecipe(recipeId);
                console.log(`Recipe loaded:`, recipe);
                console.log(`Recipe has items:`, !!recipe?.items);
                console.log(`Items array length:`, recipe?.items?.length);
                if (recipe && recipe.items) {
                    console.log(`Calling displayRecipeItems with ${recipe.items.length} items`);
                    console.log(`Items:`, recipe.items);
                    try {
                        displayRecipeItems(recipeId, recipe.items);
                        console.log(`displayRecipeItems call completed`);
                    } catch (err) {
                        console.error(`Error in displayRecipeItems:`, err);
                        console.error(`Error stack:`, err.stack);
                        detailsDiv.innerHTML = `<div class="error">Error displaying items: ${err.message}</div>`;
                    }
                } else {
                    console.log(`No items found, showing empty message`);
                    detailsDiv.innerHTML = '<div class="recipe-items-empty">No ingredients found.</div>';
                }
            } catch (error) {
                console.error('Error loading recipe details:', error);
                console.error('Error stack:', error.stack);
                detailsDiv.innerHTML = `<div class="error">Failed to load recipe ingredients: ${error.message}</div>`;
            }
        }
    } else {
        // Collapse
        detailsDiv.style.display = 'none';
        expandIcon.textContent = '▶';
    }
}

function displayRecipeItems(recipeId, items) {
    try {
        console.log(`displayRecipeItems called for recipe ${recipeId} with ${items ? items.length : 0} items`);
        console.log(`Items data:`, items);
        
        const detailsDiv = document.getElementById(`recipe-details-${recipeId}`);
        if (!detailsDiv) {
            console.error(`Recipe details div not found for recipe ${recipeId}`);
            return;
        }
        console.log(`Found detailsDiv for recipe ${recipeId}`);
        
        if (!items || items.length === 0) {
            console.log(`No items to display for recipe ${recipeId}`);
            detailsDiv.innerHTML = '<div class="recipe-items-empty">No ingredients yet.</div>';
            return;
        }
        
        console.log(`Rendering ${items.length} items for recipe ${recipeId}`);
        let html = '<div class="recipe-items-list"><ul>';
        
        items.forEach((item, index) => {
        const sizeStr = item.size_qualifier ? ` ${item.size_qualifier}` : '';
        const prepStr = item.preparation_notes ? `, ${item.preparation_notes}` : '';
        
        if (item.item_type === 'sub_recipe') {
            const yieldStr = item.sub_recipe_yield_quantity 
                ? ` (yields ${item.sub_recipe_yield_quantity} ${item.sub_recipe_yield_unit_name})`
                : '';
            html += `
                <li class="recipe-item-line">
                    <span class="item-quantity">${formatQuantity(item.quantity)}</span>
                    <span class="item-unit">${item.unit_name || ''}</span>
                    <span class="item-name sub-recipe">${item.sub_recipe_name || 'Unknown'}</span>
                    <span class="item-yield">${yieldStr}</span>
                    ${prepStr ? `<span class="item-prep">${prepStr}</span>` : ''}
                </li>
            `;
        } else {
            html += `
                <li class="recipe-item-line">
                    <span class="item-quantity">${formatQuantity(item.quantity)}</span>
                    <span class="item-unit">${item.unit_name || ''}</span>
                    ${sizeStr ? `<span class="item-size">${sizeStr}</span>` : ''}
                    <span class="item-name">${item.ingredient_name || 'Unknown'}</span>
                    ${prepStr ? `<span class="item-prep">${prepStr}</span>` : ''}
                </li>
            `;
            }
        });
        
        html += '</ul></div>';
        console.log(`Setting innerHTML for recipe ${recipeId}, HTML length: ${html.length}`);
        console.log(`detailsDiv exists:`, !!detailsDiv);
        console.log(`detailsDiv.style.display before:`, detailsDiv.style.display);
        console.log(`detailsDiv computed display before:`, window.getComputedStyle(detailsDiv).display);
        
        // Ensure div is visible before setting HTML
        detailsDiv.style.display = 'block';
        detailsDiv.innerHTML = html;
        
        // Force a reflow to ensure rendering
        detailsDiv.offsetHeight;
        
        console.log(`HTML set, detailsDiv.innerHTML length: ${detailsDiv.innerHTML.length}`);
        console.log(`detailsDiv.style.display after:`, detailsDiv.style.display);
        console.log(`detailsDiv computed display after:`, window.getComputedStyle(detailsDiv).display);
        console.log(`detailsDiv has .recipe-items-list:`, !!detailsDiv.querySelector('.recipe-items-list'));
        console.log(`detailsDiv has <ul>:`, !!detailsDiv.querySelector('ul'));
        const listItems = detailsDiv.querySelectorAll('li');
        console.log(`Number of <li> elements:`, listItems.length);
        if (listItems.length > 0) {
            console.log(`First <li> content:`, listItems[0].textContent);
            console.log(`First <li> computed display:`, window.getComputedStyle(listItems[0]).display);
        }
    } catch (err) {
        console.error(`Error in displayRecipeItems:`, err);
        console.error(`Error stack:`, err.stack);
        throw err; // Re-throw to be caught by caller
    }
}

function formatQuantity(quantity) {
    // Format quantity to remove unnecessary decimals
    if (quantity % 1 === 0) {
        return quantity.toString();
    }
    // Round to 2 decimal places for fractional quantities
    return parseFloat(quantity).toFixed(2).replace(/\.?0+$/, '');
}

function setupFormHandlers() {
    const form = document.getElementById('recipe-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveRecipe();
    });
    
    // Handle sub-recipe checkbox
    const isSubRecipeCheck = document.getElementById('is-sub-recipe');
    if (isSubRecipeCheck) {
        isSubRecipeCheck.addEventListener('change', handleSubRecipeToggle);
    }
    
    // Setup item handlers
    setupItemHandlers();
}

function handleSubRecipeToggle(e) {
    const isSubRecipe = e.target.checked;
    const yieldUnitSelect = document.getElementById('yield-unit-select');
    
    if (!yieldUnitSelect) return;
    
    // If sub-recipe, filter out "servings" from yield units
    if (isSubRecipe) {
        const options = yieldUnitSelect.querySelectorAll('option');
        options.forEach(option => {
            if (option.textContent.includes('serving') || option.textContent.includes('special')) {
                option.style.display = 'none';
            } else {
                option.style.display = 'block';
            }
        });
    } else {
        // Show all units
        const options = yieldUnitSelect.querySelectorAll('option');
        options.forEach(option => {
            option.style.display = 'block';
        });
    }
}

function setupItemHandlers() {
    const itemTypeToggle = document.getElementById('item-type-toggle');
    if (itemTypeToggle) {
        itemTypeToggle.addEventListener('change', handleItemTypeChange);
    }
    
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', addRecipeItem);
    }
}

function handleItemTypeChange(e) {
    const itemType = e.target.value;
    const ingredientSection = document.getElementById('ingredient-item-section');
    const subRecipeSection = document.getElementById('sub-recipe-item-section');
    
    if (!ingredientSection || !subRecipeSection) return;
    
    if (itemType === 'ingredient') {
        ingredientSection.style.display = 'block';
        subRecipeSection.style.display = 'none';
        // Don't set required - validation happens in addIngredientItem()
    } else {
        ingredientSection.style.display = 'none';
        subRecipeSection.style.display = 'block';
        // Don't set required - validation happens in addSubRecipeItem()
    }
}

function addRecipeItem() {
    const itemType = document.getElementById('item-type-toggle').value;
    
    if (itemType === 'ingredient') {
        addIngredientItem();
    } else {
        addSubRecipeItem();
    }
}

function addIngredientItem() {
    const ingredientId = parseInt(document.getElementById('ingredient-select').value);
    const quantity = parseFloat(document.getElementById('item-quantity').value);
    const unitId = parseInt(document.getElementById('item-unit-select').value);
    const sizeQualifier = document.getElementById('item-size-qualifier').value || null;
    const preparationNotes = document.getElementById('item-preparation-notes').value.trim() || null;
    
    if (!ingredientId || !quantity || !unitId) {
        showError('Please fill in ingredient, quantity, and unit.');
        return;
    }
    
    const ingredient = ingredients.find(i => i.id === ingredientId);
    const unit = unitTypes.find(u => u.id === unitId);
    
    recipeItems.push({
        item_type: 'ingredient',
        ingredient_id: ingredientId,
        quantity,
        unit_id: unitId,
        size_qualifier: sizeQualifier,
        preparation_notes: preparationNotes,
    });
    
    displayRecipeFormItems();
    
    // Reset form
    document.getElementById('ingredient-select').value = '';
    document.getElementById('item-quantity').value = '';
    document.getElementById('item-unit-select').value = '';
    document.getElementById('item-size-qualifier').value = '';
    document.getElementById('item-preparation-notes').value = '';
}

function addSubRecipeItem() {
    const subRecipeId = parseInt(document.getElementById('sub-recipe-select').value);
    const quantity = parseFloat(document.getElementById('item-quantity').value);
    const unitId = parseInt(document.getElementById('item-unit-select').value);
    
    if (!subRecipeId || !quantity || !unitId) {
        showError('Please fill in sub-recipe, quantity, and unit.');
        return;
    }
    
    recipeItems.push({
        item_type: 'sub_recipe',
        sub_recipe_id: subRecipeId,
        quantity,
        unit_id: unitId,
    });
    
    displayRecipeFormItems();
    
    // Reset form
    document.getElementById('sub-recipe-select').value = '';
    document.getElementById('item-quantity').value = '';
    document.getElementById('item-unit-select').value = '';
}

function displayRecipeFormItems() {
    const container = document.getElementById('recipe-items-list');
    if (!container) return;
    
    if (recipeItems.length === 0) {
        container.innerHTML = '<p style="color: #999; font-style: italic; margin: 0;">No ingredients added yet. Add your first ingredient below.</p>';
        container.style.border = '1px dashed #ddd';
        return;
    }
    
    container.style.border = '1px solid #ddd';
    container.style.borderStyle = 'solid';
    container.innerHTML = '';
    
    recipeItems.forEach((item, index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'recipe-item-row';
        
        if (item.item_type === 'ingredient') {
            const ingredient = ingredients.find(i => i.id === item.ingredient_id);
            const unit = unitTypes.find(u => u.id === item.unit_id);
            
            let itemText = `${item.quantity} ${unit.name} ${ingredient.name}`;
            if (item.size_qualifier) {
                itemText = `${item.size_qualifier} ${itemText}`;
            }
            if (item.preparation_notes) {
                itemText += ` (${item.preparation_notes})`;
            }
            
            itemDiv.innerHTML = `
                <span>${itemText}</span>
                <button class="btn-remove" onclick="removeRecipeItem(${index})">Remove</button>
            `;
        } else {
            const subRecipe = subRecipes.find(r => r.id === item.sub_recipe_id);
            const unit = unitTypes.find(u => u.id === item.unit_id);
            
            itemDiv.innerHTML = `
                <span>${item.quantity} ${unit.name} ${subRecipe.name}</span>
                <button class="btn-remove" onclick="removeRecipeItem(${index})">Remove</button>
            `;
        }
        
        container.appendChild(itemDiv);
    });
}

function removeRecipeItem(index) {
    recipeItems.splice(index, 1);
    displayRecipeFormItems();
}

async function saveRecipe() {
    const name = document.getElementById('recipe-name').value.trim();
    const isSubRecipeCheck = document.getElementById('is-sub-recipe');
    const isSubRecipe = isSubRecipeCheck ? isSubRecipeCheck.checked : false;
    const yieldQuantity = parseFloat(document.getElementById('yield-quantity').value);
    const yieldUnitId = parseInt(document.getElementById('yield-unit-select').value);
    const pageNumberInput = document.getElementById('recipe-page-number');
    const pageNumber = pageNumberInput ? (pageNumberInput.value.trim() ? parseInt(pageNumberInput.value) : null) : null;
    
    if (!name || !yieldQuantity || !yieldUnitId) {
        showError('Please fill in all required fields.');
        return;
    }
    
    if (recipeItems.length === 0) {
        showError('Please add at least one ingredient or sub-recipe.');
        return;
    }
    
    try {
        const recipe = {
            name,
            is_sub_recipe: isSubRecipe,
            yield_quantity: yieldQuantity,
            yield_unit_id: yieldUnitId,
            page_number: pageNumber,
            items: recipeItems,
        };
        
        if (isEditing && currentRecipe) {
            // Update existing recipe
            await updateRecipe(currentRecipe, recipe);
            showSuccess('Recipe updated successfully!');
        } else {
            // Create new recipe
            await createRecipe(recipe);
            showSuccess('Recipe created successfully!');
        }
        
        // Reload recipes
        recipes = await getRecipes();
        subRecipes = recipes.filter(r => r.is_sub_recipe);
        displayRecipes();
        
        // Reset form
        cancelEdit();
        
    } catch (error) {
        showError(`Failed to ${isEditing ? 'update' : 'create'} recipe: ` + error.message);
    }
}

async function editRecipe(id) {
    try {
        isEditing = true;
        currentRecipe = id;
        
        // Show form if hidden
        const formColumn = document.getElementById('recipe-form-column');
        const showFormBtn = document.getElementById('show-form-btn');
        const twoColumn = document.querySelector('.two-column');
        if (formColumn && (formColumn.style.display === 'none' || !formColumn.style.display)) {
            formColumn.style.display = 'block';
            if (twoColumn) {
                twoColumn.classList.add('form-visible');
            }
            if (showFormBtn) {
                showFormBtn.style.display = 'none';
            }
        }
        
        // Load recipe data
        const recipe = await getRecipe(id);
        
        // Populate form with recipe data
        document.getElementById('recipe-name').value = recipe.name;
        document.getElementById('yield-quantity').value = recipe.yield_quantity;
        document.getElementById('yield-unit-select').value = recipe.yield_unit_id;
        const pageNumberInput = document.getElementById('recipe-page-number');
        if (pageNumberInput && recipe.page_number) {
            pageNumberInput.value = recipe.page_number;
        }
        
        // Set is_sub_recipe checkbox (disabled - immutable)
        const isSubRecipeCheck = document.getElementById('is-sub-recipe');
        if (isSubRecipeCheck) {
            isSubRecipeCheck.checked = recipe.is_sub_recipe;
            isSubRecipeCheck.disabled = true;  // Immutable per requirements
        }
        
        // Load recipe items
        recipeItems = recipe.items || [];
        displayRecipeFormItems();
        
        // Update form title and button
        const formTitle = formColumn ? formColumn.querySelector('h3') : document.querySelector('.column h3');
        if (formTitle) {
            formTitle.textContent = 'Edit Recipe';
        }
        
        const submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.textContent = 'Update Recipe';
        }
        
        // Show cancel button
        const cancelBtn = document.getElementById('cancel-edit-btn');
        if (cancelBtn) {
            cancelBtn.style.display = 'inline-block';
        }
        
        // Scroll to form
        document.querySelector('.column:last-child').scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        showError('Failed to load recipe: ' + error.message);
        isEditing = false;
        currentRecipe = null;
    }
}

async function deleteRecipe(id) {
    // Find the recipe to show its name in the confirmation
    const recipe = recipes.find(r => r.id === id);
    const recipeName = recipe ? recipe.name : 'this recipe';
    
    // Check if recipe is being edited
    if (isEditing && currentRecipe === id) {
        showError('Please finish editing this recipe or cancel before deleting it.');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete "${recipeName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        const result = await deleteRecipeAPI(id);
        
        // Show warning if it was a sub-recipe that was referenced
        if (result.was_sub_recipe && result.referencing_recipes && result.referencing_recipes.length > 0) {
            const refNames = result.referencing_recipes.map(r => r.name).join(', ');
            showSuccess(`Recipe "${recipeName}" deleted. Note: This was a sub-recipe that was removed from: ${refNames}`);
        } else {
            showSuccess(`Recipe "${recipeName}" deleted successfully.`);
        }
        
        // Reload recipes list
        recipes = await getRecipes();
        subRecipes = recipes.filter(r => r.is_sub_recipe);
        displayRecipes();
        
        // If we deleted a sub-recipe, refresh the sub-recipe selector
        populateSubRecipeSelector();
        
    } catch (error) {
        showError('Failed to delete recipe: ' + error.message);
    }
}

function showError(message) {
    const alert = document.getElementById('alert');
    if (alert) {
        alert.className = 'alert alert-error';
        alert.textContent = message;
        alert.style.display = 'block';
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

function showSuccess(message) {
    const alert = document.getElementById('alert');
    if (alert) {
        alert.className = 'alert alert-success';
        alert.textContent = message;
        alert.style.display = 'block';
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    }
}

function cancelEdit() {
    isEditing = false;
    currentRecipe = null;
    recipeItems = [];
    
    // Reset form
    document.getElementById('recipe-form').reset();
    const isSubRecipeCheck = document.getElementById('is-sub-recipe');
    if (isSubRecipeCheck) {
        isSubRecipeCheck.disabled = false;
    }
    
    // Reset form title and button
    const formTitle = document.querySelector('.column h3');
    if (formTitle) {
        formTitle.textContent = 'Add New Recipe';
    }
    
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.textContent = 'Create Recipe';
    }
    
    const cancelBtn = document.getElementById('cancel-edit-btn');
    if (cancelBtn) {
        cancelBtn.style.display = 'none';
    }
    
    displayRecipeFormItems();
}

function toggleRecipeForm() {
    const formColumn = document.getElementById('recipe-form-column');
    const showFormBtn = document.getElementById('show-form-btn');
    const twoColumn = document.querySelector('.two-column');
    
    if (!formColumn) return;
    
    if (formColumn.style.display === 'none' || !formColumn.style.display) {
        // Show form
        formColumn.style.display = 'block';
        if (twoColumn) {
            twoColumn.classList.add('form-visible');
        }
        if (showFormBtn) {
            showFormBtn.style.display = 'none';
        }
    } else {
        // Hide form
        formColumn.style.display = 'none';
        if (twoColumn) {
            twoColumn.classList.remove('form-visible');
        }
        if (showFormBtn) {
            showFormBtn.style.display = 'inline-block';
        }
        // Cancel any edit in progress
        if (isEditing) {
            cancelEdit();
        }
    }
}

// Make functions available globally
window.removeRecipeItem = removeRecipeItem;
window.handleItemTypeChange = handleItemTypeChange;
window.editRecipe = editRecipe;
window.toggleRecipeForm = toggleRecipeForm;
window.deleteRecipe = deleteRecipe;
window.cancelEdit = cancelEdit;

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRecipesPage);
} else {
    initRecipesPage();
}

