"""Smart Parking Lot ANPR & Dynamic Slab Tariff Billing Engine."""

import re
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class VehicleEntryTicket(BaseModel):
    ticket_id: str
    plate_number: str
    vehicle_type: str  # TWO_WHEELER, FOUR_WHEELER, COMMERCIAL
    entry_time: str    # ISO format YYYY-MM-DD HH:MM:SS
    allocated_bay: str
    barcode_token: str
    is_settled: bool = False
    exit_time: Optional[str] = None
    total_fee: Optional[float] = None
    payment_mode: Optional[str] = None  # FASTAG, UPI, CASH


class SmartParkingEngine:
    """Manages barrier gate check-ins, license plate standardization, and tariff slabs."""

    TARIFF_SLABS = {
        "TWO_WHEELER": {"base_2hr": 30.0, "hourly_after": 15.0, "lost_ticket_penalty": 200.0},
        "FOUR_WHEELER": {"base_2hr": 60.0, "hourly_after": 30.0, "lost_ticket_penalty": 500.0},
        "COMMERCIAL": {"base_2hr": 120.0, "hourly_after": 60.0, "lost_ticket_penalty": 800.0},
    }

    PLATE_REGEX = re.compile(r"^[A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4}$", re.IGNORECASE)

    def __init__(self, facility_name: str = "Metro City Smart Hub Parking"):
        self.facility_name = facility_name
        self.active_vehicles: Dict[str, VehicleEntryTicket] = {}
        self.ticket_seq = 1000

    def clean_plate_number(self, raw_plate: str) -> str:
        """Standardizes messy ANPR OCR strings into clean format (e.g., 'mh-12 ab 1234' -> 'MH12AB1234')."""
        cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_plate).upper()
        if not (8 <= len(cleaned) <= 11):
            raise ValueError(f"Invalid vehicle license plate format: {raw_plate}")
        return cleaned

    def vehicle_checkin(
        self,
        raw_plate: str,
        vehicle_type: str = "FOUR_WHEELER",
        entry_time_str: Optional[str] = None,
        allocated_bay: str = "B-12"
    ) -> VehicleEntryTicket:
        """Issues entry slip when ANPR camera detects front license plate."""
        clean_plate = self.clean_plate_number(raw_plate)
        if clean_plate in self.active_vehicles:
            raise ValueError(f"Vehicle {clean_plate} is already inside the parking premises.")

        v_type = vehicle_type.upper()
        if v_type not in self.TARIFF_SLABS:
            raise ValueError(f"Invalid vehicle type. Choose from {list(self.TARIFF_SLABS.keys())}")

        self.ticket_seq += 1
        ticket_id = f"PRK-{self.ticket_seq}"
        entry_time = entry_time_str or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        barcode_token = f"{ticket_id}-{clean_plate}"

        ticket = VehicleEntryTicket(
            ticket_id=ticket_id,
            plate_number=clean_plate,
            vehicle_type=v_type,
            entry_time=entry_time,
            allocated_bay=allocated_bay,
            barcode_token=barcode_token,
            is_settled=False
        )

        self.active_vehicles[clean_plate] = ticket
        return ticket

    def calculate_exit_fee(
        self,
        plate_number: str,
        exit_time_str: Optional[str] = None,
        payment_mode: str = "FASTAG"
    ) -> Dict[str, Any]:
        """Calculates fee based on duration slabs."""
        clean_plate = self.clean_plate_number(plate_number)
        ticket = self.active_vehicles.get(clean_plate)
        if not ticket:
            raise ValueError(f"No active check-in ticket found for vehicle {clean_plate}")

        t_in = datetime.strptime(ticket.entry_time, "%Y-%m-%d %H:%M:%S")
        exit_str = exit_time_str or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t_out = datetime.strptime(exit_str, "%Y-%m-%d %H:%M:%S")

        duration_seconds = max(0, (t_out - t_in).total_seconds())
        duration_minutes = duration_seconds / 60.0
        duration_hours = math.ceil(duration_minutes / 60.0)

        # Free grace window (15 minutes)
        if duration_minutes <= 15:
            ticket.is_settled = True
            ticket.exit_time = exit_str
            ticket.total_fee = 0.0
            ticket.payment_mode = "GRACE_PERIOD_FREE"
            del self.active_vehicles[clean_plate]
            return {
                "plate_number": clean_plate,
                "duration_minutes": round(duration_minutes, 1),
                "total_fee": 0.0,
                "note": "15-minute free drop-off grace window applied."
            }

        slabs = self.TARIFF_SLABS[ticket.vehicle_type]
        base_fee = slabs["base_2hr"]

        if duration_hours <= 2:
            computed_fee = base_fee
        else:
            extra_hours = duration_hours - 2
            computed_fee = base_fee + (extra_hours * slabs["hourly_after"])

        ticket.is_settled = True
        ticket.exit_time = exit_str
        ticket.total_fee = round(computed_fee, 2)
        ticket.payment_mode = payment_mode

        del self.active_vehicles[clean_plate]

        return {
            "ticket_id": ticket.ticket_id,
            "plate_number": clean_plate,
            "vehicle_type": ticket.vehicle_type,
            "entry_time": ticket.entry_time,
            "exit_time": exit_str,
            "duration_hours": duration_hours,
            "total_fee": round(computed_fee, 2),
            "payment_mode": payment_mode,
            "barrier_gate": "OPEN"
        }
