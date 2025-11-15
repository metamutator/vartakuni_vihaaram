# Data Directory

## Structure

### `raw/`
Original, unprocessed data files. Do not modify these directly.

**Expected files:**
- `stations.csv` - List of all stations with metadata
- `connections.csv` - Direct links between stations (train + walking)
- `lines.csv` - Metro line metadata (colors, names)

### `processed/`
Cleaned, validated, and transformed data ready for algorithm consumption.

**Generated files:**
- `network_graph.json` - NetworkX graph serialized
- `adjacency_matrix.csv` - Distance/time matrix
- `station_index.json` - Station ID to index mapping

### `solutions/`
Pre-computed optimal routes for different starting stations.

**Format:**
- `routes_all_starts.json` - All pre-computed solutions
- Individual route files if needed

## Data Schema

### stations.csv
```csv
station_id,station_name,line_code,latitude,longitude,operational_status
NS1,Jurong East,NSL,1.3330,103.7421,active
NS1_EWL,Jurong East,EWL,1.3330,103.7421,active
```

### connections.csv
```csv
connection_id,from_station_id,to_station_id,connection_type,travel_time_minutes,distance_meters
1,NS1,NS2,train,2.0,1500
2,NS1,NS1_EWL,walk_transfer,3.0,150
```

### lines.csv
```csv
line_code,line_name,color_hex,line_type
NSL,North-South Line,#D42E12,mrt
EWL,East-West Line,#009645,mrt
```

## Data Collection Status

- [x] Singapore MRT/LRT stations list (214 entries, 181 unique stations) - **US-101** ✅
- [x] Geographic coordinates (from sgraildata) - **US-101** ✅
- [x] Line codes and multi-line station handling - **US-101** ✅
- [x] Inter-station travel times (386 train connections, estimated) - **US-102** ✅
- [x] Walking transfer times (156 walking connections) - **US-103** ✅
- [x] Line metadata (colors, names) - **US-104** ✅
- [x] Fix disconnected LRT loops and TE extension - **US-108** ✅

**Epic 1: Data Foundation - COMPLETE** 🎉

## Current Files

### Raw Data (`raw/`)
- `sg-rail.geojson` - Original GeoJSON from [sgraildata](https://github.com/cheeaun/sgraildata)
- `sg-rail-walks.geojson` - Walking connections GeoJSON from sgraildata
- `stations.csv` - **214 station entries** with coordinates and line codes
- `connections.csv` - **554 total connections:**
  - **398 train connections** (199 pairs)
  - **72 walk_transfer connections** (36 pairs, interchange transfers)
  - **84 walk_between_stations connections** (42 pairs, nearby stations)
- `lines.csv` - **15 MRT/LRT line metadata** with names, colors, types
- `DATA_SOURCE.md` - Station data source documentation
- `CONNECTIONS_SOURCE.md` - Train connection methodology and limitations
- `WALKING_CONNECTIONS_SOURCE.md` - Walking connection documentation
- `LINES_METADATA_SOURCE.md` - Line metadata documentation
- `LRT_TE_CONNECTIONS_FIX.md` - LRT hub and TE extension connection fixes (US-108)

### Important Notes

⚠️ **Train travel times are ESTIMATED**, not official schedule data. See `CONNECTIONS_SOURCE.md` for methodology.

⚠️ **Walking times are MIXED** (54% from measured source data, 46% estimated). See `WALKING_CONNECTIONS_SOURCE.md` for details.
