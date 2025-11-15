# Interchange Station Coordinate Analysis (US-105)

## Overview

This document analyzes interchange stations in `stations.csv` that currently have identical coordinates for physically separated platforms. This affects the accuracy of walking distance calculations in the TSP model.

**Generated:** November 15, 2025  
**Related User Story:** US-105 - Verify Interchange Station Coordinates

## Summary Statistics

- **Total interchange stations with duplicate coordinates:** 29
- **Total station entries affected:** 68 (including all platforms at each interchange)
- **Confirmed physical separations:** 2 (Tanah Merah, Tampines - from field observations)

## Interchange Stations with Identical Coordinates

### 🔴 HIGH PRIORITY - Confirmed Physical Separation

These interchanges have field-verified significant walking distances between platforms:

#### 1. Tanah Merah (CG / EW4)
- **Current Coordinates:** 1.327262, 103.946513
- **Lines:** Changi Airport Branch (CG) + East-West Line (EW)
- **Field Measurement:** 4:54 transfer time (EW4 → CG)
- **Notes:** Passengers must tap out of EW4, walk through external areas, then tap in at CG platform. Substantial physical separation.
- **Action Required:** ✅ Walking connection already exists (2 min transfer time in connections.csv)
- **Coordinate Update:** Research actual platform locations via OpenStreetMap

#### 2. Tampines (DT32 / EW2)
- **Current Coordinates:** 1.353374, 103.945084
- **Lines:** Downtown Line (DT) + East-West Line (EW)
- **Notes:** Mentioned in observations as requiring fare gate exit and ~10 min walk through market
- **Action Required:** Field verification or LTA/OSM research needed

### 🟡 MEDIUM PRIORITY - Large Interchange Hubs

These major interchanges likely have some platform separation:

#### 3. Dhoby Ghaut (CC1 / NE6 / NS24)
- **Coordinates:** 1.298786, 103.84502
- **Lines:** Circle, North-East, North-South
- **Notes:** 3-line interchange, platforms likely separated

#### 4. City Hall (EW13 / NS25)
- **Coordinates:** 1.293214, 103.851835
- **Lines:** East-West, North-South
- **Notes:** Major interchange with underground platforms

#### 5. Raffles Place (EW14 / NS26)
- **Coordinates:** 1.284409, 103.85147
- **Lines:** East-West, North-South
- **Notes:** Deep underground station

#### 6. Bishan (CC15 / NS17)
- **Coordinates:** 1.351455, 103.848263
- **Lines:** Circle, North-South
- **Notes:** Major interchange

#### 7. Serangoon (CC13 / NE12)
- **Coordinates:** 1.349807, 103.873771
- **Lines:** Circle, North-East
- **Notes:** Large interchange hub

### 🟢 LOW PRIORITY - Likely Minimal Separation

These interchanges are typically more compact:

#### 8-29. Other Interchanges

