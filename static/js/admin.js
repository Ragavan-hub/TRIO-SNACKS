/* Admin Dashboard JavaScript */

// Show add product modal
function showAddProductModal() {
    const modal = document.getElementById('product-modal');
    const form = document.getElementById('product-form');
    const title = document.getElementById('modal-title');
    const imagePreview = document.getElementById('image-preview');
    
    title.textContent = 'Add Product';
    form.action = '/admin/products/add';
    form.method = 'POST';
    form.reset();
    imagePreview.innerHTML = '';
    
    modal.style.display = 'block';
}

// Show edit product modal
function showEditProductModal(id, name, category, price, description, imageUrl) {
    const modal = document.getElementById('product-modal');
    const form = document.getElementById('product-form');
    const title = document.getElementById('modal-title');
    const imagePreview = document.getElementById('image-preview');
    
    title.textContent = 'Edit Product';
    form.action = `/admin/products/${id}/edit`;
    form.method = 'POST';
    
    // Populate form
    document.getElementById('product-name').value = name;
    document.getElementById('product-category').value = category;
    document.getElementById('product-price').value = price;
    document.getElementById('product-description').value = description || '';
    
    // Show current image if exists
    if (imageUrl) {
        imagePreview.innerHTML = `
            <p><strong>Current Image:</strong></p>
            <img src="/static/images/products/${imageUrl}" alt="Current" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; margin-top: 5px;">
            <p style="font-size: 0.875rem; color: #666; margin-top: 5px;">Upload new image to replace</p>
        `;
    } else {
        imagePreview.innerHTML = '';
    }
    
    modal.style.display = 'block';
}

// Image preview on file select
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('product-image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const imagePreview = document.getElementById('image-preview');
            
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    alert('Image size must be less than 5MB');
                    e.target.value = '';
                    imagePreview.innerHTML = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `
                        <p><strong>Preview:</strong></p>
                        <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd; border-radius: 4px; margin-top: 5px;">
                    `;
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.innerHTML = '';
            }
        });
    }
});

// Close product modal
function closeProductModal() {
    const modal = document.getElementById('product-modal');
    modal.style.display = 'none';
}

// Delete product
function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
        return;
    }
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/admin/products/${productId}/delete`;
    document.body.appendChild(form);
    form.submit();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('product-modal');
    if (event.target === modal) {
        closeProductModal();
    }
}

