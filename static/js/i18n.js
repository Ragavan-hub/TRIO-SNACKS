/* Multi-language Support (English + Tamil) */

const translations = {
    en: {
        products: 'Products',
        cart: 'Cart',
        clear: 'Clear',
        cart_empty: 'Cart is empty',
        subtotal: 'Subtotal:',
        tax: 'Tax',
        discount: 'Discount:',
        total: 'Total:',
        customer_details: 'Customer Details',
        customer_name: 'Name:',
        customer_phone: 'Phone:',
        process_order: 'Process Order',
        add_to_cart: 'Add to Cart',
        remove: 'Remove',
        quantity: 'Quantity',
        price: 'Price',
        total_amount: 'Total Amount'
    },
    ta: {
        products: 'தயாரிப்புகள்',
        cart: 'கார்ட்',
        clear: 'அழிக்க',
        cart_empty: 'கார்ட் காலியாக உள்ளது',
        subtotal: 'உப தொகை:',
        tax: 'வரி',
        discount: 'தள்ளுபடி:',
        total: 'மொத்தம்:',
        customer_details: 'வாடிக்கையாளர் விவரங்கள்',
        customer_name: 'பெயர்:',
        customer_phone: 'தொலைபேசி:',
        process_order: 'ஆர்டர் செய்ய',
        add_to_cart: 'கார்ட்டில் சேர்',
        remove: 'நீக்கு',
        quantity: 'அளவு',
        price: 'விலை',
        total_amount: 'மொத்த தொகை'
    }
};

let currentLanguage = localStorage.getItem('language') || 'en';

function initI18n() {
    // Load saved language preference
    currentLanguage = localStorage.getItem('language') || 'en';
    updateI18n();
    
    // Setup language toggle
    const languageToggle = document.getElementById('language-toggle');
    if (languageToggle) {
        languageToggle.addEventListener('click', toggleLanguage);
    }
}

function toggleLanguage() {
    currentLanguage = currentLanguage === 'en' ? 'ta' : 'en';
    localStorage.setItem('language', currentLanguage);
    updateI18n();
    
    const toggle = document.getElementById('language-toggle');
    if (toggle) {
        toggle.textContent = currentLanguage === 'en' ? '🌐' : '🌐';
    }
}

function updateI18n() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage] && translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
}

function t(key) {
    return translations[currentLanguage][key] || translations.en[key] || key;
}

