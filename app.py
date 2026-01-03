"""
Main Flask application for Snacks Shop with POS System
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from models import db, User, Product, Order, OrderItem, Setting, Offer
from auth import login_required, admin_required, get_current_user
from pdf_generator import generate_invoice_pdf
from config import Config
import os
import json
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Initialize default settings
    default_settings = {
        'shop_name': 'Trio Snacks',
        'shop_address': '123 Main Street, City',
        'shop_phone': '+91 9876543210',
        'tax_rate': '5.0',
        'gst_rate': '0.0',
        'stock_alert_threshold': '10',
        'invoice_footer': 'Thank you for your business!'
    }
    
    for key, value in default_settings.items():
        if not Setting.query.filter_by(key=key).first():
            setting = Setting(key=key, value=value)
            db.session.add(setting)
    
    # Initialize default offers if none exist
    if Offer.query.count() == 0:
        default_offers = [
            {'title': 'Buy 2 Get 1 Free', 'description': 'On selected chips and snacks', 'order': 0},
            {'title': 'Weekend Special', 'description': '20% off on all bakery items', 'order': 1},
            {'title': 'Happy Hours', 'description': '10% discount on snacks (7 PM - 9 PM)', 'order': 2}
        ]
        for offer_data in default_offers:
            offer = Offer(
                title=offer_data['title'],
                description=offer_data['description'],
                display_order=offer_data['order'],
                is_active=True
            )
            db.session.add(offer)
    
    db.session.commit()


# ==================== Public Routes ====================

@app.route('/')
def home():
    """Home page - public"""
    # Get popular snacks (top 6 by order count)
    popular_products = db.session.query(
        Product,
        db.func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).group_by(Product.id).order_by(
        db.desc('total_sold')
    ).limit(6).all()
    
    popular = [p[0] for p in popular_products] if popular_products else []
    
    # Get shop settings
    shop_name = Setting.query.filter_by(key='shop_name').first()
    shop_name = shop_name.value if shop_name else 'Trio Snacks'
    
    shop_logo = Setting.query.filter_by(key='shop_logo').first()
    shop_logo = shop_logo.value if shop_logo else None
    
    # Get active offers
    offers = Offer.query.filter_by(is_active=True).order_by(Offer.display_order, Offer.id).all()
    
    return render_template('home.html', popular_products=popular, shop_name=shop_name, shop_logo=shop_logo, offers=offers)


@app.route('/menu')
def menu():
    """Menu page - public"""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_available=True)
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.order_by(Product.name).all()
    
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('menu.html', products=products, categories=categories, 
                         current_category=category, search_query=search)


# ==================== Authentication Routes ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session.permanent = True
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('billing'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('home'))


# ==================== Billing/POS Routes ====================

@app.route('/billing')
@login_required
def billing():
    """Billing/POS page"""
    products = Product.query.filter_by(is_available=True).order_by(Product.name).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('billing.html', products=products, categories=categories)


@app.route('/api/products', methods=['GET'])
@login_required
def api_products():
    """API endpoint to get products"""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_available=True)
    
    if category != 'all':
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.order_by(Product.name).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'image_url': p.image_url or ''
    } for p in products])


@app.route('/api/cart/add', methods=['POST'])
@login_required
def api_cart_add():
    """Add item to cart (session-based)"""
    data = request.json
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    product = Product.query.get_or_404(product_id)
    
    # Initialize cart in session (stock check removed)
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    
    # Add or update item in cart
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity
        }
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart': cart})


@app.route('/api/cart/update', methods=['POST'])
@login_required
def api_cart_update():
    """Update item quantity in cart"""
    data = request.json
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    
    if 'cart' not in session:
        return jsonify({'error': 'Cart is empty'}), 400
    
    cart = session['cart']
    
    if product_id not in cart:
        return jsonify({'error': 'Item not in cart'}), 400
    
    product = Product.query.get(int(product_id))
    
    if quantity <= 0:
        del cart[product_id]
    else:
        cart[product_id]['quantity'] = quantity
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart': cart})


@app.route('/api/cart/remove', methods=['POST'])
@login_required
def api_cart_remove():
    """Remove item from cart"""
    data = request.json
    product_id = str(data.get('product_id'))
    
    if 'cart' not in session:
        return jsonify({'error': 'Cart is empty'}), 400
    
    cart = session['cart']
    
    if product_id in cart:
        del cart[product_id]
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart': cart})


@app.route('/api/cart/clear', methods=['POST'])
@login_required
def api_cart_clear():
    """Clear cart"""
    session['cart'] = {}
    session.modified = True
    return jsonify({'success': True})


@app.route('/api/cart', methods=['GET'])
@login_required
def api_cart():
    """Get current cart"""
    cart = session.get('cart', {})
    return jsonify({'cart': cart})


@app.route('/api/order/process', methods=['POST'])
@login_required
def api_order_process():
    """Process order and generate invoice"""
    try:
        data = request.json
        cart = session.get('cart', {})

        if not cart:
            return jsonify({'error': 'Cart is empty'}), 400

        # Get customer details and discount
        customer_name = data.get('customer_name', '')
        customer_phone = data.get('customer_phone', '')
        discount = float(data.get('discount', 0))

        # Get tax rate from settings
        tax_setting = Setting.query.filter_by(key='tax_rate').first()
        tax_rate = float(tax_setting.value) if tax_setting else 5.0

        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
        tax_amount = (subtotal * tax_rate) / 100
        discount_amount = min(discount, subtotal)
        total_amount = subtotal + tax_amount - discount_amount

        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        # Create order
        order = Order(
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_phone=customer_phone,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            created_by=session['user_id']
        )

        db.session.add(order)
        db.session.flush()

        # Create order items and update inventory
        for product_id_str, item in cart.items():
            product_id = int(product_id_str)
            product = Product.query.get(product_id)

            if product.stock_quantity < item['quantity']:
                db.session.rollback()
                return jsonify({'error': f'Insufficient stock for {product.name}'}), 400

            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=item['quantity'],
                unit_price=item['price'],
                total_price=item['price'] * item['quantity']
            )
            db.session.add(order_item)
            
            # Inventory update removed (stock management disabled)

        db.session.commit()

        # Clear cart
        session['cart'] = {}
        session.modified = True

        return jsonify({
            'success': True,
            'order_id': order.id,
            'invoice_number': invoice_number
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error processing order: {str(e)}'}), 500


@app.route('/invoice/<int:order_id>/pdf')
@login_required
def invoice_pdf(order_id):
    """Generate and download PDF invoice"""
    order = Order.query.get_or_404(order_id)
    
    # Check if user has permission (admin or creator)
    if not get_current_user().is_admin() and order.created_by != session['user_id']:
        return redirect(url_for('billing'))
    
    pdf_buffer = generate_invoice_pdf(order)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'invoice_{order.invoice_number}.pdf'
    )


# ==================== Orders History Routes ====================

@app.route('/orders')
@login_required
def orders():
    """Orders history page"""
    period = request.args.get('period', 'today')
    
    # Get date range based on period
    today = datetime.now().date()
    
    if period == 'today':
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif period == 'week':
        start_date = datetime.combine(today - timedelta(days=7), datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    elif period == 'month':
        start_date = datetime.combine(today - timedelta(days=30), datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
    else:
        start_date = None
        end_date = None
    
    # Query orders
    query = Order.query
    
    # Filter by user if not admin
    if not get_current_user().is_admin():
        query = query.filter_by(created_by=session['user_id'])
    
    if start_date and end_date:
        query = query.filter(Order.created_at >= start_date, Order.created_at <= end_date)
    
    orders_list = query.order_by(Order.created_at.desc()).all()
    
    # Calculate summary
    total_sales = sum(order.total_amount for order in orders_list)
    total_orders = len(orders_list)
    
    return render_template('orders.html', orders=orders_list, period=period, 
                         total_sales=total_sales, total_orders=total_orders)


@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Order details page"""
    order = Order.query.get_or_404(order_id)
    
    # Check permission
    if not get_current_user().is_admin() and order.created_by != session['user_id']:
        return redirect(url_for('orders'))
    
    return render_template('order_detail.html', order=order)


