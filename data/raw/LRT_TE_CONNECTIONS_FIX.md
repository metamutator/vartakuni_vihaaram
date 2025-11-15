# LRT Hub and TE Extension Connections Fix - US-108

## Overview

**Issue:** Graph builder (US-201) identified 6 disconnected components in the Singapore MRT/LRT network.

**Solution:** Added missing connections between LRT hub stations and loop stations, plus TE line gap connection.

**Result:** Graph is now fully connected (single component).

## Missing Connections Added

### 1. Sengkang LRT System

**Hub Station:** STC (Sengkang) at NE16

**East Loop (SE):**
- STC ↔ SE1 (Compassvale): 1.65 min, 672m

**West Loop (SW):**
- STC ↔ SW1 (Cheng Lim): 1.50 min, 580m

**Rationale:** Sengkang LRT operates as two loops (East and West) connected to the central STC hub, which provides interchange with NE Line.

### 2. Punggol LRT System

**Hub Station:** PTC (Punggol) at NE17

**East Loop (PE):**
- PTC ↔ PE1 (Cove): 1.79 min, 752m

**West Loop (PW):**
- PTC ↔ PW1 (Sam Kee): 1.46 min, 557m

**Rationale:** Punggol LRT operates as two loops (East and West) connected to the central PTC hub, which provides interchange with NE Line.

### 3. Thomson-East Coast Line Extension

**Direct Connection:**
- TE20 (Marina Bay) ↔ TE22 (Gardens by the Bay): 2.37 min, 1560m

**Rationale:** **TE21 (Marina South) and TE22A (Founders' Memorial) stations have been built but are not yet operational.** Trains currently run directly from TE20 to TE22, bypassing both unopened stations. This connection reflects current operations as of November 2025.

**Important:** When TE21 and TE22A become operational, this connection will need to be replaced with:
- TE20 ↔ TE21 (new connection to Marina South)
- TE21 ↔ TE22A (new connection to Founders' Memorial)
- TE22A ↔ TE22 (new connection from Founders' Memorial to Gardens by the Bay)
- Remove: TE20 ↔ TE22 (direct connection)

## Statistics

### Before Fix (US-201 validation)

- **Components:** 6 disconnected
  1. Main network: 179 stations ✅
  2. SE Loop: 5 stations ❌
  3. SW Loop: 8 stations ❌
  4. PE Loop: 7 stations ❌
  5. PW Loop: 7 stations ❌
  6. TE Extension: 8 stations ❌
- **Total Connections:** 271 (542 directional entries)
- **Train Connections:** 193 edges (386 directional entries)

### After Fix

- **Components:** 1 fully connected ✅
- **Total Stations:** 214
- **Total Connections:** 277 edges (554 directional entries)
- **Train Connections:** 199 edges (398 directional entries)
- **New Connections Added:** 6 edges (10 bidirectional pairs + 2 remaining from 12 total)
- **Graph Diameter:** 39 (maximum shortest path)
- **Average Degree:** 2.59

### Connection Breakdown

| Type | Count (edges) |
|------|---------------|
| train | 199 |
| walk_transfer | 36 |
| walk_between_stations | 42 |
| **Total** | **277** |

## Data Quality

### Travel Time Estimation

All added connections use the same estimation methodology as US-102:

```python
travel_time = (distance_km / avg_speed_kmh) * 60 + dwell_time

Where:
  - LRT average speed: 35 km/h
  - MRT average speed: 50 km/h
  - Dwell time: 0.5 minutes
```

### Distance Calculation

Distances calculated using Haversine formula based on station coordinates from US-101.

## Files Modified

1. **`data/raw/connections.csv`** - Added 10 new connection entries (5 bidirectional pairs)
2. **`scripts/fix_disconnected_components.py`** - Script to generate missing connections
3. **`data/raw/LRT_TE_CONNECTIONS_FIX.md`** - This documentation file

## Validation

Graph connectivity validated using `src.graph.builder`:

```bash
$ python -m src.graph.builder
✅ Graph is fully connected
📊 Graph Statistics:
   Stations: 214
   Connections: 277
   Diameter: 39
```

## Future Considerations

### TE21 Station Opening

When TE21 becomes operational:
1. Remove direct TE20 ↔ TE22 connection
2. Add TE20 ↔ TE21 connection
3. Add TE21 ↔ TE22 connection
4. Update with official travel times if available

### LRT Loop Topology

Current implementation assumes:
- Linear connection from hub to first loop station (SE1, SW1, PE1, PW1)
- Loop stations form circular routes returning to hub
- Matches typical LRT loop operations in Singapore

## Acceptance Criteria Status

✅ **Sengkang LRT connected:** STC hub ↔ SE1 (East Loop) and STC hub ↔ SW1 (West Loop)

✅ **Punggol LRT connected:** PTC hub ↔ PE1 (East Loop) and PTC hub ↔ PW1 (West Loop)

✅ **Thomson-East Coast Line connected:** TE20 ↔ TE22 (direct connection, bypassing unopened TE21)

✅ **All connections bidirectional** with appropriate travel times

✅ **Graph connectivity validation passes** (single connected component)

✅ **Connection type properly labeled** (all as 'train' with appropriate line codes)

**Overall:** All requirements met.

## Last Updated

November 15, 2025

---

**Related User Stories:**
- US-101: Station Data Collection
- US-102: Inter-Station Travel Time Data
- US-201: Graph Builder Module
- **US-108: Fix Disconnected LRT and TE Extension Connections** ✅
