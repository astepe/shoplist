/**
 * Ingredient Management Page Logic
 */

let ingredientTypes = [];
let unitTypes = [];
let ingredients = [];
let currentIngredient = null;
let conversionRules = [];
let sizeEstimationRules = [];
let defaultIngredients = [];

// Initialize page
async function initIngredientsPage() {
    try {
        // Display ingredients (read-only view)
        await displayIngredients();
        
    } catch (error) {
        const container = document.getElementById('ingredients-list');
        if (container) {
            container.innerHTML = `<p style="color: red;">Failed to load ingredients: ${error.message}</p>`;
        }
    }
}

function populateIngredientTypes() {
    const select = document.getElementById('ingredient-type-select');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select type...</option>';
    ingredientTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.name;
        select.appendChild(option);
    });
}

function populateUnitTypes() {
    const shoppingUnitSelect = document.getElementById('shopping-unit-select');
    if (!shoppingUnitSelect) return;
    
    // Filter for count-based units (typical shopping units)
    const countUnits = unitTypes.filter(u => u.category === 'count');
    
    shoppingUnitSelect.innerHTML = '<option value="">Select shopping unit...</option>';
    countUnits.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.id;
        option.textContent = unit.name;
        shoppingUnitSelect.appendChild(option);
    });
    
    // Setup conversion rule and size rule handlers
    setupConversionRuleHandlers();
    setupSizeEstimationRuleHandlers();
}

async function displayIngredients() {
    const container = document.getElementById('ingredients-list');
    if (!container) return;
    
    try {
        // Load ingredients fresh from API
        const allIngredients = await getIngredients();
        
        if (allIngredients.length === 0) {
            container.innerHTML = '<p>No ingredients found.</p>';
            return;
        }
        
        // Group by type
        const grouped = {};
        allIngredients.forEach(ing => {
            const typeName = ing.type_name || 'Unknown';
            if (!grouped[typeName]) {
                grouped[typeName] = [];
            }
            grouped[typeName].push(ing);
        });
        
        container.innerHTML = '';
        
        Object.keys(grouped).sort().forEach(typeName => {
            const typeSection = document.createElement('div');
            typeSection.className = 'type-section';
            
            const heading = document.createElement('h4');
            heading.textContent = typeName;
            heading.style.marginTop = '1.5rem';
            heading.style.marginBottom = '0.5rem';
            heading.style.fontSize = '1.2rem';
            typeSection.appendChild(heading);
            
            const list = document.createElement('ul');
            list.style.listStyle = 'none';
            list.style.padding = '0';
            list.style.margin = '0';
            grouped[typeName].forEach(ing => {
                const li = document.createElement('li');
                li.style.padding = '0.5rem 0';
                li.style.borderBottom = '1px solid #eee';
                li.innerHTML = `
                    <strong>${ing.name}</strong> 
                    <span class="shopping-unit" style="color: #666; margin-left: 0.5rem;">(Shopping unit: ${ing.shopping_unit_name})</span>
                `;
                list.appendChild(li);
            });
            
            typeSection.appendChild(list);
            container.appendChild(typeSection);
        });
    } catch (error) {
        container.innerHTML = `<p style="color: red;">Error loading ingredients: ${error.message}</p>`;
    }
}

function setupFormHandlers() {
    const form = document.getElementById('ingredient-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveIngredient();
    });
}

async function saveIngredient() {
    const name = document.getElementById('ingredient-name').value.trim();
    const typeId = document.getElementById('ingredient-type-select').value;
    const shoppingUnitId = document.getElementById('shopping-unit-select').value;
    const useDefaults = document.getElementById('use-default-conversions').checked;
    
    if (!name || !typeId || !shoppingUnitId) {
        showError('Please fill in all required fields.');
        return;
    }
    
    // Get conversion rules
    const conversionRulesData = getConversionRules();
    
    // If using defaults, we'll let the backend fill them in
    // Otherwise, we need at least one rule
    if (!useDefaults && conversionRulesData.length === 0) {
        showError('Please add at least one conversion rule, or enable default conversions.');
        return;
    }
    
    // Get size estimation rules (optional, may come from defaults)
    const sizeEstimationRulesData = getSizeEstimationRules();
    
    try {
        const ingredient = {
            name,
            type_id: parseInt(typeId),
            shopping_unit_id: parseInt(shoppingUnitId),
            conversion_rules: conversionRulesData,
            size_estimation_rules: sizeEstimationRulesData,
            use_default_conversions: useDefaults,
        };
        
        await createIngredient(ingredient);
        showSuccess('Ingredient created successfully!');
        
        // Reload ingredients
        ingredients = await getIngredients();
        displayIngredients();
        
        // Reset form
        document.getElementById('ingredient-form').reset();
        clearConversionRules();
        clearSizeEstimationRules();
        
        // Reset hints
        const hint = document.getElementById('default-conversions-hint');
        if (hint) {
            hint.textContent = '';
        }
        
    } catch (error) {
        showError('Failed to create ingredient: ' + error.message);
    }
}

