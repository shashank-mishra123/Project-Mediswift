# 🏥 MediSwift — Django REST API

MediSwift is a comprehensive healthcare backend API built with Django REST Framework and SQLite. It features role-based authentication, advanced ORM queries, custom business logic, and a complete e-commerce system for medical products.

---

## 📁 Project Structure

```
mediswift/
├── mediswift/          # Project configuration and main URLs
├── users/              # Custom user model, JWT authentication, role-based permissions
├── doctors/            # Doctor profiles, likes, and personalized dashboards
├── appointments/       # Appointment booking with conflict detection and scheduling
├── products/           # Product catalog with categories, advanced filtering, and recommendations
├── orders/             # Shopping cart, order management, and transaction handling
├── delivery/           # Delivery boy management and order tracking
├── seed_data.py        # Sample data loader for testing all features
├── requirements.txt    # Python dependencies
└── mediswift.sqlite3   # SQLite database (created automatically)
```

---

## 🚀 Quick Start for Fresh Django Developers

### 1. Environment Setup
```bash
# Clone or download the project
cd mediswift

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Load sample data for testing
python manage.py shell < seed_data.py

# Start the development server
python manage.py runserver
```

### 2. Test the API
```bash
# Base URL for all API calls
BASE_URL="http://127.0.0.1:8000/api"

# Login as a patient
curl -X POST $BASE_URL/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"patient1@mediswift.com","password":"Patient@123"}'

# Use the access token for authenticated requests
TOKEN="your_access_token_here"
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/products/
```

---

## 🔑 Authentication & User Management

### JWT Authentication
MediSwift uses JSON Web Tokens for secure authentication. All protected endpoints require a Bearer token.

```http
Authorization: Bearer <access_token>
```

### User Roles
- **Admin**: Full system access, user management, analytics
- **Doctor**: Profile management, appointment handling, patient interactions
- **Patient**: Browse products/doctors, book appointments, place orders, like items
- **Delivery**: Order delivery management and status updates

### Authentication Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/api/auth/register/` | Register new patient account | Public |
| POST | `/api/auth/login/` | Obtain JWT tokens | Public |
| POST | `/api/auth/token/refresh/` | Refresh access token | Public |
| POST | `/api/auth/logout/` | Logout (client-side) | Authenticated |
| GET | `/api/auth/me/` | Get current user profile | Authenticated |
| PUT | `/api/auth/change-password/` | Change password | Authenticated |

---

## 👤 User Management & Dashboards

### Patient Dashboard
```http
GET /api/patient/dashboard/
Authorization: Bearer <token>
```
**Features:**
- Order statistics and history
- Appointment tracking
- Liked doctors and products count
- Recent activity summary

### Admin Dashboard
```http
GET /api/admin/stats/
Authorization: Bearer <admin_token>
```
**Features:**
- User statistics by role
- Order and appointment analytics
- Product inventory status
- Recent activity (last 7 days)

---

## 👨‍⚕️ Doctor Management

### Public Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/doctors/` | List active doctors with filtering | Public |
| GET | `/api/doctors/<id>/` | Doctor details | Public |
| POST | `/api/doctors/<id>/like/` | Like a doctor | Patient |
| DELETE | `/api/doctors/<id>/like/` | Unlike a doctor | Patient |
| GET | `/api/doctors/<id>/likes/` | Get likes count | Public |

### Doctor-Specific Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/doctors/my-profile/` | Doctor's own profile | Doctor |
| PUT | `/api/doctors/my-profile/` | Update profile | Doctor |
| GET | `/api/doctor/dashboard/` | Personalized dashboard | Doctor |

### Doctor Dashboard Features
- Today's appointments schedule
- Upcoming appointments (next 7 days)
- Monthly performance statistics
- Profile completion percentage
- Appointment status breakdown

### Admin Doctor Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/admin/doctors/` | List all doctors | Admin |
| POST | `/api/admin/doctors/` | Create doctor | Admin |
| GET | `/api/admin/doctors/<id>/` | Doctor details | Admin |
| PUT | `/api/admin/doctors/<id>/` | Update doctor | Admin |
| DELETE | `/api/admin/doctors/<id>/` | Delete doctor | Admin |
| PATCH | `/api/admin/doctors/<id>/status/` | Change status | Admin |

---

## 📅 Appointment System

### Booking & Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/api/appointments/` | Book appointment | Patient |
| GET | `/api/appointments/my/` | Patient's appointments | Patient |
| GET | `/api/appointments/<id>/` | Appointment details | Owner/Admin |
| PUT | `/api/appointments/<id>/` | Update appointment | Owner/Admin |
| DELETE | `/api/appointments/<id>/` | Delete appointment | Owner/Admin |
| PATCH | `/api/appointments/<id>/cancel/` | Cancel appointment | Patient |