@app.route('/orders/<int:order_id>/delete', methods=['POST'])
@admin_required
def order_delete(order_id):
    """Delete order"""
    order = Order.query.get_or_404(order_id)
    
    try:
        # Delete order items (cascade should handle this, but being explicit)
        OrderItem.query.filter_by(order_id=order_id).delete()
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== Admin Routes ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics
    total_products = Product.query.count()
    
    # Sales statistics
    today = datetime.now().date()
    start_date = datetime.combine(today, datetime.min.time())
    end_date = datetime.combine(today, datetime.max.time())
    
    today_orders = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).all()
    
    today_sales = sum(order.total_amount for order in today_orders)
    
    # Top selling items
    top_items = db.session.query(
        Product.name,
        db.func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem).join(Order).filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).group_by(Product.id).order_by(
        db.desc('total_sold')
    ).limit(5).all()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         today_sales=today_sales,
                         today_orders_count=len(today_orders),
                         top_items=top_items,
                         recent_orders=recent_orders)


@app.route('/admin/products')
@admin_required
def admin_products():
    """Product management page"""
    products = Product.query.order_by(Product.name).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('admin/products.html', products=products, categories=categories)


@app.route('/admin/products/add', methods=['POST'])
@admin_required
def admin_products_add():
    """Add new product"""
    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    description = request.form.get('description', '')
    
    # Handle image upload
    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # Secure filename and save
            filename = secure_filename(file.filename)
            # Add timestamp to make unique
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = filename
    
    product = Product(
        name=name,
        category=category,
        price=price,
        stock_quantity=999,  # Set high default since stock is removed
        description=description,
        barcode=None,  # Barcode removed
        image_url=image_url,
        is_available=True
    )
    
    db.session.add(product)
    db.session.commit()
    
    return redirect(url_for('admin_products'))