function setupConversionRuleHandlers() {
    const addBtn = document.getElementById('add-conversion-rule-btn');
    if (!addBtn) return;
    
    addBtn.addEventListener('click', addConversionRule);
}

function setupSizeEstimationRuleHandlers() {
    const addBtn = document.getElementById('add-size-rule-btn');
    if (!addBtn) return;
    
    addBtn.addEventListener('click', addSizeEstimationRule);
}

function addConversionRule() {
    const container = document.getElementById('conversion-rules-list');
    if (!container) return;
    
    const ruleIndex = conversionRules.length;
    const ruleDiv = document.createElement('div');
    ruleDiv.className = 'conversion-rule';
    ruleDiv.id = `conversion-rule-${ruleIndex}`;
    
    // Get shopping unit ID (will be set when user selects it)
    const shoppingUnitId = document.getElementById('shopping-unit-select').value;
    
    // Recipe units (volume and weight)
    const recipeUnits = unitTypes.filter(u => u.category === 'volume' || u.category === 'weight' || u.category === 'count');
    
    ruleDiv.innerHTML = `
        <div class="rule-row">
            <label>From Unit (Recipe Unit):</label>
            <select class="from-unit-select" required>
                <option value="">Select unit...</option>
                ${recipeUnits.map(u => `<option value="${u.id}">${u.name} (${u.category})</option>`).join('')}
            </select>
            <label>Conversion Factor:</label>
            <input type="number" step="0.0001" class="conversion-factor" required placeholder="e.g., 0.167">
            <small>How many shopping units per recipe unit (e.g., 1 cup = 0.167 heads)</small>
            <button type="button" class="btn-remove" onclick="removeConversionRule(${ruleIndex})">Remove</button>
        </div>
    `;
    
    container.appendChild(ruleDiv);
    conversionRules.push({ index: ruleIndex });
}

function removeConversionRule(index) {
    const ruleDiv = document.getElementById(`conversion-rule-${index}`);
    if (ruleDiv) {
        ruleDiv.remove();
    }
    conversionRules = conversionRules.filter(r => r.index !== index);
}

function addSizeEstimationRule() {
    const container = document.getElementById('size-estimation-rules-list');
    if (!container) return;
    
    const ruleIndex = sizeEstimationRules.length;
    const ruleDiv = document.createElement('div');
    ruleDiv.className = 'size-estimation-rule';
    ruleDiv.id = `size-rule-${ruleIndex}`;
    
    // Weight/volume units for size estimation
    const weightVolumeUnits = unitTypes.filter(u => u.category === 'weight' || u.category === 'volume');
    
    ruleDiv.innerHTML = `
        <div class="rule-row">
            <label>Size:</label>
            <select class="size-qualifier-select" required>
                <option value="small">Small</option>
                <option value="medium" selected>Medium</option>
                <option value="large">Large</option>
            </select>
            <label>Reference Value:</label>
            <input type="number" step="0.01" class="size-value" required placeholder="e.g., 150">
            <label>Unit:</label>
            <select class="size-unit-select" required>
                <option value="">Select unit...</option>
                ${weightVolumeUnits.map(u => `<option value="${u.id}">${u.name}</option>`).join('')}
            </select>
            <small>e.g., Medium onion = 150g</small>
            <button type="button" class="btn-remove" onclick="removeSizeEstimationRule(${ruleIndex})">Remove</button>
        </div>
    `;
    
    container.appendChild(ruleDiv);
    sizeEstimationRules.push({ index: ruleIndex });
}

function removeSizeEstimationRule(index) {
    const ruleDiv = document.getElementById(`size-rule-${ruleIndex}`);
    if (ruleDiv) {
        ruleDiv.remove();
    }
    sizeEstimationRules = sizeEstimationRules.filter(r => r.index !== index);
}

function getConversionRules() {
    const shoppingUnitId = parseInt(document.getElementById('shopping-unit-select').value);
    if (!shoppingUnitId) return [];
    
    const rules = [];
    const ruleDivs = document.querySelectorAll('.conversion-rule');
    
    ruleDivs.forEach(ruleDiv => {
        const fromUnitId = parseInt(ruleDiv.querySelector('.from-unit-select').value);
        const factor = parseFloat(ruleDiv.querySelector('.conversion-factor').value);
        
        if (fromUnitId && !isNaN(factor)) {
            rules.push({
                from_unit_id: fromUnitId,
                to_unit_id: shoppingUnitId,
                conversion_factor: factor,
            });
        }
    });
    
    return rules;
}

