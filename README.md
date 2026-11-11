# Frappe Warehouse 3D Bin Putaway & Directed Picking Optimizer 🏬🪜

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Frappe](https://img.shields.io/badge/Frappe-v14%20%7C%20v15-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

An intelligent 4-coordinate storage bin putaway, ABC product velocity slotting, and serpentine directed picking path optimizer for **Frappe Framework & ERPNext Warehouse Management**.

---

## 🚀 Key Features

- **Aisle-Bay-Shelf-Bin 4-Level Coordinates**: Granular spatial mapping of industrial warehouse pallet racks and shelf locations.
- **ABC Velocity-Driven Slotting**: Positions fast-moving Class 'A' items on ground-level eye-level shelves nearest to the dispatch dock, and Class 'C' slow items on top levels.
- **Volumetric & Weight Capacity Verification**: Prevents structural rack overloading by tracking live bin volume and kilogram limits.
- **Serpentine (S-Shape) Directed Pick Paths**: Generates optimized pick paths that eliminate wasted walking distance and aisle congestion for warehouse pickers.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/shyampandey1104/frappe-warehouse-bin-putaway-optimizer.git
cd frappe-warehouse-bin-putaway-optimizer
pip install -r requirements.txt
```

---

## 🛠️ Usage Example

```python
from putaway.engine import WarehouseBinPutawayOptimizer, StorageBin, SKUProfile

optimizer = WarehouseBinPutawayOptimizer()

optimizer.register_bin(StorageBin(bin_id="A01-B02-S01-01", aisle=1, bay=2, shelf_level=1, max_volume_cm3=80000, max_weight_kg=150.0))
optimizer.register_sku(SKUProfile(sku="ENERGY-BAR-CHOC", name="Protein Bar", unit_volume_cm3=150, unit_weight_kg=0.08, abc_velocity_class="A"))

# Generate putaway recommendation
slot = optimizer.recommend_putaway("ENERGY-BAR-CHOC", quantity=50)
print(f"Putaway SKU into Bin: {slot.recommended_bin_id} (Shelf {slot.shelf_level}) - {slot.reason}")
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License
MIT License. Created with ❤️ by [Shyam Pandey](https://github.com/shyampandey1104).
