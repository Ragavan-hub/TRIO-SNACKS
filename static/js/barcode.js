/* Barcode Scanner Integration */

let barcodeBuffer = '';
let barcodeTimeout;

function initBarcodeScanner() {
    const searchInput = document.getElementById('product-search');
    if (!searchInput) return;
    
    // Listen for keyboard input (barcode scanners typically send data as keyboard input)
    searchInput.addEventListener('keydown', function(e) {
        // Clear buffer if too much time has passed (user is typing normally)
        if (barcodeTimeout) {
            clearTimeout(barcodeTimeout);
        }
        
        // If Enter is pressed and buffer looks like a barcode (long string, no spaces)
        if (e.key === 'Enter' && barcodeBuffer.length > 5 && !barcodeBuffer.includes(' ')) {
            e.preventDefault();
            searchByBarcode(barcodeBuffer);
            barcodeBuffer = '';
            return;
        }
        
        // Accumulate characters (barcode scanners send data very quickly)
        if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
            barcodeBuffer += e.key;
            
            // Clear buffer after 100ms of no input (user is typing normally)
            barcodeTimeout = setTimeout(() => {
                barcodeBuffer = '';
            }, 100);
        } else if (e.key === 'Enter') {
            // Normal search on Enter
            barcodeBuffer = '';
        }
    });
    
    // Also listen for paste events (some scanners use clipboard)
    searchInput.addEventListener('paste', function(e) {
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        if (pastedText.length > 5 && !pastedText.includes(' ')) {
            e.preventDefault();
            searchByBarcode(pastedText.trim());
        }
    });
}

// Search product by barcode
async function searchByBarcode(barcode) {
    try {
        const response = await fetch(`/api/products?barcode=${encodeURIComponent(barcode)}`);
        const products = await response.json();
        
        if (products.length > 0) {
            // If product found, add to cart
            const product = products[0];
            if (product.stock > 0) {
                addToCart(product.id);
                showNotification(`Product found: ${product.name}`, 'success');
            } else {
                showNotification('Product out of stock', 'error');
            }
        } else {
            showNotification('Product not found', 'error');
        }
        
        // Clear search input
        document.getElementById('product-search').value = '';
    } catch (error) {
        console.error('Error searching by barcode:', error);
        showNotification('Error searching product', 'error');
    }
}