function getSizeEstimationRules() {
    const rules = [];
    const ruleDivs = document.querySelectorAll('.size-estimation-rule');
    
    ruleDivs.forEach(ruleDiv => {
        const sizeQualifier = ruleDiv.querySelector('.size-qualifier-select').value;
        const value = parseFloat(ruleDiv.querySelector('.size-value').value);
        const unitId = parseInt(ruleDiv.querySelector('.size-unit-select').value);
        
        if (sizeQualifier && !isNaN(value) && unitId) {
            rules.push({
                size_qualifier: sizeQualifier,
                reference_value: value,
                reference_unit_id: unitId,
            });
        }
    });
    
    return rules;
}

function clearConversionRules() {
    conversionRules = [];
    const container = document.getElementById('conversion-rules-list');
    if (container) {
        container.innerHTML = '';
    }
}

function clearSizeEstimationRules() {
    sizeEstimationRules = [];
    const container = document.getElementById('size-estimation-rules-list');
    if (container) {
        container.innerHTML = '';
    }
}

// Make functions available globally for onclick handlers
window.removeConversionRule = removeConversionRule;
window.removeSizeEstimationRule = removeSizeEstimationRule;

function setupDefaultConversionsHandler() {
    const nameInput = document.getElementById('ingredient-name');
    const defaultCheckbox = document.getElementById('use-default-conversions');
    const addRuleBtn = document.getElementById('add-conversion-rule-btn');
    
    if (nameInput && defaultCheckbox) {
        // Check for defaults when name changes
        nameInput.addEventListener('input', () => {
            checkForDefaultConversions();
        });
        
        // Check when shopping unit changes
        const shoppingUnitSelect = document.getElementById('shopping-unit-select');
        if (shoppingUnitSelect) {
            shoppingUnitSelect.addEventListener('change', () => {
                if (defaultCheckbox.checked) {
                    checkForDefaultConversions();
                }
            });
        }
    }
}

function checkForDefaultConversions() {
    const nameInput = document.getElementById('ingredient-name');
    const defaultCheckbox = document.getElementById('use-default-conversions');
    const hint = document.getElementById('default-conversions-hint');
    const addRuleBtn = document.getElementById('add-conversion-rule-btn');
    
    if (!nameInput || !defaultCheckbox || !hint) return;
    
    const ingredientName = nameInput.value.trim();
    
    if (ingredientName && defaultIngredients.includes(ingredientName)) {
        hint.textContent = `✓ Default conversions available for "${ingredientName}". Enable the checkbox above to use them.`;
        hint.style.color = '#27ae60';
    } else if (ingredientName) {
        hint.textContent = `No default conversions available for "${ingredientName}". You'll need to add conversion rules manually.`;
        hint.style.color = '#666';
    } else {
        hint.textContent = '';
    }
}

async function handleDefaultConversionsToggle() {
    const defaultCheckbox = document.getElementById('use-default-conversions');
    const nameInput = document.getElementById('ingredient-name');
    const shoppingUnitSelect = document.getElementById('shopping-unit-select');
    const addRuleBtn = document.getElementById('add-conversion-rule-btn');
    
    if (!defaultCheckbox || !nameInput || !shoppingUnitSelect) return;
    
    const ingredientName = nameInput.value.trim();
    const shoppingUnitId = shoppingUnitSelect.value;
    
    if (defaultCheckbox.checked && ingredientName && shoppingUnitId && defaultIngredients.includes(ingredientName)) {
        // Clear existing rules
        clearConversionRules();
        clearSizeEstimationRules();
        
        // Hide manual add button (using defaults)
        if (addRuleBtn) {
            addRuleBtn.style.display = 'none';
        }
        
        // Show message that defaults will be applied
        const hint = document.getElementById('default-conversions-hint');
        if (hint) {
            hint.textContent = `✓ Default conversion rules will be automatically applied when you save. You can still add custom rules if needed.`;
            hint.style.color = '#27ae60';
        }
    } else {
        // Show manual add button
        if (addRuleBtn) {
            addRuleBtn.style.display = 'inline-block';
        }
        
        if (!defaultCheckbox.checked && ingredientName) {
            const hint = document.getElementById('default-conversions-hint');
            if (hint && defaultIngredients.includes(ingredientName)) {
                hint.textContent = `Default conversions available but not enabled. Add rules manually or enable defaults.`;
                hint.style.color = '#666';
            } else if (hint) {
                hint.textContent = `No default conversions available for "${ingredientName}". Add rules manually.`;
                hint.style.color = '#666';
            }
        }
    }
}

// Make available globally
window.handleDefaultConversionsToggle = handleDefaultConversionsToggle;

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

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initIngredientsPage);
} else {
    initIngredientsPage();
}

