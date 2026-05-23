"""
Run with:  python manage.py shell < seed_data.py
Creates sample data so you can test every API endpoint immediately.
"""
import os, django, datetime, decimal
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediswift.settings')
django.setup()

from django.contrib.auth import get_user_model
from doctors.models import Doctor
from delivery.models import DeliveryBoy
from products.models import Category, Product
from appointments.models import Appointment

User = get_user_model()

print("=== Seeding MediSwift Database ===\n")

# ── Users ─────────────────────────────────────────────────────
users_data = [
    dict(email='admin@mediswift.com',    name='Admin User',        role='admin',    password='Admin@123'),
    dict(email='doctor1@mediswift.com',  name='Dr. Priya Sharma',  role='doctor',   password='Doctor@123'),
    dict(email='doctor2@mediswift.com',  name='Dr. Rahul Mehta',   role='doctor',   password='Doctor@123'),
    dict(email='patient1@mediswift.com', name='Amit Kumar',        role='patient',  password='Patient@123'),
    dict(email='patient2@mediswift.com', name='Sneha Singh',       role='patient',  password='Patient@123'),
    dict(email='delivery1@mediswift.com',name='Ravi Delivery',     role='delivery', password='Delivery@123'),
]

created_users = {}
for u in users_data:
    if not User.objects.filter(email=u['email']).exists():
        phone = '9' + u['name'][:9].replace(' ','').replace('.','').ljust(9,'0')[:9]
        user = User.objects.create_user(
            email=u['email'], name=u['name'],
            password=u['password'], role=u['role'],
            phone=phone[:15]
        )
        if u['role'] == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            created_users[u['role'] + '_' + u['name'].split()[0].lower()] = user
            print(f"  ✅ User created: {u['email']}")
        else:
            user = User.objects.get(email=u['email'])
            created_users[u['role'] + '_' + u['name'].split()[0].lower()] = user
            print(f"  ℹ️  User exists:  {u['email']}")

# ── Doctors ───────────────────────────────────────────────────
print("\n--- Doctors ---")
doctors_data = [
    dict(user_email='doctor1@mediswift.com', specialization='Cardiology',
         experience_years=8, clinic_address='123 Health St, Kanpur',
         clinic_phone='5123456789', consultation_fee=500, availability_status='Available',
         bio='Experienced cardiologist with 8 years of practice.'),
    dict(user_email='doctor2@mediswift.com', specialization='General Medicine',
         experience_years=12, clinic_address='456 Medical Ave, Kanpur',
         clinic_phone='5187654321', consultation_fee=400, availability_status='Available',
         bio='General practitioner with 12 years of experience.'),
]
for d in doctors_data:
    u = User.objects.get(email=d.pop('user_email'))
    if not Doctor.objects.filter(user=u).exists():
        doc = Doctor.objects.create(user=u, **d)
        print(f"  ✅ Doctor: {doc.name}")
    else:
        print(f"  ℹ️  Doctor exists: {u.email}")

# ── Delivery Boys ─────────────────────────────────────────────
print("\n--- Delivery Boys ---")
u = User.objects.get(email='delivery1@mediswift.com')
if not DeliveryBoy.objects.filter(user=u).exists():
    db = DeliveryBoy.objects.create(
        user=u, name='Ravi Delivery', phone='9876543210',
        vehicle_number='UP32AB1234', service_area='Kanpur Central, Govind Nagar'
    )
    print(f"  ✅ Delivery Boy: {db.name}")
else:
    print("  ℹ️  Delivery boy exists")

# ── Categories ────────────────────────────────────────────────
print("\n--- Categories ---")
categories = [
    ('medicines',    'Medicines',         '💊'),
    ('wellness',     'Health & Wellness',  '🌿'),
    ('equipment',    'Medical Equipment', '🩺'),
    ('skincare',     'Skin Care',         '✨'),
    ('vitamins',     'Vitamins & Supplements', '💪'),
    ('first_aid',    'First Aid',         '🩹'),
]
cat_objects = {}
for name, display, icon in categories:
    cat, created = Category.objects.get_or_create(name=name, defaults={'display_name': display, 'icon': icon})
    cat_objects[name] = cat
    print(f"  {'✅' if created else 'ℹ️ '} Category: {display}")

