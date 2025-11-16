# SVG Map Integration Guide

This document explains how to work with the Singapore MRT/LRT SVG map and maintain the station ID mapping.

## Overview

The project uses an SVG map sourced from Wikimedia Commons (CC BY-SA 3.0) and augments it with station IDs from our dataset. This enables:
1. Visual representation of the network with correct station identifiers
2. Rendering TSP tour overlays on the map
3. Interactive station identification

## Files

### Source Data
- `data/raw/Singapore_MRT_and_LRT_System_Map.svg` - Original SVG map (CC BY-SA 3.0)
- `data/raw/stations.csv` - Station data with IDs, names, coordinates, status

### Generated/Processed Files
- `data/processed/svg_name_map.csv` - **Core mapping file**: Maps SVG text labels → station IDs
- `data/processed/unmatched_svg_labels.csv` - SVG labels that couldn't be auto-matched
- `data/processed/sg_mrt_lrt_built_only.svg` - Pruned map with station IDs added

### Scripts
- `scripts/create_svg_mapping.py` - Creates initial mapping (auto-matching)
- `scripts/validate_svg_mapping.py` - Validates mapping coverage
- `scripts/prune_svg_map.py` - Updates SVG with station IDs, hides non-operational

## Mapping File Format

`data/processed/svg_name_map.csv` structure:

```csv
svg_label,station_ids,display_label,x,y
Admiralty,NS10,Admiralty (NS10),586.0,80.0
Bishan,"CC15,NS17","Bishan (CC15, NS17)",793.0,390.0
Dhoby Ghaut,"CC1,NE6,NS24","Dhoby Ghaut (CC1, NE6, NS24)",713.5,657.5
```

Fields:
- **svg_label**: Text label as it appears in the original SVG
- **station_ids**: Comma-separated list of station IDs (for interchanges)
- **display_label**: Formatted label with IDs for display (e.g., "Expo (CG1, DT35)")
- **x, y**: SVG coordinates of the label

## How to Update the Mapping

### 1. Auto-Generate Initial Mapping

```bash
python scripts/create_svg_mapping.py
```

This will:
- Extract all station labels from the SVG
- Match them to station names in `stations.csv`
- Create `svg_name_map.csv` with successful matches
- Export unmatched labels to `unmatched_svg_labels.csv`

### 2. Validate Coverage

```bash
python scripts/validate_svg_mapping.py
```

This reports:
- Coverage percentage (target: ≥95%)
- List of unmapped stations
- Duplicate/ambiguous mappings
- Unmatched SVG labels

### 3. Manual Fixes

Common issues and fixes:

#### Issue: Word Order Reversed
SVG label: `"India Little"`
Should map to: `DT12` (Little India), `NE7` (Little India)

**Fix**: Add to `svg_name_map.csv`:
```csv
India Little,"DT12,NE7","Little India (DT12, NE7)",x,y
```

#### Issue: Multi-word Names Split
SVG may split "Choa Chu Kang" into separate labels: `"Choa"`, `"Chu Kang"`, `"Choa Chu Kang"`

**Fix**: Keep only the complete label mapping:
```csv
Choa Chu Kang,"BP1,NS4","Choa Chu Kang (BP1, NS4)",x,y
```
Delete partial mappings for `"Choa"`, `"Chu Kang"`.

#### Issue: Language Variants
SVG has Malay/English alternatives (via `<switch>` elements).
Our parser may extract both. Keep the English version.

Example:
- SVG label: `"Bunga Gardens Kebun Botanic"` (mixed Malay/English)
- Should be: `"Botanic Gardens"`

**Fix**:
```csv
Botanic Gardens,"CC19,DT9","Botanic Gardens (CC19, DT9)",x,y
```

### 4. Re-run Scripts

After manual edits to `svg_name_map.csv`:

```bash
# Validate updated mapping
python scripts/validate_svg_mapping.py

# Regenerate pruned SVG with updates
python scripts/prune_svg_map.py
```

## Station Coverage Status

### Current Coverage
Run `python scripts/validate_svg_mapping.py` for latest stats.

### Known Unmapped Stations
As of latest run, the following operational stations lack SVG labels or require manual mapping:
- See validation script output for current list

### Intentionally Unmapped
Some future/planned stations are in the SVG but not in `stations.csv` with `active` status:
- Brickland (future)
- Sungei Kadut (future)
- Various JRL, CRL, TEL extensions

These are correctly excluded from the mapping.

## Workflow Summary

```
┌─────────────────────────────────┐
│ Original SVG + stations.csv     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ create_svg_mapping.py           │
│ (auto-match labels → IDs)       │
└────────────┬────────────────────┘
             │
             ├─► svg_name_map.csv
             └─► unmatched_svg_labels.csv
             │
             ▼
┌─────────────────────────────────┐
│ Manual review & editing         │
│ (fix mismatches, add missing)   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ validate_svg_mapping.py         │
│ (check coverage ≥ 95%)          │
└────────────┬────────────────────┘
             │
             ▼ (if validated)
┌─────────────────────────────────┐
│ prune_svg_map.py                │
│ (update SVG with IDs)           │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ sg_mrt_lrt_built_only.svg       │
│ (ready for tour rendering)      │
└─────────────────────────────────┘
```

## Attribution

Original map source:
- **Title**: Singapore MRT/LRT System Map
- **Source**: https://commons.wikimedia.org/wiki/File:Singapore_MRT_and_LRT_System_Map.svg
- **License**: CC BY-SA 3.0
- **Attribution**: Wikipedia contributors

This attribution is preserved in:
- `data/raw/MRT_ATTRIBUTION.md`
- XML comments in processed SVG files

## Troubleshooting

### "Coverage < 95%"
- Run validation to see which stations are unmapped
- Check `unmatched_svg_labels.csv` for labels that might match
- Manually add mappings to `svg_name_map.csv`

### "Duplicate mappings"
- Review the duplicate list in validation output
- Often caused by word-splitting (e.g., "Choa", "Chu Kang", "Choa Chu Kang" all mapping to same station)
- Remove partial matches, keep only complete station names

### "Station not visible in SVG"
- Some stations may not have text labels in the SVG
- Document these in the "Intentionally Unmapped" section above
- Acceptable if coverage is still ≥95%

## Next Steps

Once mapping is validated (≥95% coverage):
1. Proceed to US-803: Tour Overlay Renderer
2. Use `svg_name_map.csv` to locate stations for rendering tour paths
3. Generate sample tours with US-804
