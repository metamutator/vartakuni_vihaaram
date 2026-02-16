# TSP Tour Maps

This directory contains rendered SVG maps showing TSP (Traveling Salesman Problem) tours of the Singapore MRT/LRT network.

## Available Tours

### Nearest Neighbor Tour
**File**: `nearest_neighbor_tour.svg`

- **Algorithm**: Nearest Neighbor heuristic
- **Stations**: 214 (all operational stations)
- **Total Distance**: 799.48 minutes
- **Start/End**: NS1 (Jurong East)
- **Coverage**: 189/214 stations rendered (88.3%)

This tour uses a greedy algorithm that always selects the nearest unvisited station. While not optimal, it provides a quick baseline solution.

## How to View

### In Browser
Simply open the SVG files in a modern web browser:
- Chrome, Firefox, Safari, or Edge
- The maps are fully interactive (pan, zoom, inspect)

### In Jupyter/Quarto
```python
from IPython.display import SVG, display
display(SVG('data/processed/maps/nearest_neighbor_tour.svg'))
```

### Embed in HTML
```html
<object data="data/processed/maps/nearest_neighbor_tour.svg" type="image/svg+xml" width="100%">
  <img src="data/processed/maps/nearest_neighbor_tour.svg" alt="TSP Tour" />
</object>
```

## Map Features

Each tour SVG includes:
- **Base map**: Singapore MRT/LRT system with station IDs
- **Tour path**: Red arrows showing direction of travel
- **Step numbers**: Sequential numbering at each station
- **Start marker**: Green circle highlighting the starting station
- **Legend**: Tour information (name, station count, visual key)

## Map Elements

- **Tour color**: Red (#FF0000)
- **Arrow markers**: Directional indicators on each segment
- **Station markers**: White circles with black numbers
- **Start station**: Green circle (larger)
- **Non-operational stations**: Faded with 20% opacity

## Attribution

**Original Map Source:**
- Title: Singapore MRT/LRT System Map
- Source: https://commons.wikimedia.org/wiki/File:Singapore_MRT_and_LRT_System_Map.svg
- License: CC BY-SA 3.0
- Attribution: Wikipedia contributors

**Modifications:**
- Added station IDs to labels
- Removed/faded non-operational stations
- Overlaid TSP tour paths with directional indicators
- Added legends and tour metadata

## Generating New Tours

To create a new tour map:

1. **Generate a tour** (creates JSON file):
   ```bash
   python scripts/generate_sample_tour.py
   ```

2. **Render the tour onto SVG**:
   ```bash
   python scripts/render_tour_to_svg.py data/processed/tours/sample_nn_tour.json \
     --name "My Custom Tour" \
     --color "#0000FF" \
     --output data/processed/maps/my_tour.svg
   ```

3. **View the result**:
   - Open `data/processed/maps/my_tour.svg` in your browser

## Advanced Usage

### Custom Tour from List

Create a JSON file with your tour:
```json
{
  "tour": ["NS1", "NS2", "NS3", "EW1", "EW2"],
  "algorithm": "Custom",
  "cost": 150.5
}
```

Then render it:
```bash
python scripts/render_tour_to_svg.py mytour.json
```

### Styling Options

```bash
python scripts/render_tour_to_svg.py tour.json \
  --name "Blue Tour" \
  --color "#0000FF" \    # Blue path
  --width "5" \           # Thicker line
  --no-numbers           # Hide step numbers
```

## Known Limitations

- **Coverage**: Currently 88.3% of stations are mapped to SVG positions
- **Unmapped stations**: 25 stations lack SVG label matches (see `unmatched_svg_labels.csv`)
- **Tour continuity**: Unmapped stations will have gaps in the rendered path
- **Static only**: Tours are rendered as static SVG (no animation or interactivity)

To improve coverage, update `data/processed/svg_name_map.csv` following the guide in `docs/visualization/svg_map_integration.md`.

## File Sizes

Typical file sizes:
- Base pruned map: ~60 KB
- Tour overlay SVG: ~120-150 KB (depending on tour length)

## Future Enhancements

Potential improvements for future versions:
- Interactive tour playback (JavaScript-based)
- Multiple tours on one map (color-coded)
- Tour statistics overlay (distance, time, segments)
- Comparison view (side-by-side tours)
- Export to other formats (PNG, PDF)

## License

The original map is licensed under CC BY-SA 3.0. All derivative works (including these tour overlays) inherit the same license.

When using or sharing these maps, please attribute:
- Original map: Wikipedia contributors (CC BY-SA 3.0)
- Tour overlay: Vartakuni Vihaaram project

## Support

For issues or questions:
- Check `docs/visualization/svg_map_integration.md` for mapping details
- Run `python scripts/validate_svg_mapping.py` to check coverage
- See `scripts/github_issues/issues.md` for Epic 8 user stories
