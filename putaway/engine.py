"""Warehouse 3D Bin Location Putaway, ABC Velocity Slotting & Directed Picking Engine."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StorageBin(BaseModel):
    bin_id: str         # e.g., "A01-B03-S02-01" (Aisle 1, Bay 3, Shelf 2, Bin 1)
    aisle: int
    bay: int
    shelf_level: int    # 1 (Ground/Eye-level), 2 (Mid), 3 (High - requires forklift)
    max_volume_cm3: float
    max_weight_kg: float
    current_stored_sku: Optional[str] = None
    current_stored_qty: int = 0
    current_weight_kg: float = 0.0


class SKUProfile(BaseModel):
    sku: str
    name: str
    unit_volume_cm3: float
    unit_weight_kg: float
    abc_velocity_class: str  # 'A' (Fastest 20%), 'B' (Medium), 'C' (Slow moving)


class PutawayRecommendation(BaseModel):
    sku: str
    quantity: int
    recommended_bin_id: str
    aisle: int
    bay: int
    shelf_level: int
    reason: str


class WarehouseBinPutawayOptimizer:
    """Optimizes warehouse rack putaway slotting and computes serpentine picking routes."""

    def __init__(self):
        self.bins: Dict[str, StorageBin] = {}
        self.sku_catalog: Dict[str, SKUProfile] = {}

    def register_bin(self, b: StorageBin) -> StorageBin:
        self.bins[b.bin_id] = b
        return b

    def register_sku(self, sku: SKUProfile) -> SKUProfile:
        self.sku_catalog[sku.sku] = sku
        return sku

    def recommend_putaway(self, sku_code: str, quantity: int) -> PutawayRecommendation:
        sku = self.sku_catalog.get(sku_code)
        if not sku:
            raise ValueError(f"SKU {sku_code} not found in catalog.")

        total_vol = sku.unit_volume_cm3 * quantity
        total_wt = sku.unit_weight_kg * quantity

        # ABC Strategy:
        # 'A' velocity -> Ground level (Shelf 1) & low Bay numbers (close to dispatch dock)
        # 'B' velocity -> Mid levels (Shelf 2)
        # 'C' velocity -> Top levels (Shelf 3)
        target_shelf = 1 if sku.abc_velocity_class == "A" else (2 if sku.abc_velocity_class == "B" else 3)

        eligible_bins = []
        for b in self.bins.values():
            # Check if empty or already storing this SKU
            if b.current_stored_sku is None or b.current_stored_sku == sku_code:
                if (b.max_weight_kg - b.current_weight_kg) >= total_wt:
                    eligible_bins.append(b)

        if not eligible_bins:
            raise ValueError(f"No suitable bin with capacity for {quantity} units of {sku_code}.")

        # Score bins: match target shelf level, lowest bay distance from dispatch
        def bin_score(b: StorageBin):
            shelf_penalty = abs(b.shelf_level - target_shelf) * 10
            bay_distance = b.bay + (b.aisle * 5)
            return shelf_penalty + bay_distance

        eligible_bins.sort(key=bin_score)
        selected_bin = eligible_bins[0]

        # Allocate
        selected_bin.current_stored_sku = sku_code
        selected_bin.current_stored_qty += quantity
        selected_bin.current_weight_kg += total_wt

        return PutawayRecommendation(
            sku=sku_code,
            quantity=quantity,
            recommended_bin_id=selected_bin.bin_id,
            aisle=selected_bin.aisle,
            bay=selected_bin.bay,
            shelf_level=selected_bin.shelf_level,
            reason=f"Optimal slot for Class '{sku.abc_velocity_class}' SKU: Shelf {selected_bin.shelf_level}, Bay {selected_bin.bay} nearest dispatch."
        )

    def generate_serpentine_pick_path(self, pick_list_skus: List[str]) -> List[Dict[str, Any]]:
        """Generates directed pick path sorting bins in serpentine (S-shape) aisle travel to minimize walking distance."""
        locations = []
        for sku in pick_list_skus:
            for b in self.bins.values():
                if b.current_stored_sku == sku and b.current_stored_qty > 0:
                    locations.append(b)
                    break

        # S-shape / Serpentine traversal:
        # If Aisle is odd -> Bay ascending (1 -> N)
        # If Aisle is even -> Bay descending (N -> 1)
        def serpentine_key(b: StorageBin):
            if b.aisle % 2 == 1:
                return (b.aisle, b.bay, b.shelf_level)
            else:
                return (b.aisle, -b.bay, b.shelf_level)

        sorted_route = sorted(locations, key=serpentine_key)

        return [
            {
                "stop_sequence": idx + 1,
                "bin_id": b.bin_id,
                "aisle": b.aisle,
                "bay": b.bay,
                "shelf": b.shelf_level,
                "sku": b.current_stored_sku
            }
            for idx, b in enumerate(sorted_route)
        ]
