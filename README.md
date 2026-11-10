# Python Parking Lot ANPR & Dynamic Tariff Billing 🚗🅿️

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

An intelligent Automatic Number Plate Recognition (ANPR) parking management and dynamic tariff billing system. Built in Python for shopping malls, IT parks, airports, and municipal multi-level parking facilities.

---

## 🚀 Key Features

- **Indian License Plate Normalization**: OCR string sanitizer handling varied state plate formats (`MH`, `DL`, `KA`, `UP`, `GJ`, etc.).
- **Tiered Vehicle Classification**: Granular hourly slab tariffs for 2-Wheelers, 4-Wheelers, and Commercial Buses/Vans.
- **Grace Window Handling**: 15-minute free drop-off/pickup pass logic.
- **FASTag & UPI Integration Support**: Real-time cashier exit reconciliation with automated barrier gate trigger.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/shyampandey1104/python-parking-lot-anpr-billing.git
cd python-parking-lot-anpr-billing
pip install -r requirements.txt
```

---

## 🛠️ Usage Example

```python
from parking.engine import SmartParkingEngine

parking = SmartParkingEngine("Airport Terminal Parking")

# Vehicle check-in via ANPR camera
ticket = parking.vehicle_checkin(
    raw_plate="DL 01 AB 8842",
    vehicle_type="FOUR_WHEELER",
    entry_time_str="2026-04-10 14:00:00",
    allocated_bay="B2-10"
)

# Vehicle check-out
receipt = parking.calculate_exit_fee(
    plate_number="DL 01 AB 8842",
    exit_time_str="2026-04-10 17:30:00",
    payment_mode="FASTAG"
)
print(f"Fee: ₹{receipt['total_fee']} | Barrier: {receipt['barrier_gate']}")
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License
MIT License. Created with ❤️ by [Shyam Pandey](https://github.com/shyampandey1104).
