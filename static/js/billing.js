/* Billing/POS JavaScript */

let cart = {};
let taxRate = window.taxRate || 5.0; // Use taxRate from page context

// Load cart from session
async function loadCart() {
    try {
        const response = await fetch('/api/cart');
        const data = await response.json();
        cart = data.cart || {};
        renderCart();
        calculateTotal();
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

// Add product to cart
async function addToCart(productId) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showNotification(data.error, 'error');
            return;
        }
        
        cart = data.cart;
        renderCart();
        calculateTotal();
        showNotification('Item added to cart', 'success');
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Error adding item to cart', 'error');
    }
}

// Update item quantity in cart
async function updateCartItem(productId, quantity) {
    if (quantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showNotification(data.error, 'error');
            return;
        }
        
        cart = data.cart;
        renderCart();
        calculateTotal();
    } catch (error) {
        console.error('Error updating cart:', error);
        showNotification('Error updating cart', 'error');
    }
}

// Remove item from cart
async function removeFromCart(productId) {
    try {
        const response = await fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showNotification(data.error, 'error');
            return;
        }
        
        cart = data.cart;
        renderCart();
        calculateTotal();
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('Error removing item from cart', 'error');
    }
}

// Clear cart
async function clearCart() {
    if (Object.keys(cart).length === 0) return;
    
    if (!confirm('Are you sure you want to clear the cart?')) return;
    
    try {
        const response = await fetch('/api/cart/clear', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            cart = {};
            renderCart();
            calculateTotal();
            showNotification('Cart cleared', 'success');
        }
    } catch (error) {
        console.error('Error clearing cart:', error);
        showNotification('Error clearing cart', 'error');
    }
}

// Render cart items
function renderCart() {
    const cartItems = document.getElementById('cart-items');
    
    if (Object.keys(cart).length === 0) {
        cartItems.innerHTML = '<p class="empty-cart" data-i18n="cart_empty">Cart is empty</p>';
        return;
    }
    
    let html = '';
    
    for (const [productId, item] of Object.entries(cart)) {
        const itemTotal = item.price * item.quantity;
        html += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
                    <p class="item-price">${formatCurrency(item.price)} each</p>
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-control">
                        <button onclick="updateCartItem(${productId}, ${item.quantity - 1})">-</button>
                        <input type="number" value="${item.quantity}" min="1" 
                               onchange="updateCartItem(${productId}, parseInt(this.value))">
                        <button onclick="updateCartItem(${productId}, ${item.quantity + 1})">+</button>
                    </div>
                    <span class="cart-item-total">${formatCurrency(itemTotal)}</span>
                    <button class="cart-item-remove" onclick="removeFromCart(${productId})" title="Remove">×</button>
                </div>
            </div>
        `;
    }
    
    cartItems.innerHTML = html;
    updateI18n(); // Update translations if i18n is loaded
}

// Calculate totals (tax removed)
function calculateTotal() {
    let subtotal = 0;
    
    for (const item of Object.values(cart)) {
        subtotal += item.price * item.quantity;
    }
    
    const discountInput = document.getElementById('discount-input');
    const discount = parseFloat(discountInput.value) || 0;
    
    const discountAmount = Math.min(discount, subtotal);
    const total = subtotal - discountAmount;
    
    document.getElementById('subtotal').textContent = formatCurrency(subtotal);
    document.getElementById('total-amount').textContent = formatCurrency(total);
}

// Process order
async function processOrder() {
    if (Object.keys(cart).length === 0) {
        showNotification('Cart is empty', 'error');
        return;
    }
    
    const discountInput = document.getElementById('discount-input');
    const discount = parseFloat(discountInput.value) || 0;
    
    try {
        const response = await fetch('/api/order/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                discount: discount
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showNotification(data.error, 'error');
            return;
        }
        
        if (data.success) {
            showNotification('Order processed successfully!', 'success');
            
            // Clear discount
            discountInput.value = 0;
            
            // Clear cart
            cart = {};
            renderCart();
            calculateTotal();
            
            // Optionally redirect to order detail or show invoice
            setTimeout(() => {
                if (confirm('Order processed! Would you like to view the invoice?')) {
                    window.location.href = `/orders/${data.order_id}`;
                }
            }, 1000);
        }
    } catch (error) {
        console.error('Error processing order:', error);
        showNotification('Error processing order', 'error');
    }
}

// Search products
function searchProducts() {
    const search = document.getElementById('product-search').value.trim();
    const category = currentCategory || 'all';
    
    fetch(`/api/products?category=${category}&search=${encodeURIComponent(search)}`)
        .then(response => response.json())
        .then(products => {
            renderProducts(products);
        })
        .catch(error => {
            console.error('Error searching products:', error);
        });
}

// Filter by category
function filterByCategory(category) {
    currentCategory = category;
    
    // Update active button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.category-btn[data-category="${category}"]`).classList.add('active');
    
    // Fetch and render products
    const search = document.getElementById('product-search').value.trim();
    fetch(`/api/products?category=${category}&search=${encodeURIComponent(search)}`)
        .then(response => response.json())
        .then(products => {
            renderProducts(products);
        })
        .catch(error => {
            console.error('Error filtering products:', error);
        });
}

// Render products list
function renderProducts(products) {
    const productsList = document.getElementById('products-list');
    
    if (products.length === 0) {
        productsList.innerHTML = '<p class="empty-cart">No products found</p>';
        return;
    }
    
    let html = '';
    
    products.forEach(product => {
        const imageUrl = product.image_url ? `/static/images/products/${product.image_url}` : '';
        html += `
            <div class="product-item" data-product-id="${product.id}" data-category="${product.category}">
                <div class="product-item-image">
                    ${imageUrl ? 
                        `<img src="${imageUrl}" alt="${product.name}" onerror="this.parentElement.innerHTML='<div class=\\'product-image-placeholder-small\\'>${product.name[0]}</div>'">` :
                        `<div class="product-image-placeholder-small">${product.name[0]}</div>`
                    }
                </div>
                    <div class="product-item-info">
                        <h4>${product.name}</h4>
                        <p class="product-category">${product.category.charAt(0).toUpperCase() + product.category.slice(1)}</p>
                    </div>
                <div class="product-item-actions">
                    <span class="product-price">${formatCurrency(product.price)}</span>
                    <button class="btn btn-sm btn-primary" onclick="addToCart(${product.id})">Add</button>
                </div>
            </div>
        `;
    });
    
    productsList.innerHTML = html;
}

// Initialize - called after page loads
function initBilling() {
    // Use taxRate from global scope (set in billing.html)
    if (typeof window.taxRate !== 'undefined') {
        taxRate = window.taxRate;
    }
    
    // Discount input change handler
    const discountInput = document.getElementById('discount-input');
    if (discountInput) {
        discountInput.addEventListener('input', calculateTotal);
    }
    
    // Product search enter key
    const productSearch = document.getElementById('product-search');
    if (productSearch) {
        productSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchProducts();
            }
        });
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBilling);
} else {
    initBilling();
}

