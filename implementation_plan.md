## Implementation Plan: Plot Item Hierarchies

### Context

The user wants to visualize item hierarchies from the dataset. Based on the metadata analysis, there is a hierarchical structure embedded in the **Item.[Product Planning Level]** column which contains 199 unique product planning level values with a naming convention that suggests a multi-level hierarchy.

**Dataset**: `Fact.DownloadResult247872ef3de7467cb8ff769b234539c5.csv`
- **Location**: `generated_code/Input/Fact.DownloadResult247872ef3de7467cb8ff769b234539c5.csv`
- **Key Column**: `Item.[Product Planning Level]` (199 unique values)

**Sample Values from Item.[Product Planning Level]**:
- `Nike_KOBE_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL`
- `Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_SPORTSWEAR`
- `Nike_NOT_SUPPLD_WOMENS_APPAREL DIVISION_GLOBAL FOOTBALL`
- `Nike_NOT_SUPPLD_MENS_FOOTWEAR DIVISION_SKATE`

The naming convention suggests a hierarchy structure:
- **Level 1**: Brand (Nike)
- **Level 2**: Sub-brand (KOBE, NOT_SUPPLD)
- **Level 3**: Consumer Offense (KIDS, MENS, WOMENS)
- **Level 4**: Product Type (APPAREL, FOOTWEAR, EQUIPMENT)
- **Level 5**: Division (APPAREL DIVISION, FOOTWEAR DIVISION)
- **Level 6**: Category/Sport (GLOBAL FOOTBALL, SPORTSWEAR, SKATE)

---

## Data Requirements

- [ ] Load CSV file from `generated_code/Input/Fact.DownloadResult247872ef3de7467cb8ff769b234539c5.csv`
- [ ] Extract unique values from `Item.[Product Planning Level]` column
- [ ] Parse the hierarchical structure from the naming convention (split by underscore `_`)
- [ ] Build a parent-child relationship structure for visualization
- [ ] Optionally aggregate metrics (sum of `Actual Cleansed`) per hierarchy level for sizing nodes

---

## Visualization Approach

Recommended visualization types for hierarchical data:

1. **Tree Diagram (Horizontal)**: Shows hierarchy from left to right with connected branches
2. **Radial Tree / Sunburst**: Circular layout with root at center, branches radiating outward
3. **Collapsible Tree**: Interactive tree where nodes can be expanded/collapsed
4. **Dendrogram**: Cluster-style hierarchy diagram

**Recommended**: Use an interactive radial sunburst or collapsible tree to allow exploration of the 6-level hierarchy.

---

## Implementation Steps

- [ ] **Step 1**: Load the dataset and extract unique `Item.[Product Planning Level]` values
- [ ] **Step 2**: Parse each value into hierarchy levels based on the underscore delimiter
- [ ] **Step 3**: Build a hierarchical tree structure (nested dictionary or networkx graph)
- [ ] **Step 4**: Optionally calculate aggregated `Actual Cleansed` totals per hierarchy node
- [ ] **Step 5**: Generate visualization using plotly (interactive) or matplotlib (static)
- [ ] **Step 6**: Save output as HTML (interactive) or PNG (static)

---

## Tools/Libraries

| Library | Purpose |
|---------|---------|
| **pandas** | Data loading and parsing |
| **plotly.express** | Interactive sunburst/radial chart |
| **plotly.graph_objects** | Custom hierarchical visualizations |
| **networkx** | Build and analyze hierarchy graph |
| **matplotlib** | Static tree visualizations |
| **graphviz** | DOT language-based tree rendering |

**Recommended Primary**: `plotly.express` with `treemap()` or `sunburst()` for interactive exploration.

---

## Output Format

- **Primary Deliverable**: Interactive HTML visualization (plotly) allowing zoom, hover tooltips, and drill-down
- **Secondary Deliverable**: Static PNG image for reporting
- **Optional**: JSON structure of the hierarchy for downstream processing

---

## Open Questions

1. **Hierarchy Parsing**: Should the hierarchy be parsed strictly by underscore delimiter, or are there other parsing rules (e.g., "APPAREL DIVISION" as a single level)?
2. **Visualization Preference**: Does the user prefer a horizontal tree, radial sunburst, or treemap?
3. **Sizing**: Should the hierarchy nodes be sized by `Actual Cleansed` totals, or just show the structure?
4. **Interactivity**: Is an interactive HTML output preferred, or a static image?

---

## Implementation Notes

- The `Item.[Product Planning Level]` values use underscores as delimiters between hierarchy levels
- Some levels may contain spaces (e.g., "APPAREL DIVISION") - handle as single level
- Filter out any invalid or malformed entries that don't follow the expected pattern
- Consider using DuckDB if memory issues arise with large dataset (2M+ rows)

---

****