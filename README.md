# Trio Snacks - Snacks Shop Website with Billing & POS System

A modern, responsive Snacks Shop Website with an integrated Billing (POS) System built with Flask (Python), SQLite database, and vanilla JavaScript.

## Features

### 🏠 Public Pages
- **Home Page**: Shop branding, popular snacks display, special offers, and call-to-action
- **Menu Page**: Browse snacks by category (chips, sweets, bakery, drinks) with search functionality

### 💰 Billing/POS System (Core Feature)
- Real-time product search and selection
- Shopping cart with quantity controls
- Automatic price calculation (subtotal, tax, discount, total)
- Customer details input (name, phone number)
- Invoice number auto-generation
- Print & PDF download functionality
- Barcode scanner support (keyboard input simulation)
- Dark mode for billing screen
- Multi-language support (English + Tamil)

### 📊 Orders History
- View orders with filters (daily, weekly, monthly, all)
- Order details view
- Sales summary (total sales, order count)
- PDF invoice download

### 👨‍💼 Admin Dashboard
- **Product Management**: Add, edit, delete snacks
- Update prices and stock quantities
- Category management
- Low stock alerts
- **Analytics**: 
  - Total sales and profit calculations
  - Top-selling items
  - Sales trends
- **Settings**: Configure tax rate, GST rate, shop information, stock alerts

### 🔐 Authentication
- Login system for admin and cashier
- Role-based access control
- Session management

## Tech Stack

- **Backend**: Python Flask 3.0.0
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **PDF Generation**: ReportLab
- **Barcode**: python-barcode (backend) + keyboard input detection (frontend)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd "TRIO SNACKS"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   The database will be automatically created when you run the application for the first time.

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to: `http://localhost:5000`
   - Default admin credentials: `admin` / `admin123`
   - Default cashier credentials: `cashier` / `cashier123`

## Project Structure

```
snacks-shop/
├── app.py                 # Flask application entry point
├── config.py              # Configuration settings
├── models.py              # Database models (SQLAlchemy)
├── auth.py                # Authentication utilities
├── pdf_generator.py       # Invoice PDF generation
├── requirements.txt       # Python dependencies
├── database.db            # SQLite database (auto-generated)
├── static/
│   ├── css/
│   │   ├── main.css       # Main stylesheet
│   │   ├── billing.css    # Billing/POS specific styles
│   │   └── dark-mode.css  # Dark mode styles
│   ├── js/
│   │   ├── main.js        # Common JavaScript utilities
│   │   ├── billing.js     # Billing/POS functionality
│   │   ├── admin.js       # Admin dashboard scripts
│   │   ├── barcode.js     # Barcode scanner integration
│   │   └── i18n.js        # Multi-language support
│   └── images/
│       └── products/      # Product images
├── templates/
│   ├── base.html          # Base template with navigation
│   ├── home.html          # Home page
│   ├── menu.html          # Menu page (public)
│   ├── login.html         # Login page
│   ├── billing.html       # Billing/POS page
│   ├── orders.html        # Orders history page
│   ├── order_detail.html  # Order details page
│   └── admin/
│       ├── dashboard.html # Admin dashboard
│       ├── products.html  # Product management
│       └── settings.html # Settings page
└── README.md              # This file
```

## Usage Guide

### For Shop Owner (Admin)

1. **Login** with admin credentials
2. **Add Products**: Go to Admin → Manage Products → Add New Product
   - Enter product name, category, price, stock quantity
   - Optionally add barcode and description
3. **Configure Settings**: Go to Admin → Settings
   - Set shop name, address, phone
   - Configure tax rate, GST rate
   - Set stock alert threshold
4. **View Analytics**: Check the Admin Dashboard for sales statistics and top-selling items

### For Cashier

1. **Login** with cashier credentials
2. **Billing**: Go to Billing page
   - Search or scan products to add to cart
   - Adjust quantities, apply discounts
   - Enter customer details (optional)
   - Process order to generate invoice
3. **View Orders**: Check Orders History to view past transactions

### Barcode Scanner Usage

- Connect a USB barcode scanner (it will work as a keyboard input device)
- On the Billing page, click the search box
- Scan a barcode - the product will be automatically added to cart
- Make sure products have barcodes configured in the admin panel

### Dark Mode

- Click the moon icon (🌙) in the Billing page header to toggle dark mode
- Preference is saved in browser localStorage

### Multi-language Support

- Click the globe icon (🌐) in the Billing page header to toggle between English and Tamil
- Preference is saved in browser localStorage

## Default Settings

- **Tax Rate**: 5%
- **GST Rate**: 0%
- **Stock Alert Threshold**: 10 units
- **Shop Name**: Trio Snacks

These can be changed in Admin → Settings.

## Security Notes

- Change default passwords after first login
- In production, set a strong `SECRET_KEY` in `config.py` or as environment variable
- Consider using a production WSGI server (e.g., Gunicorn) instead of Flask's development server
- Use environment variables for sensitive configuration

## Features in Detail

### Billing System Flow
1. Cashier logs in → Billing page
2. Search/scan product → Add to cart
3. Adjust quantities, apply discount
4. Enter customer details (optional)
5. Calculate total (subtotal + tax - discount)
6. Generate invoice → Save order → Update inventory
7. Print/download PDF

### Invoice Generation
- PDF invoices include:
  - Shop details
  - Invoice number (auto-generated)
  - Date and time
  - Customer information (if provided)
  - Itemized list with quantities and prices
  - Subtotal, tax, discount, and total
  - Footer message

### Inventory Management
- Stock automatically decreases when orders are processed
- Products marked as unavailable when stock reaches 0
- Low stock alerts in admin dashboard (configurable threshold)

## Troubleshooting

### Database Issues
- If you encounter database errors, delete `database.db` and restart the app (it will recreate)
- Make sure you have write permissions in the project directory

### PDF Generation Issues
- Ensure ReportLab is properly installed: `pip install reportlab`
- Check that the `static/images/products/` directory exists

### Barcode Scanner Not Working
- Make sure the barcode scanner is set to "Keyboard Wedge" mode
- Test by scanning into a text editor first
- Ensure products have barcodes configured in admin panel

## Development

### Adding New Features
- Backend routes: Add to `app.py`
- Frontend: Add templates in `templates/` and JavaScript in `static/js/`
- Styles: Add to appropriate CSS file in `static/css/`

### Database Migrations
- For schema changes, you may need to delete `database.db` and restart
- In production, consider using Flask-Migrate for proper migrations

## License

This project is created for educational and commercial use.

## Support

For issues or questions, please check the code comments or refer to Flask documentation.

---

**Built with ❤️ for local snacks shops**