### Doctor Appointment Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/doctor/appointments/` | Doctor's schedule | Doctor |
| PATCH | `/api/doctor/appointments/<id>/status/` | Update status | Doctor |

### Public Utilities
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/appointments/booked-slots/` | Check available slots | Public |

### Admin Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/admin/appointments/` | All appointments | Admin |
| GET | `/api/admin/appointments/<id>/` | Appointment details | Admin |
| PUT | `/api/admin/appointments/<id>/` | Update appointment | Admin |
| DELETE | `/api/admin/appointments/<id>/` | Delete appointment | Admin |

---

## 🛒 Product Catalog & E-commerce

### Public Product Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/categories/` | List all categories | Public |
| GET | `/api/products/` | List products with advanced filtering | Public |
| GET | `/api/products/<id>/` | Product details | Public |
| POST | `/api/products/<id>/like/` | Like product | Patient |
| DELETE | `/api/products/<id>/like/` | Unlike product | Patient |
| GET | `/api/products/<id>/likes/` | Get likes count | Public |
| GET | `/api/products/recommendations/` | Get recommendations | Public |
| GET | `/api/products/<id>/similar/` | Similar products | Public |

### Advanced Product Filtering
```http
GET /api/products/?category=medicines&min_price=10&max_price=100&search=paracetamol&sort_by=price&sort_order=asc
```

**Available Filters:**
- `category`: Filter by category name
- `subcategory`: Filter by subcategory
- `search`: Search in name, description, manufacturer
- `min_price`, `max_price`: Price range
- `manufacturer`: Filter by manufacturer
- `prescription_required`: true/false
- `in_stock`: true/false (show only in-stock items)
- `discount_only`: true/false (show only discounted items)
- `rating_min`: Minimum rating
- `sort_by`: name, price, rating, popularity, newest
- `sort_order`: asc, desc

### Shopping Cart
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/cart/` | View cart items | Patient |
| POST | `/api/cart/add/` | Add item to cart | Patient |
| PUT | `/api/cart/<id>/` | Update item quantity | Patient |
| DELETE | `/api/cart/<id>/` | Remove item from cart | Patient |
| DELETE | `/api/cart/clear/` | Clear entire cart | Patient |

### Order Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/api/orders/` | Place order from cart | Patient |
| GET | `/api/orders/my/` | User's order history | Patient |
| GET | `/api/orders/<id>/` | Order details | Patient |
| PATCH | `/api/orders/<id>/cancel/` | Cancel order | Patient |

### Admin Product Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/admin/categories/` | List categories | Admin |
| POST | `/api/admin/categories/` | Create category | Admin |
| GET | `/api/admin/categories/<id>/` | Category details | Admin |
| PUT | `/api/admin/categories/<id>/` | Update category | Admin |
| DELETE | `/api/admin/categories/<id>/` | Delete category | Admin |
| GET | `/api/admin/products/` | List products | Admin |
| POST | `/api/admin/products/` | Create product | Admin |
| GET | `/api/admin/products/<id>/` | Product details | Admin |
| PUT | `/api/admin/products/<id>/` | Update product | Admin |
| DELETE | `/api/admin/products/<id>/` | Delete product | Admin |
| GET | `/api/admin/products/low-stock/` | Low stock alerts | Admin |
| GET | `/api/admin/products/near-expiry/` | Near expiry alerts | Admin |

### Admin Order Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/admin/orders/` | All orders | Admin |
| GET | `/api/admin/orders/<id>/` | Order details | Admin |
| PUT | `/api/admin/orders/<id>/` | Update order | Admin |
| DELETE | `/api/admin/orders/<id>/` | Delete order | Admin |
| PATCH | `/api/admin/orders/<id>/status/` | Update order status | Admin |
| GET | `/api/admin/orders/stats/` | Order statistics | Admin |

---

## 🚚 Delivery Management

### Delivery Boy Endpoints
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/delivery/my-profile/` | Delivery profile | Delivery |
| PUT | `/api/delivery/my-profile/` | Update profile | Delivery |
| GET | `/api/delivery/my-orders/` | Assigned orders | Delivery |
| PATCH | `/api/delivery/my-status/` | Update availability | Delivery |
| PATCH | `/api/delivery/orders/<id>/delivered/` | Mark order delivered | Delivery |
| GET | `/api/delivery/dashboard/` | Performance dashboard | Delivery |

### Admin Delivery Management
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/admin/delivery/` | List delivery boys | Admin |
| POST | `/api/admin/delivery/` | Create delivery boy | Admin |
| GET | `/api/admin/delivery/<id>/` | Delivery boy details | Admin |
| PUT | `/api/admin/delivery/<id>/` | Update delivery boy | Admin |
| DELETE | `/api/admin/delivery/<id>/` | Delete delivery boy | Admin |
| GET | `/api/admin/delivery/available/` | Available delivery boys | Admin |

