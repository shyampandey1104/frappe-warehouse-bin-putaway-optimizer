import unittest
from putaway.engine import WarehouseBinPutawayOptimizer, StorageBin, SKUProfile


class TestWarehouseBinPutaway(unittest.TestCase):
    def setUp(self):
        self.optimizer = WarehouseBinPutawayOptimizer()
        # Register Bins
        self.optimizer.register_bin(StorageBin(
            bin_id="A01-B01-S01-01", aisle=1, bay=1, shelf_level=1, max_volume_cm3=50000, max_weight_kg=100.0
        ))
        self.optimizer.register_bin(StorageBin(
            bin_id="A01-B01-S03-01", aisle=1, bay=1, shelf_level=3, max_volume_cm3=50000, max_weight_kg=100.0
        ))
        # Register SKUs: Class A (Fastest) and Class C (Slow)
        self.optimizer.register_sku(SKUProfile(
            sku="SKU-FAST-COLDDRINK", name="Coke 500ml", unit_volume_cm3=600, unit_weight_kg=0.55, abc_velocity_class="A"
        ))
        self.optimizer.register_sku(SKUProfile(
            sku="SKU-SLOW-DRILLBIT", name="Concrete Drill Bit", unit_volume_cm3=200, unit_weight_kg=0.20, abc_velocity_class="C"
        ))

    def test_class_a_putaway_to_ground_shelf(self):
        rec = self.optimizer.recommend_putaway("SKU-FAST-COLDDRINK", quantity=20)
        # Class A prefers shelf 1
        self.assertEqual(rec.shelf_level, 1)
        self.assertEqual(rec.recommended_bin_id, "A01-B01-S01-01")

    def test_serpentine_pick_path(self):
        path = self.optimizer.generate_serpentine_pick_path(["SKU-FAST-COLDDRINK"])
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0]["stop_sequence"], 1)


if __name__ == "__main__":
    unittest.main()
