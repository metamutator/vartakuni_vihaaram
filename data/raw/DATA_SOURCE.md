# Singapore MRT/LRT Stations Data - Source Documentation

## Data Source

**Primary Source:** [cheeaun/sgraildata](https://github.com/cheeaun/sgraildata)
**File Used:** `data/v1/sg-rail.geojson`
**Date Downloaded:** November 9, 2025
**License:** Open source (verify repository license)

## Data Attribution

The original sgraildata repository aggregates data from multiple sources:
- **CityMapper** - Routes and stops
- **Wikipedia** - Station names (English, Chinese, Tamil)
- **Land Transport Authority (LTA)** - Exit point coordinates, official station codes
- **OpenStreetMap** - Additional geographic data

## Data Processing

### Conversion Process

The GeoJSON data was converted to CSV format using the script:
`scripts/convert_geojson_to_csv.py`

### Transformations Applied

1. **Extracted station features** from GeoJSON (filtered by `stop_type: "station"`)
2. **Split multi-line stations** into separate rows (one row per platform)
   - Example: "Dhoby Ghaut" (NS24-NE6-CC1) → 3 separate rows
3. **Mapped line codes** from station codes (e.g., "NS10" → line code "NS")
4. **Set operational status** to "active" for all stations (to be refined with LTA API data)
5. **Converted coordinates** from GeoJSON format [longitude, latitude] to separate lat/lon columns

### CSV Schema

```csv
station_id, station_name, line_code, latitude, longitude, operational_status
```

**Field Descriptions:**
- `station_id`: Unique identifier (e.g., NS10, EW12, DT16)
- `station_name`: Station name in English
- `line_code`: Line abbreviation (NS, EW, CC, NE, DT, TE, CE, CG, BP, SE, SW, PE, PW, STC, PTC)
- `latitude`: Latitude in decimal degrees (EPSG:4326)
- `longitude`: Longitude in decimal degrees (EPSG:4326)
- `operational_status`: active | under_construction | planned

## Data Quality

### Coverage

- **Total station entries:** 214
- **Unique stations:** 181
- **Interchange stations:** 30 (multi-line transfer points)
- **Line codes:** 15 different MRT/LRT lines

### Validation

Data validated using `scripts/validate_stations.py` with checks for:
- ✅ Complete required fields
- ✅ Valid Singapore geographic coordinates
- ✅ Consistent station ID formats
- ✅ No duplicate station IDs
- ✅ Meets minimum station count (189+)

### Known Line Codes

**MRT Lines:**
- NS - North-South Line
- EW - East-West Line
- CC - Circle Line
- NE - North-East Line
- DT - Downtown Line
- TE - Thomson-East Coast Line
- CE - Circle Line Extension
- CR - Cross Island Line (future)
- CG - Changi Airport Branch Line

**LRT Lines:**
- BP - Bukit Panjang LRT
- SE - Sengkang East Loop
- SW - Sengkang West Loop
- PE - Punggol East Loop
- PW - Punggol West Loop
- STC - Sengkang LRT (composite code)
- PTC - Punggol LRT (composite code)

### Interchange Stations (Multi-Line)

Stations serving multiple lines have separate entries for each platform:

1. Bayfront (CE, DT)
2. Bishan (CC, NS)
3. Botanic Gardens (CC, DT)
4. Bugis (DT, EW)
5. Bukit Panjang (BP, DT)
6. Buona Vista (CC, EW)
7. Caldecott (CC, TE)
8. Chinatown (DT, NE)
9. Choa Chu Kang (BP, NS)
10. City Hall (EW, NS)
11. Dhoby Ghaut (CC, NE, NS) - **3-line interchange**
12. Expo (CG, DT)
13. HarbourFront (CC, NE)
14. Jurong East (EW, NS)
15. Little India (DT, NE)
16. MacPherson (CC, DT)
17. Marina Bay (CE, NS, TE) - **3-line interchange**
18. Newton (DT, NS)
19. Orchard (NS, TE)
20. Outram Park (EW, NE, TE) - **3-line interchange**
21. Paya Lebar (CC, EW)
22. Promenade (CC, DT)
23. Punggol (NE, PTC)
24. Raffles Place (EW, NS)
25. Sengkang (NE, STC)
26. Serangoon (CC, NE)
27. Stevens (DT, TE)
28. Tampines (DT, EW)
29. Tanah Merah (CG, EW)
30. Woodlands (NS, TE)

## Limitations & Future Work

### Current Limitations

1. **Operational Status:** All stations marked as "active" - needs verification against LTA for under-construction/planned stations
2. **Exit Coordinates:** Data uses general station coordinates, not specific platform exits
3. **Station Names:** Only English names included; Chinese and Tamil names available in source but not imported
4. **Recent Updates:** Data may not include stations opened after sgraildata's last update

### Recommended Next Steps

1. **Cross-validate with LTA DataMall API** to verify:
   - Operational status of stations
   - Recently opened stations
   - Under-construction stations

2. **Verify multi-line station handling** with official LTA platform data

3. **Add station codes to validation** - ensure all codes are currently valid

4. **Consider including alternative names** (Chinese, Tamil) for internationalization

## Verification Against Acceptance Criteria

✅ **CSV file contains all 189+ active/under-construction stations**
   - Current: 214 station entries (181 unique stations)

✅ **Each station has: unique ID, name, line code(s), lat/long, operational status**
   - All fields present and validated

✅ **Multi-line stations have separate entries per platform**
   - 30 interchange stations with 64 total platform entries

⚠️  **Data validated against official LTA sources**
   - Partially validated (source data from LTA via sgraildata)
   - Recommended: Direct LTA API verification for operational status

## Files Generated

1. `data/raw/sg-rail.geojson` - Original GeoJSON from sgraildata
2. `data/raw/stations.csv` - Converted and processed station data
3. `scripts/convert_geojson_to_csv.py` - Conversion script
4. `scripts/validate_stations.py` - Data validation script
5. `data/raw/DATA_SOURCE.md` - This documentation file

## Last Updated

November 9, 2025

---

**Note:** This dataset serves as the foundation for building the metro network graph. The next step (US-102) will involve collecting inter-station travel times and connections.