---

## 🧠 Custom Business Logic & ORM Features

### Enhanced Models with Custom Methods

#### User Model Custom Methods
```python
# Role checking
user.is_patient()  # Returns True if role == 'patient'
user.is_doctor()   # Returns True if role == 'doctor'
user.is_admin()    # Returns True if role == 'admin'

# Status management
user.activate()    # Set status to 'active'
user.deactivate()  # Set status to 'inactive'
user.suspend()     # Set status to 'suspended'

# Activity properties
user.total_orders        # Count of user's orders
user.total_appointments  # Count of user's appointments
user.liked_doctors_count # Count of liked doctors
user.liked_products_count # Count of liked products
```

#### Doctor Model Custom Methods
```python
# Statistics
doctor.total_appointments      # Total appointments
doctor.pending_appointments    # Pending appointments
doctor.completed_appointments  # Completed appointments
doctor.likes_count            # Number of likes

# Schedule management
doctor.get_upcoming_appointments(limit=5)  # Next appointments
doctor.get_today_appointments()            # Today's schedule
doctor.get_monthly_stats(year, month)      # Monthly performance
```

#### Product Model Custom Methods
```python
# Stock management
product.is_in_stock           # Boolean: stock > 0
product.stock_status          # "In Stock", "Low Stock", "Out of Stock"
product.reduce_stock(quantity) # Decrease stock
product.increase_stock(quantity) # Increase stock

# Pricing
product.discounted_price      # Price after discount

# Recommendations
Product.get_popular_products(limit=10)     # Most liked products
Product.get_low_stock_products(threshold=10) # Low stock items
Product.get_near_expiry_products(days=90)  # Near expiry items
product.get_similar_products(limit=5)      # Similar category products
```

#### Appointment Model Custom Methods
```python
# Status checking
appointment.is_upcoming       # Boolean: date >= today
appointment.is_today          # Boolean: date == today
appointment.can_cancel        # Boolean: can be cancelled
appointment.can_reschedule    # Boolean: can be rescheduled

# Actions
appointment.cancel()          # Cancel appointment
appointment.confirm()         # Confirm appointment
appointment.complete()        # Mark as completed

# Class methods
Appointment.get_today_appointments()       # All today's appointments
Appointment.get_upcoming_appointments(days=7) # Future appointments
Appointment.get_doctor_schedule(doctor, date) # Doctor's schedule
```

#### Order Model Custom Methods
```python
# Properties
order.items_count             # Number of items
order.total_quantity          # Total quantity
order.can_cancel              # Boolean: can be cancelled
order.can_ship                # Boolean: can be shipped
order.is_delivered            # Boolean: delivered

# Actions
order.cancel()                # Cancel and restore stock
order.confirm()               # Confirm order
order.ship(delivery_boy)      # Mark as out for delivery
order.deliver()               # Mark as delivered

# Class methods
Order.get_pending_orders()    # All pending orders
Order.get_orders_by_status(status) # Orders by status
Order.get_monthly_revenue(year, month) # Monthly revenue
```

#### DeliveryBoy Model Custom Methods
```python
# Status
delivery_boy.is_available     # Boolean: status == 'available'
delivery_boy.current_deliveries # Current assignments count

# Actions
delivery_boy.set_available()  # Set status to available
delivery_boy.set_busy()       # Set status to busy
delivery_boy.set_offline()    # Set status to offline
delivery_boy.assign_order(order) # Assign order to delivery
delivery_boy.complete_delivery(order) # Mark delivery complete

# Class methods
DeliveryBoy.get_available_boys() # Available delivery boys
DeliveryBoy.get_top_performers(limit=10) # Top performers
```

### Advanced Query Optimizations

#### Select Related & Prefetch Related
```python
# Efficiently load related data
cart_items = Cart.objects.filter(user=request.user).select_related('product')
orders = Order.objects.filter(user=request.user).prefetch_related('items')
```

#### Complex Filtering with Q Objects
```python
# Advanced product search
products = Product.objects.filter(
    Q(name__icontains=search) |
    Q(description__icontains=search) |
    Q(manufacturer__icontains=search)
)
```

