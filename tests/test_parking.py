import unittest
from parking.engine import SmartParkingEngine


class TestSmartParkingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SmartParkingEngine()

    def test_plate_cleaning(self):
        cleaned = self.engine.clean_plate_number("dl-01 ab 1234")
        self.assertEqual(cleaned, "DL01AB1234")

    def test_checkin_and_exit_billing(self):
        # Entry at 10:00:00
        ticket = self.engine.vehicle_checkin(
            raw_plate="MH 12 CD 4567",
            vehicle_type="FOUR_WHEELER",
            entry_time_str="2026-03-01 10:00:00",
            allocated_bay="P1-24"
        )
        self.assertEqual(ticket.plate_number, "MH12CD4567")

        # Exit at 13:10:00 (3 hours 10 mins -> ceil 4 hours)
        # Slabs for 4-wheeler: first 2 hours = 60, next 2 hours @ 30 = 60 => Total 120
        receipt = self.engine.calculate_exit_fee(
            plate_number="MH 12 CD 4567",
            exit_time_str="2026-03-01 13:10:00",
            payment_mode="FASTAG"
        )
        self.assertEqual(receipt["duration_hours"], 4)
        self.assertEqual(receipt["total_fee"], 120.0)
        self.assertEqual(receipt["barrier_gate"], "OPEN")

    def test_grace_period_free(self):
        self.engine.vehicle_checkin(
            raw_plate="KA 05 MN 9999",
            vehicle_type="TWO_WHEELER",
            entry_time_str="2026-03-01 10:00:00"
        )
        # Exit within 10 minutes
        receipt = self.engine.calculate_exit_fee(
            plate_number="KA 05 MN 9999",
            exit_time_str="2026-03-01 10:10:00"
        )
        self.assertEqual(receipt["total_fee"], 0.0)


if __name__ == "__main__":
    unittest.main()