| Station Name | Station IDs | Lines | Coordinates |
|--------------|-------------|-------|-------------|
| HarbourFront | CC29, NE1 | CC, NE | 1.265391, 103.822403 |
| Marina Bay | CE2, NS27, TE20 | CE, NS, TE | 1.275171, 103.854751 |
| Outram Park | EW16, NE3, TE17 | EW, NE, TE | 1.280685, 103.840241 |
| Bayfront | CE1, DT16 | CE, DT | 1.282535, 103.85973 |
| Chinatown | DT19, NE4 | DT, NE | 1.28502, 103.844003 |
| Promenade | CC4, DT15 | CC, DT | 1.293854, 103.860151 |
| Bugis | DT14, EW12 | DT, EW | 1.30053, 103.856095 |
| Orchard | NS22, TE14 | NS, TE | 1.303223, 103.831982 |
| Little India | DT12, NE7 | DT, NE | 1.306571, 103.849299 |
| Buona Vista | CC22, EW21 | CC, EW | 1.307263, 103.790705 |
| Newton | DT11, NS21 | DT, NS | 1.31296, 103.838864 |
| Paya Lebar | CC9, EW8 | CC, EW | 1.31805, 103.892318 |
| Stevens | DT10, TE11 | DT, TE | 1.320192, 103.825461 |
| Botanic Gardens | CC19, DT9 | CC, DT | 1.322559, 103.815747 |
| MacPherson | CC10, DT26 | CC, DT | 1.326728, 103.890102 |
| Jurong East | EW24, NS1 | EW, NS | 1.333115, 103.742297 |
| Expo | CG1, DT35 | CG, DT | 1.33564, 103.962238 |
| Caldecott | CC17, TE9 | CC, TE | 1.33768, 103.839991 |
| Bukit Panjang | BP6, DT1 | BP, DT | 1.378296, 103.762138 |
| Choa Chu Kang | BP1, NS4 | BP, NS | 1.384749, 103.744534 |
| Sengkang | NE16, STC | NE, STC | 1.39133, 103.895294 |
| Punggol | NE17, PTC | NE, PTC | 1.405255, 103.902354 |
| Woodlands | NS9, TE2 | NS, TE | 1.437388, 103.787675 |

## Data Sources for Coordinate Updates

### Recommended Sources

1. **OpenStreetMap (OSM)**
   - URL: https://www.openstreetmap.org/
   - Search for station names and extract platform/entrance coordinates
   - Most accurate for platform-level precision

2. **LTA DataMall**
   - URL: https://datamall.lta.gov.sg/
   - Official LTA data source
   - May provide platform-specific coordinates

3. **Google Maps**
   - Can identify separate platform entrances
   - Use "Street View" to confirm physical layout

4. **Field Measurements**
   - GPS coordinates from actual platform visits
   - Most accurate but time-intensive

## Acceptance Criteria (from US-105)

- [ ] Identify interchange stations where platforms are physically separated
- [ ] Source actual platform coordinates from OpenStreetMap or LTA data
- [ ] Update stations.csv with platform-specific coordinates where applicable
- [ ] Document stations with significant inter-platform walking distances (>5 min)
- [ ] Validation script confirms coordinate accuracy

## Current Walking Transfer Times

The following walking connections already exist in `connections.csv`:

```
CG ↔ EW4 (Tanah Merah): 2.0 min
DT32 ↔ EW2 (Tampines): walking connection TBD
```

**Note:** The 2.0 min transfer time for Tanah Merah may be underestimated given the 4:54 field measurement.

## Recommended Actions

1. **Research Phase:**
   - Extract platform coordinates from OpenStreetMap for all 29 interchanges
   - Cross-reference with LTA DataMall if available
   - Create CSV with old vs new coordinates

2. **Validation Phase:**
   - Calculate Haversine distances between old/new coordinates
   - Identify stations with >100m coordinate differences
   - Prioritize updates for stations with >200m differences

3. **Update Phase:**
   - Update `stations.csv` with verified coordinates
   - Recalculate walking transfer times based on new distances
   - Update `connections.csv` via `add_walking_connections.py`

4. **Testing Phase:**
   - Run validation scripts
   - Compare total network distance before/after
   - Verify all connections remain valid

## Impact Assessment

**Benefits:**
- More accurate walking distance calculations
- Better TSP route optimization for transfers
- Realistic transfer time estimates

**Risks:**
- May require regenerating all walking connections
- Could affect existing route calculations
- Need to maintain data consistency

## Related Files

- `data/raw/stations.csv` - Station coordinate data
- `data/raw/connections.csv` - Connection data with walking transfers
- `scripts/add_walking_connections.py` - Walking connection generator
- `scripts/validate_stations.py` - Validation tool
- `data/raw/observations.md` - Field measurement data

## Next Steps

1. Create script to extract OSM platform coordinates
2. Generate coordinate update CSV
3. Review and approve coordinate changes
4. Apply updates to stations.csv
5. Regenerate walking connections
6. Validate complete network
7. Update US-105 issue with findings
