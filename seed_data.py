from datetime import date, datetime, timedelta
from app.database import engine, SessionLocal, Base
import app.models
from app.models.room import Room, Bed
from app.models.tenant import Tenant, TenantDocument
from app.models.billing import Invoice, Payment
from app.models.maintenance import MaintenanceTicket
from app.models.meal import MealMenu, MealAttendance

def seed_database(force: bool = False):
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if not force:
            existing_room = db.query(Room).first()
            if existing_room:
                print("Database already contains records. Skipping seed.")
                return

        if force:
            print("Force flag set: Recreating tables...")
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)

        print("Seeding Latha PG Rooms and Beds...")
        # Rooms according to banner: 2, 3, 4 Sharing with Attached Bathrooms
        amenities_str = "Attached Bathroom, High-Speed Wi-Fi, 24/7 CCTV, Washing Machine, Power Backup"
        r101 = Room(room_number="101", floor=1, room_type="2-Sharing", has_ac=True, has_attached_bathroom=True, base_rent=8500.0, amenities=amenities_str)
        r102 = Room(room_number="102", floor=1, room_type="2-Sharing", has_ac=False, has_attached_bathroom=True, base_rent=7500.0, amenities=amenities_str)
        r201 = Room(room_number="201", floor=2, room_type="3-Sharing", has_ac=True, has_attached_bathroom=True, base_rent=6500.0, amenities=amenities_str)
        r202 = Room(room_number="202", floor=2, room_type="3-Sharing", has_ac=False, has_attached_bathroom=True, base_rent=6000.0, amenities=amenities_str)
        r301 = Room(room_number="301", floor=3, room_type="4-Sharing", has_ac=False, has_attached_bathroom=True, base_rent=5000.0, amenities=amenities_str)

        db.add_all([r101, r102, r201, r202, r301])
        db.commit()

        # Beds (Total 14 beds)
        beds = [
            # Room 101 (2-Sharing)
            Bed(room_id=r101.id, bed_number="101-A", status="OCCUPIED"),
            Bed(room_id=r101.id, bed_number="101-B", status="OCCUPIED"),
            # Room 102 (2-Sharing)
            Bed(room_id=r102.id, bed_number="102-A", status="OCCUPIED"),
            Bed(room_id=r102.id, bed_number="102-B", status="AVAILABLE"),
            # Room 201 (3-Sharing)
            Bed(room_id=r201.id, bed_number="201-A", status="OCCUPIED"),
            Bed(room_id=r201.id, bed_number="201-B", status="OCCUPIED"),
            Bed(room_id=r201.id, bed_number="201-C", status="AVAILABLE"),
            # Room 202 (3-Sharing)
            Bed(room_id=r202.id, bed_number="202-A", status="AVAILABLE"),
            Bed(room_id=r202.id, bed_number="202-B", status="MAINTENANCE"),
            Bed(room_id=r202.id, bed_number="202-C", status="AVAILABLE"),
            # Room 301 (4-Sharing)
            Bed(room_id=r301.id, bed_number="301-A", status="AVAILABLE"),
            Bed(room_id=r301.id, bed_number="301-B", status="AVAILABLE"),
            Bed(room_id=r301.id, bed_number="301-C", status="AVAILABLE"),
            Bed(room_id=r301.id, bed_number="301-D", status="AVAILABLE"),
        ]
        db.add_all(beds)
        db.commit()

        print("Seeding Tenants...")
        t1 = Tenant(
            full_name="Rahul Sharma",
            phone="9876543210",
            email="rahul.sharma@example.com",
            emergency_contact_name="Mahesh Sharma (Father)",
            emergency_contact_phone="9876500001",
            permanent_address="14, Civil Lines, Jaipur, Rajasthan",
            occupation="Software Engineer @ Google",
            id_proof_type="Aadhaar",
            id_proof_number="1234-5678-9012",
            kyc_status="VERIFIED",
            check_in_date=date(2026, 1, 15),
            is_active=True,
            security_deposit=28000.0,
            bed_id=beds[0].id
        )

        t2 = Tenant(
            full_name="Priya Patel",
            phone="9876543211",
            email="priya.patel@example.com",
            emergency_contact_name="Sunita Patel (Mother)",
            emergency_contact_phone="9876500002",
            permanent_address="45 Navrangpura, Ahmedabad, Gujarat",
            occupation="Data Analyst @ Flipkart",
            id_proof_type="Passport",
            id_proof_number="N8765432",
            kyc_status="VERIFIED",
            check_in_date=date(2026, 3, 1),
            is_active=True,
            security_deposit=19000.0,
            bed_id=beds[1].id
        )

        t3 = Tenant(
            full_name="Amit Kumar",
            phone="9876543212",
            email="amit.kumar@example.com",
            emergency_contact_name="Rajesh Kumar (Brother)",
            emergency_contact_phone="9876500003",
            permanent_address="88 Gomti Nagar, Lucknow, UP",
            occupation="Student @ Engineering College",
            id_proof_type="Aadhaar",
            id_proof_number="5678-9012-3456",
            kyc_status="PENDING",
            check_in_date=date(2026, 7, 10),
            is_active=True,
            security_deposit=15000.0,
            bed_id=beds[2].id
        )

        t4 = Tenant(
            full_name="Sneha Rao",
            phone="9876543213",
            email="sneha.rao@example.com",
            emergency_contact_name="Kavita Rao (Mother)",
            emergency_contact_phone="9876500004",
            permanent_address="102 Indiranagar, Bengaluru, Karnataka",
            occupation="UX Designer @ Swiggy",
            id_proof_type="Driving License",
            id_proof_number="KA-03-2022001928",
            kyc_status="VERIFIED",
            check_in_date=date(2026, 5, 20),
            is_active=True,
            security_deposit=13000.0,
            bed_id=beds[4].id
        )

        t5 = Tenant(
            full_name="Rohan Verma",
            phone="9876543214",
            email="rohan.verma@example.com",
            emergency_contact_name="Dinesh Verma (Father)",
            emergency_contact_phone="9876500005",
            permanent_address="32 Model Town, Delhi",
            occupation="Financial Analyst @ Deloitte",
            id_proof_type="Aadhaar",
            id_proof_number="9012-3456-7890",
            kyc_status="VERIFIED",
            check_in_date=date(2026, 8, 1),
            is_active=True,
            security_deposit=13000.0,
            bed_id=beds[5].id
        )

        db.add_all([t1, t2, t3, t4, t5])
        db.commit()

        # KYC Documents
        docs = [
            TenantDocument(tenant_id=t1.id, document_name="Aadhaar Front & Back", document_path_or_url="/uploads/kyc/rahul_aadhaar.pdf"),
            TenantDocument(tenant_id=t1.id, document_name="Company ID Card", document_path_or_url="/uploads/kyc/rahul_company_id.png"),
            TenantDocument(tenant_id=t2.id, document_name="Passport Scan", document_path_or_url="/uploads/kyc/priya_passport.pdf"),
            TenantDocument(tenant_id=t3.id, document_name="College ID Card", document_path_or_url="/uploads/kyc/amit_college_id.jpg"),
        ]
        db.add_all(docs)
        db.commit()

        print("Seeding Billing & Invoices...")
        current_month = "2026-09"
        due_date = date(2026, 9, 5)

        inv1 = Invoice(
            invoice_number="INV-202609-001",
            tenant_id=t1.id,
            billing_month=current_month,
            due_date=due_date,
            rent_amount=14000.0,
            utility_charges=800.0,
            penalty_charges=0.0,
            discount=0.0,
            total_amount=14800.0,
            paid_amount=14800.0,
            status="PAID",
            notes="September Rent + Electricity"
        )

        inv2 = Invoice(
            invoice_number="INV-202609-002",
            tenant_id=t2.id,
            billing_month=current_month,
            due_date=due_date,
            rent_amount=9500.0,
            utility_charges=500.0,
            penalty_charges=0.0,
            discount=0.0,
            total_amount=10000.0,
            paid_amount=10000.0,
            status="PAID",
            notes="September Rent + Maintenance"
        )

        inv3 = Invoice(
            invoice_number="INV-202609-003",
            tenant_id=t3.id,
            billing_month=current_month,
            due_date=due_date,
            rent_amount=9500.0,
            utility_charges=500.0,
            penalty_charges=200.0,
            discount=0.0,
            total_amount=10200.0,
            paid_amount=5000.0,
            status="PARTIAL",
            notes="September Rent (Late fee included, balance due: Rs. 5,200)"
        )

        inv4 = Invoice(
            invoice_number="INV-202609-004",
            tenant_id=t4.id,
            billing_month=current_month,
            due_date=due_date,
            rent_amount=6500.0,
            utility_charges=400.0,
            penalty_charges=0.0,
            discount=0.0,
            total_amount=6900.0,
            paid_amount=0.0,
            status="UNPAID",
            notes="September Rent + Wi-Fi"
        )

        db.add_all([inv1, inv2, inv3, inv4])
        db.commit()

        # Payments
        pay1 = Payment(
            receipt_number="REC-20260901-01",
            invoice_id=inv1.id,
            tenant_id=t1.id,
            amount=14800.0,
            payment_method="UPI",
            transaction_reference="UPI/260901/88921",
            payment_date=datetime(2026, 9, 2, 10, 30),
            notes="Google Pay payment"
        )

        pay2 = Payment(
            receipt_number="REC-20260901-02",
            invoice_id=inv2.id,
            tenant_id=t2.id,
            amount=10000.0,
            payment_method="BANK_TRANSFER",
            transaction_reference="NEFT-HDFC-991823",
            payment_date=datetime(2026, 9, 3, 14, 15),
            notes="Online bank transfer"
        )

        pay3 = Payment(
            receipt_number="REC-20260905-03",
            invoice_id=inv3.id,
            tenant_id=t3.id,
            amount=5000.0,
            payment_method="CASH",
            transaction_reference="CASH-REC-001",
            payment_date=datetime(2026, 9, 5, 18, 0),
            notes="Cash partial deposit handed to manager"
        )

        db.add_all([pay1, pay2, pay3])
        db.commit()

        print("Seeding Maintenance Complaints...")
        tickets = [
            MaintenanceTicket(
                ticket_number="TKT-0902-101",
                tenant_id=t2.id,
                room_id=r102.id,
                category="PLUMBING",
                title="Washroom tap dripping continuously",
                description="The washroom basin tap is dripping water and cannot be shut tightly.",
                priority="HIGH",
                status="IN_PROGRESS",
                reported_at=datetime.utcnow() - timedelta(days=2)
            ),
            MaintenanceTicket(
                ticket_number="TKT-0904-102",
                tenant_id=t4.id,
                room_id=r201.id,
                category="WIFI",
                title="Slow Wi-Fi speed in Room 201",
                description="Wi-Fi signal drops frequently in the corner of Room 201 during evening hours.",
                priority="MEDIUM",
                status="OPEN",
                reported_at=datetime.utcnow() - timedelta(days=1)
            ),
            MaintenanceTicket(
                ticket_number="TKT-0828-103",
                tenant_id=t1.id,
                room_id=r101.id,
                category="APPLIANCE",
                title="AC cooling issue",
                description="AC cooling was low. Technician cleaned filter and refilled gas.",
                priority="LOW",
                status="RESOLVED",
                reported_at=datetime.utcnow() - timedelta(days=14),
                resolved_at=datetime.utcnow() - timedelta(days=12),
                resolution_notes="Filter serviced and gas pressure calibrated."
            )
        ]
        db.add_all(tickets)
        db.commit()

        print("Seeding Mess Menu...")
        menu_items = [
            MealMenu(day_of_week="Monday", meal_type="BREAKFAST", items="Idli, Vada, Sambar, Coconut Chutney, Tea/Coffee"),
            MealMenu(day_of_week="Monday", meal_type="LUNCH", items="Rice, Dal Tadka, Seasonal Veg Sabzi, Roti, Curd, Salad"),
            MealMenu(day_of_week="Monday", meal_type="DINNER", items="Paneer Butter Masala, Roti, Jeera Rice, Dal Makhani, Gulab Jamun", is_special=True),
            MealMenu(day_of_week="Tuesday", meal_type="BREAKFAST", items="Poha, Boiled Eggs / Banana, Mint Chutney, Tea"),
            MealMenu(day_of_week="Tuesday", meal_type="LUNCH", items="Rice, Rajma, Aloo Gobi, Phulka, Pickle"),
            MealMenu(day_of_week="Tuesday", meal_type="DINNER", items="Egg Curry / Kadai Paneer, Chapati, Rice, Dal Fry"),
            MealMenu(day_of_week="Wednesday", meal_type="BREAKFAST", items="Aloo Paratha with Curd, Pickle, Butter, Tea"),
            MealMenu(day_of_week="Wednesday", meal_type="LUNCH", items="Rice, Chana Dal, Bhindi Masala, Roti, Papad"),
            MealMenu(day_of_week="Wednesday", meal_type="DINNER", items="Chicken Biryani / Veg Pulao, Mirchi Ka Salan, Raita", is_special=True),
            MealMenu(day_of_week="Thursday", meal_type="BREAKFAST", items="Upma, Sheera, Coconut Chutney, Coffee"),
            MealMenu(day_of_week="Thursday", meal_type="LUNCH", items="Rice, Moong Dal, Lauki Chana, Phulka, Curd"),
            MealMenu(day_of_week="Thursday", meal_type="DINNER", items="Mix Veg, Dal Tadka, Roti, Steamed Rice"),
            MealMenu(day_of_week="Friday", meal_type="BREAKFAST", items="Masala Dosa, Potato Masala, Sambar, Filter Coffee"),
            MealMenu(day_of_week="Friday", meal_type="LUNCH", items="Curd Rice, Lemon Rice, Potato Roast, Pickle"),
            MealMenu(day_of_week="Friday", meal_type="DINNER", items="Matar Mushroom / Paneer Bhurji, Naan, Rice, Sweet Lassi"),
            MealMenu(day_of_week="Saturday", meal_type="BREAKFAST", items="Puri Bhaji, Halwa, Tea"),
            MealMenu(day_of_week="Saturday", meal_type="LUNCH", items="Khichdi, Kadhi, Papad, Achar, Begun Bhaja"),
            MealMenu(day_of_week="Saturday", meal_type="DINNER", items="Chole Bhature, Onion Salad, Boondi Raita", is_special=True),
            MealMenu(day_of_week="Sunday", meal_type="BREAKFAST", items="Masala Omelette / Bread Butter Jam, Cornflakes, Milk"),
            MealMenu(day_of_week="Sunday", meal_type="LUNCH", items="Special South Indian / North Indian Thali"),
            MealMenu(day_of_week="Sunday", meal_type="DINNER", items="Light Khichdi, Tomato Soup, Fruit Salad"),
        ]
        db.add_all(menu_items)
        db.commit()

        print("Seeding Today's Meal Attendance...")
        today = date.today()
        attendances = [
            MealAttendance(date=today, meal_type="DINNER", tenant_id=t1.id, is_attending=True, wants_packed_meal=False),
            MealAttendance(date=today, meal_type="DINNER", tenant_id=t2.id, is_attending=True, wants_packed_meal=True, feedback="Please pack by 8 PM"),
            MealAttendance(date=today, meal_type="DINNER", tenant_id=t3.id, is_attending=False, feedback="Dining out with friends"),
            MealAttendance(date=today, meal_type="DINNER", tenant_id=t4.id, is_attending=True, wants_packed_meal=False),
            MealAttendance(date=today, meal_type="DINNER", tenant_id=t5.id, is_attending=True, wants_packed_meal=False),
        ]
        db.add_all(attendances)
        db.commit()

        print("Mock data seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
