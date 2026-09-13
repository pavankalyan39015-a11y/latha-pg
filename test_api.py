from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_and_health():
    res = client.get("/", follow_redirects=False)
    assert res.status_code in [200, 307, 302]

    res_dash = client.get("/dashboard/")
    assert res_dash.status_code == 200
    assert "PG Manager Pro" in res_dash.text

    res_h = client.get("/health")
    assert res_h.status_code == 200
    assert res_h.json()["status"] == "healthy"
    print(" [PASS] Root redirect, Web Dashboard HTML & Health endpoints")

def test_dashboard_summary():
    res = client.get("/api/v1/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_rooms" in data
    assert "total_beds" in data
    assert "occupied_beds" in data
    assert "available_beds" in data
    assert "active_tenants" in data
    assert "total_outstanding_dues" in data
    assert data["total_rooms"] >= 5
    assert data["total_beds"] >= 11
    print(f" [PASS] Executive Dashboard: {data['total_beds']} beds, {data['occupied_beds']} occupied, Rs. {data['total_outstanding_dues']} dues")

def test_list_rooms():
    res = client.get("/api/v1/rooms")
    assert res.status_code == 200
    rooms = res.json()
    assert len(rooms) >= 5
    assert any(r["room_number"] == "101" for r in rooms)
    print(f" [PASS] Rooms API: returned {len(rooms)} rooms")

def test_available_beds():
    res = client.get("/api/v1/rooms/beds/available")
    assert res.status_code == 200
    beds = res.json()
    assert len(beds) > 0
    assert all(b["status"] == "AVAILABLE" for b in beds)
    print(f" [PASS] Beds API: {len(beds)} available beds found")

def test_list_tenants():
    res = client.get("/api/v1/tenants")
    assert res.status_code == 200
    tenants = res.json()
    assert len(tenants) >= 5
    assert any("Rahul" in t["full_name"] for t in tenants)
    print(f" [PASS] Tenants API: {len(tenants)} tenants loaded")

def test_tenant_dues():
    res = client.get("/api/v1/billing/tenants/1/dues")
    assert res.status_code == 200
    dues = res.json()
    assert dues["tenant_id"] == 1
    assert "outstanding_dues" in dues
    print(f" [PASS] Billing API: Tenant 1 dues = Rs. {dues['outstanding_dues']}")

def test_maintenance_tickets():
    res = client.get("/api/v1/complaints")
    assert res.status_code == 200
    tickets = res.json()
    assert len(tickets) >= 3
    print(f" [PASS] Complaints API: {len(tickets)} tickets tracked")

def test_meal_menu_and_headcount():
    res = client.get("/api/v1/meals/menu?day=Monday")
    assert res.status_code == 200
    menu = res.json()
    assert len(menu) >= 3

    res_hc = client.get("/api/v1/meals/headcount?meal_type=DINNER")
    assert res_hc.status_code == 200
    headcount = res_hc.json()
    assert headcount["attending_count"] > 0
    print(f" [PASS] Meals API: Headcount for dinner = {headcount['attending_count']} attendees")

def test_auto_invoice_settlement():
    # Tenant 4 has unpaid invoice 4 for 6900.0
    res_before = client.get("/api/v1/billing/invoices/4")
    assert res_before.status_code == 200
    assert res_before.json()["status"] == "UNPAID"

    # Make payment without specifying invoice_id
    res_pay = client.post("/api/v1/billing/payments", json={
        "tenant_id": 4,
        "amount": 6900.0,
        "payment_method": "UPI",
        "transaction_reference": "UPI-TEST-AUTO-SETTLE"
    })
    assert res_pay.status_code == 201
    pay_data = res_pay.json()
    assert pay_data["invoice_id"] == 4

    # Verify invoice 4 is now PAID
    res_after = client.get("/api/v1/billing/invoices/4")
    assert res_after.status_code == 200
    assert res_after.json()["status"] == "PAID"
    assert res_after.json()["paid_amount"] == 6900.0
    print(" [PASS] Auto Invoice Settlement: Unpaid invoice automatically settled via general payment")

def test_invoice_patch():
    # Update notes and discount on invoice 3
    res_patch = client.patch("/api/v1/billing/invoices/3", json={
        "notes": "Updated notes via PATCH",
        "discount": 500.0
    })
    assert res_patch.status_code == 200
    inv = res_patch.json()
    assert inv["notes"] == "Updated notes via PATCH"
    assert inv["discount"] == 500.0
    print(f" [PASS] Invoice PATCH: Successfully updated invoice total to Rs. {inv['total_amount']}")

def test_bed_validation_and_deletion():
    # Find maintenance bed (202-B)
    res_rooms = client.get("/api/v1/rooms")
    m_bed = None
    occ_bed = None
    for r in res_rooms.json():
        for b in r["beds"]:
            if b["status"] == "MAINTENANCE":
                m_bed = b
            elif b["status"] == "OCCUPIED":
                occ_bed = b

    # Attempt to onboard tenant to MAINTENANCE bed -> Should fail with 400
    if m_bed:
        res_fail = client.post("/api/v1/tenants/onboard", json={
            "full_name": "Invalid Bed Test",
            "phone": "9999988888",
            "bed_id": m_bed["id"]
        })
        assert res_fail.status_code == 400
        assert "not available" in res_fail.json()["detail"]
        print(" [PASS] Bed Allocation Validation: Prevented assigning MAINTENANCE bed")

    # Attempt to delete occupied bed -> Should fail with 400
    if occ_bed:
        res_del_occ = client.delete(f"/api/v1/rooms/beds/{occ_bed['id']}")
        assert res_del_occ.status_code == 400
        assert "occupied" in res_del_occ.json()["detail"]
        print(" [PASS] Bed Deletion Safety: Prevented deleting OCCUPIED bed")

    # Add extra bed to room 1, then delete it
    res_add = client.post("/api/v1/rooms/1/beds", json={"bed_number": "101-TEST", "status": "AVAILABLE"})
    assert res_add.status_code == 201
    new_bed_id = res_add.json()["id"]

    res_del = client.delete(f"/api/v1/rooms/beds/{new_bed_id}")
    assert res_del.status_code == 204
    print(" [PASS] Bed Lifecycle: Successfully created and deleted unoccupied bed slot")

def test_tenant_lifecycle_and_delete():
    # 1. Onboard temporary tenant
    res_avail = client.get("/api/v1/rooms/beds/available")
    avail_beds = res_avail.json()
    assert len(avail_beds) > 0
    target_bed = avail_beds[0]

    res_onb = client.post("/api/v1/tenants/onboard", json={
        "full_name": "Temporary Test Guest",
        "phone": "9911223344",
        "bed_id": target_bed["id"]
    })
    assert res_onb.status_code == 201
    temp_tenant_id = res_onb.json()["id"]

    # 2. Bed should now be OCCUPIED
    res_rooms = client.get("/api/v1/rooms")
    bed_check = next(b for r in res_rooms.json() for b in r["beds"] if b["id"] == target_bed["id"])
    assert bed_check["status"] == "OCCUPIED"

    # 3. Delete temporary tenant
    res_del = client.delete(f"/api/v1/tenants/{temp_tenant_id}")
    assert res_del.status_code == 204

    # 4. Bed should be restored to AVAILABLE
    res_rooms_after = client.get("/api/v1/rooms")
    bed_restored = next(b for r in res_rooms_after.json() for b in r["beds"] if b["id"] == target_bed["id"])
    assert bed_restored["status"] == "AVAILABLE"
    print(" [PASS] Tenant Delete & Bed Release: Tenant removed and bed restored to AVAILABLE")

if __name__ == "__main__":
    print("\n--- RUNNING API INTEGRATION TESTS ---")
    test_root_and_health()
    test_dashboard_summary()
    test_list_rooms()
    test_available_beds()
    test_list_tenants()
    test_tenant_dues()
    test_auto_invoice_settlement()
    test_invoice_patch()
    test_bed_validation_and_deletion()
    test_tenant_lifecycle_and_delete()
    test_maintenance_tickets()
    test_meal_menu_and_headcount()
    print("\n--- ALL TESTS PASSED SUCCESSFULLY! ---\n")