@app.route('/admin/products/<int:product_id>/edit', methods=['POST'])
@admin_required
def admin_products_edit(product_id):
    """Edit product"""
    product = Product.query.get_or_404(product_id)
    
    product.name = request.form.get('name')
    product.category = request.form.get('category')
    product.price = float(request.form.get('price', 0))
    product.stock_quantity = 999  # Stock removed, set high default
    product.description = request.form.get('description', '')
    product.barcode = None  # Barcode removed
    product.is_available = True  # Always available since stock is removed
    product.updated_at = datetime.utcnow()
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # Delete old image if exists
            if product.image_url:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], product.image_url)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            
            # Save new image
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            product.image_url = filename
    
    db.session.commit()
    
    return redirect(url_for('admin_products'))


@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def admin_products_delete(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return redirect(url_for('admin_products'))


@app.route('/admin/offers')
@admin_required
def admin_offers():
    """Manage offers page"""
    offers = Offer.query.order_by(Offer.display_order, Offer.id).all()
    return render_template('admin/offers.html', offers=offers)


@app.route('/admin/offers/add', methods=['POST'])
@admin_required
def admin_offers_add():
    """Add new offer"""
    title = request.form.get('title')
    description = request.form.get('description')
    display_order = int(request.form.get('display_order', 0))
    is_active = request.form.get('is_active') == 'on'
    
    offer = Offer(
        title=title,
        description=description,
        display_order=display_order,
        is_active=is_active
    )
    
    db.session.add(offer)
    db.session.commit()
    
    return redirect(url_for('admin_offers'))


@app.route('/admin/offers/<int:offer_id>/edit', methods=['POST'])
@admin_required
def admin_offers_edit(offer_id):
    """Edit offer"""
    offer = Offer.query.get_or_404(offer_id)
    
    offer.title = request.form.get('title')
    offer.description = request.form.get('description')
    offer.display_order = int(request.form.get('display_order', 0))
    offer.is_active = request.form.get('is_active') == 'on'
    offer.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return redirect(url_for('admin_offers'))


@app.route('/admin/offers/<int:offer_id>/delete', methods=['POST'])
@admin_required
def admin_offers_delete(offer_id):
    """Delete offer"""
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    
    return redirect(url_for('admin_offers'))


@app.route('/admin/settings')
@admin_required
def admin_settings():
    """Settings page"""
    settings = {s.key: s.value for s in Setting.query.all()}
    return render_template('admin/settings.html', settings=settings)


@app.route('/admin/settings/update', methods=['POST'])
@admin_required
def admin_settings_update():
    """Update settings"""
    # Handle logo upload
    if 'logo' in request.files:
        file = request.files['logo']
        if file and file.filename:
            # Delete old logo if exists
            old_logo_setting = Setting.query.filter_by(key='shop_logo').first()
            if old_logo_setting and old_logo_setting.value:
                old_logo_path = os.path.join('static/images', old_logo_setting.value)
                if os.path.exists(old_logo_path):
                    os.remove(old_logo_path)
            
            # Save new logo
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            logo_dir = 'static/images'
            os.makedirs(logo_dir, exist_ok=True)
            filepath = os.path.join(logo_dir, filename)
            file.save(filepath)
            
            # Update setting
            logo_setting = Setting.query.filter_by(key='shop_logo').first()
            if logo_setting:
                logo_setting.value = filename
            else:
                logo_setting = Setting(key='shop_logo', value=filename)
                db.session.add(logo_setting)
    
    # Update other settings
    for key in ['shop_name', 'shop_address', 'shop_phone', 'tax_rate', 'gst_rate', 
                'stock_alert_threshold', 'invoice_footer']:
        value = request.form.get(key, '')
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()
    return redirect(url_for('admin_settings'))


if __name__ == '__main__':
    app.run(debug=True)