#### Database Annotations
```python
# Add computed fields
popular_products = Product.objects.annotate(
    likes_count=Count('liked_by')
).order_by('-likes_count')
```

#### Transaction Management
```python
# Atomic operations for data consistency
@transaction.atomic
def place_order(request):
    # Stock checking and order creation
    # All operations succeed or all fail
```

---

## 🧪 Testing Examples

### 1. User Registration & Authentication
```bash
# Register a new patient
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "Test@123",
    "phone": "9876543210"
  }'

# Login and get tokens
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient1@mediswift.com",
    "password": "Patient@123"
  }'
# Response includes: access_token, refresh_token, user data
```

### 2. Product Browsing & Filtering
```bash
# Get all products
curl http://127.0.0.1:8000/api/products/

# Filter by category and price
curl "http://127.0.0.1:8000/api/products/?category=medicines&min_price=10&max_price=100"

# Search products
curl "http://127.0.0.1:8000/api/products/?search=paracetamol"

# Get product recommendations
curl http://127.0.0.1:8000/api/products/recommendations/
```

### 3. Shopping Cart & Orders
```bash
# Add item to cart (requires authentication)
curl -X POST http://127.0.0.1:8000/api/cart/add/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# View cart
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/cart/

# Place order
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address": "123 Main St, City, State 12345"}'
```

### 4. Appointment Booking
```bash
# Check booked slots
curl "http://127.0.0.1:8000/api/appointments/booked-slots/?doctor_id=1&date=2024-12-25"

# Book appointment
curl -X POST http://127.0.0.1:8000/api/appointments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 1,
    "appointment_date": "2024-12-25",
    "appointment_time": "10:00",
    "notes": "Regular checkup"
  }'
```

### 5. Doctor Dashboard
```bash
# Get doctor's personalized dashboard
curl -H "Authorization: Bearer <doctor_token>" http://127.0.0.1:8000/api/doctor/dashboard/
```

### 6. Admin Analytics
```bash
# Get comprehensive admin statistics
curl -H "Authorization: Bearer <admin_token>" http://127.0.0.1:8000/api/admin/stats/
```

---

## 🔐 Sample Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@mediswift.com | Admin@123 |
| Doctor | doctor1@mediswift.com | Doctor@123 |
| Doctor | doctor2@mediswift.com | Doctor@123 |
| Patient | patient1@mediswift.com | Patient@123 |
| Patient | patient2@mediswift.com | Patient@123 |
| Delivery | delivery1@mediswift.com | Delivery@123 |

---

## 📚 Learning Guide for Fresh Django Developers

### 1. **Understanding Django ORM**
- **Models**: Define data structure and relationships
- **Managers**: Custom query methods (e.g., `get_popular_products()`)
- **Properties**: Computed fields (e.g., `discounted_price`)
- **Methods**: Business logic (e.g., `cancel()`, `confirm()`)

### 2. **DRF Best Practices**
- **Serializers**: Data validation and transformation
- **Permissions**: Role-based access control
- **Views**: HTTP method handling and business logic
- **URLs**: Clean endpoint organization

### 3. **Custom Logic Patterns**
- **Model Methods**: Keep business logic in models
- **View Logic**: Handle HTTP concerns in views
- **Utility Functions**: Shared logic in separate modules
- **Signals**: Automated actions on model changes

### 4. **Database Optimization**
- **Select Related**: Foreign key optimization
- **Prefetch Related**: Many-to-many optimization
- **Annotations**: Computed database fields
- **Indexes**: Performance optimization

### 5. **Security Considerations**
- **Permissions**: Proper access control
- **Validation**: Input sanitization
- **Transactions**: Data consistency
- **JWT**: Secure authentication

### 6. **API Design Principles**
- **RESTful**: Standard HTTP methods
- **Consistent**: Uniform response format
- **Documented**: Clear endpoint documentation
- **Versioned**: Future-proof API design

---

## 🚀 Next Steps

1. **Explore the Codebase**: Start with `models.py` files to understand data structure
2. **Test Endpoints**: Use the provided curl examples to test functionality
3. **Add Features**: Extend existing models with new fields and methods
4. **Write Tests**: Add unit tests for models and API endpoints
5. **Optimize Queries**: Use Django Debug Toolbar to identify slow queries
6. **Add Frontend**: Build a React/Vue frontend to consume the API

---

## 📞 Support

This project demonstrates advanced Django ORM usage, DRF implementation, and scalable API design patterns. Each app is self-contained with proper separation of concerns, making it easy to understand and extend.

For any questions or issues, please reach out to the project maintainer at 