# ── Products ──────────────────────────────────────────────────
print("\n--- Products ---")
products_data = [
    dict(name='Paracetamol 500mg', price=25, category='medicines', manufacturer='Cipla',
         stock=200, prescription_required=False, discount_percent=10,
         description='Relieves mild to moderate pain and reduces fever.',
         expiry_date=datetime.date(2027, 6, 30)),
    dict(name='Amoxicillin 500mg', price=120, category='medicines', manufacturer='Sun Pharma',
         stock=80, prescription_required=True, discount_percent=0,
         description='Antibiotic used to treat bacterial infections.',
         expiry_date=datetime.date(2026, 12, 31)),
    dict(name='Cetirizine 10mg', price=35, category='medicines', manufacturer='Dr. Reddy\'s',
         stock=150, prescription_required=False, discount_percent=5,
         description='Antihistamine for allergy relief.',
         expiry_date=datetime.date(2027, 3, 31)),
    dict(name='Multivitamin Capsules', price=299, category='vitamins', manufacturer='HealthVit',
         stock=120, prescription_required=False, discount_percent=15,
         description='Daily multivitamin for overall health.',
         expiry_date=datetime.date(2027, 8, 31)),
    dict(name='Digital Thermometer', price=199, category='equipment', manufacturer='Dr. Trust',
         stock=50, prescription_required=False, discount_percent=0,
         description='Fast and accurate digital thermometer.'),
    dict(name='Blood Pressure Monitor', price=1499, category='equipment', manufacturer='Omron',
         stock=30, prescription_required=False, discount_percent=10,
         description='Automatic BP monitor for home use.'),
    dict(name='Band Aid Strips', price=45, category='first_aid', manufacturer='3M',
         stock=300, prescription_required=False, discount_percent=0,
         description='Flexible fabric adhesive bandages.'),
    dict(name='Hand Sanitizer 500ml', price=149, category='wellness', manufacturer='Dettol',
         stock=200, prescription_required=False, discount_percent=5,
         description='Kills 99.9% of germs instantly.'),
    dict(name='Vitamin C 1000mg', price=199, category='vitamins', manufacturer='Himalaya',
         stock=100, prescription_required=False, discount_percent=10,
         description='Boosts immunity and acts as antioxidant.',
         expiry_date=datetime.date(2027, 1, 31)),
    dict(name='Moisturizing Face Wash', price=189, category='skincare', manufacturer='Cetaphil',
         stock=90, prescription_required=False, discount_percent=8,
         description='Gentle face wash for sensitive skin.'),
]
for pd in products_data:
    cat_name = pd.pop('category')
    if not Product.objects.filter(name=pd['name']).exists():
        p = Product.objects.create(category=cat_objects[cat_name], **pd)
        print(f"  ✅ Product: {p.name}")
    else:
        print(f"  ℹ️  Product exists: {pd['name']}")

# ── Sample Appointment ────────────────────────────────────────
print("\n--- Appointments ---")
patient = User.objects.get(email='patient1@mediswift.com')
doc = Doctor.objects.first()
if doc and not Appointment.objects.filter(patient=patient, doctor=doc).exists():
    appt = Appointment.objects.create(
        doctor=doc, patient=patient,
        patient_name=patient.name,
        patient_mobile='9876543210',
        appointment_date=datetime.date.today() + datetime.timedelta(days=2),
        appointment_time='10:00',
        status='Pending'
    )
    print(f"  ✅ Appointment: {appt.booking_ref}")
else:
    print("  ℹ️  Appointment exists or no doctor found")

print("\n=== Seed Complete! ===")
print("\n📋 LOGIN CREDENTIALS:")
print("┌─────────────────────────────────────────────────┐")
print("│  Role      │ Email                  │ Password   │")
print("├─────────────────────────────────────────────────┤")
print("│  Admin     │ admin@mediswift.com     │ Admin@123  │")
print("│  Doctor    │ doctor1@mediswift.com   │ Doctor@123 │")
print("│  Doctor    │ doctor2@mediswift.com   │ Doctor@123 │")
print("│  Patient   │ patient1@mediswift.com  │ Patient@123│")
print("│  Patient   │ patient2@mediswift.com  │ Patient@123│")
print("│  Delivery  │ delivery1@mediswift.com │Delivery@123│")
print("└─────────────────────────────────────────────────┘")
