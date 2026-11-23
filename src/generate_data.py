import json
import os
import random
from datetime import date, timedelta

random.seed(42)

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CLINICS = ["Balwyn", "Mornington", "Geelong", "Berwick"]
DIRTY_CLINICS = {
    "Balwyn": ["balwyn", "DB Balwyn", "BALWYN "],
    "Mornington": ["mornington", "DB Mornington"],
    "Geelong": ["GEELONG", "Geelong Clinic"],
    "Berwick": ["berwick", "DB Berwick"],
}

SERVICES = {
    "Smile Discovery Session": (0, 0),
    "Porcelain Veneers": (6000, 18000),
    "Invisalign": (4500, 8500),
    "Dental Implants": (4000, 12000),
    "Sleep Dentistry": (1200, 3500),
    "General Dentistry": (250, 900),
}

PAID_SERVICES = [s for s in SERVICES if s != "Smile Discovery Session"]
PAYMENT_METHODS = ["Upfront Card", "Private Health Fund", "3rd-Party Payment Plan"]
CLINICIANS = [f"CLN-{i:03d}" for i in range(1, 17)]


def maybe_dirty_clinic(clinic_name: str) -> str:
    # Bug 3: ~5% inconsistent clinic naming
    if random.random() < 0.05:
        return random.choice(DIRTY_CLINICS[clinic_name])
    return clinic_name


def generate():
    start_date = date.today() - timedelta(days=180)
    appointments = []
    billings = []
    collections = []

    appt_counter = 1000
    bill_counter = 5000
    coll_counter = 9000

    for patient_num in range(1, 1401):
        patient_id = f"PAT-{patient_num:05d}"
        clinic = random.choice(CLINICS)
        first_visit_offset = random.randint(0, 145)
        first_visit_date = start_date + timedelta(days=first_visit_offset)

        # 60% of new patients start with a free Smile Discovery Session
        starts_with_discovery = random.random() < 0.60

        if starts_with_discovery:
            appt_counter += 1
            appt_id = f"APT-{appt_counter}"
            status = random.choices(
                ["Completed", "Cancelled", "No-Show"], weights=[0.82, 0.11, 0.07]
            )[0]

            appointments.append({
                "appointment_id": appt_id,
                "patient_id": patient_id,
                "clinic_name": maybe_dirty_clinic(clinic),
                "clinician_id": random.choice(CLINICIANS),
                "appointment_date": first_visit_date.isoformat(),
                "service_category": "Smile Discovery Session",
                "status": status,
                "is_new_patient": True,
            })

            # ~42% of completed Smile Discovery patients convert to a paid treatment within 30 days
            if status == "Completed" and random.random() < 0.42:
                followup_date = first_visit_date + timedelta(days=random.randint(5, 28))
                if followup_date <= date.today():
                    appt_counter += 1
                    paid_appt_id = f"APT-{appt_counter}"
                    service = random.choices(
                        PAID_SERVICES, weights=[0.30, 0.30, 0.20, 0.10, 0.10]
                    )[0]
                    paid_status = random.choices(
                        ["Completed", "Cancelled", "No-Show"], weights=[0.88, 0.08, 0.04]
                    )[0]

                    appointments.append({
                        "appointment_id": paid_appt_id,
                        "patient_id": patient_id,
                        "clinic_name": maybe_dirty_clinic(clinic),
                        "clinician_id": random.choice(CLINICIANS),
                        "appointment_date": followup_date.isoformat(),
                        "service_category": service,
                        "status": paid_status,
                        "is_new_patient": False,
                    })
        else:
            # Direct booking for a paid service
            appt_counter += 1
            appt_id = f"APT-{appt_counter}"
            service = random.choices(
                PAID_SERVICES, weights=[0.15, 0.20, 0.15, 0.10, 0.40]
            )[0]
            status = random.choices(
                ["Completed", "Cancelled", "No-Show"], weights=[0.85, 0.10, 0.05]
            )[0]

            appointments.append({
                "appointment_id": appt_id,
                "patient_id": patient_id,
                "clinic_name": maybe_dirty_clinic(clinic),
                "clinician_id": random.choice(CLINICIANS),
                "appointment_date": first_visit_date.isoformat(),
                "service_category": service,
                "status": status,
                "is_new_patient": random.random() < 0.35,
            })

    # Generate billings and collections for appointments
    for appt in appointments:
        service = appt["service_category"]
        if service == "Smile Discovery Session":
            continue

        low, high = SERVICES[service]
        is_completed = appt["status"] == "Completed"
        # Bug 2: ~4% of Cancelled/No-Show appointments accidentally get billed
        inject_orphan_billing = (not is_completed) and (random.random() < 0.04)

        if is_completed or inject_orphan_billing:
            bill_counter += 1
            billing_id = f"BIL-{bill_counter}"
            billed_amount = round(random.uniform(low, high), 2)

            billings.append({
                "billing_id": billing_id,
                "appointment_id": appt["appointment_id"],
                "patient_id": appt["patient_id"],
                "clinic_name": appt["clinic_name"],
                "billing_date": appt["appointment_date"],
                "billed_amount_aud": billed_amount,
                "treatment_plan_id": f"TP-{random.randint(100, 999)}",
            })

            # Simulate payment collection (only for genuinely completed treatments)
            if is_completed:
                method = random.choices(
                    PAYMENT_METHODS, weights=[0.35, 0.30, 0.35]
                )[0]
                bill_dt = date.fromisoformat(appt["appointment_date"])

                if method == "Upfront Card":
                    coll_amount = billed_amount
                    lag_days = 0
                elif method == "Private Health Fund":
                    coll_amount = round(billed_amount * random.uniform(0.85, 1.0), 2)
                    lag_days = random.randint(1, 7)
                else:
                    # Payment plans collect an initial deposit first
                    coll_amount = round(billed_amount * random.uniform(0.25, 0.65), 2)
                    lag_days = random.randint(0, 14)

                # Bug 4: ~2% collection anomalies (negative refund or overpayment)
                if random.random() < 0.02:
                    coll_amount = round(-abs(coll_amount * 0.2), 2) if random.random() < 0.5 else round(billed_amount * 1.15, 2)

                coll_counter += 1
                collections.append({
                    "collection_id": f"COL-{coll_counter}",
                    "billing_id": billing_id,
                    "collection_date": (bill_dt + timedelta(days=lag_days)).isoformat(),
                    "collected_amount_aud": coll_amount,
                    "payment_method": method,
                })

    # Bug 1: Inject ~2% duplicate appointment rows to simulate a PMS sync glitch
    duplicates = random.sample(appointments, k=max(1, int(len(appointments) * 0.02)))
    appointments.extend(duplicates)

    datasets = {
        "pms_appointments.json": appointments,
        "pms_billings.json": billings,
        "finance_collections.json": collections,
    }

    for filename, rows in datasets.items():
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    generate()