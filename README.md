# Machine Order Timeline Analyzer

A Python solution using xlwings lite to read Excel tables and provide quarterly timeline analysis of machine orders.

## Features

- **Reads Excel files** with machine order data containing dates and quantities
- **Automatically detects** date, quantity, and machine type columns
- **Generates quarterly reports** showing how many machines to order per quarter
- **Exports detailed analysis** to Excel with multiple sheets
- **Supports both xlwings and pandas** for maximum compatibility

## Files

- `machine_timeline_analyzer_lite.py` - Enhanced analyzer with command-line interface
- `machine_timeline_analyzer.py` - Basic analyzer version
- `create_sample_data.py` - Creates sample machine order data for testing
- `machine_orders.xlsx` - Sample machine order data
- `machine_timeline_analysis.xlsx` - Generated quarterly analysis report

## Requirements

```bash
pip install pandas openpyxl xlwings
```

## Usage

### Basic Usage
```bash
python machine_timeline_analyzer_lite.py machine_orders.xlsx
```

### Advanced Usage
```bash
# Specify custom column names
python machine_timeline_analyzer_lite.py data.xlsx --date-col "Purchase Date" --quantity-col "Qty"

# Specify sheet name and output file
python machine_timeline_analyzer_lite.py orders.xlsx --sheet "Orders" --output "quarterly_report.xlsx"

# Use specific machine type column
python machine_timeline_analyzer_lite.py data.xlsx --machine-col "Equipment Type"
```

### Command Line Options
- `--sheet` - Sheet name to read (default: first sheet)
- `--date-col` - Date column name (auto-detected if not specified)
- `--quantity-col` - Quantity column name (auto-detected if not specified)
- `--machine-col` - Machine type column name (auto-detected if not specified)
- `--output` - Output Excel file name (default: machine_timeline_analysis.xlsx)
- `--use-xlwings` - Use xlwings instead of pandas

## Expected Excel Format

The Excel file should contain at least a date column. The analyzer will automatically detect:

| Column Type | Auto-detected Names |
|-------------|-------------------|
| Date | Order Date, Purchase Date, Date, Delivery Date |
| Quantity | Quantity, Qty, Amount, Count, Units |
| Machine Type | Machine Type, Equipment, Product, Item |

### Example Excel Structure
```
| Order ID | Machine Type | Order Date | Quantity | Priority |
|----------|-------------|------------|----------|----------|
| ORD-1001 | CNC Lathe   | 2024-01-15 | 2        | High     |
| ORD-1002 | Press       | 2024-02-10 | 3        | Medium   |
```

## Output

The analyzer generates:

1. **Console Report** - Detailed quarterly breakdown showing:
   - Total machines to order per quarter
   - Machine type breakdown with quantities and order counts
   - Summary statistics

2. **Excel Report** with multiple sheets:
   - `Quarterly_Summary` - High-level quarterly totals
   - `Machine_Breakdown` - Detailed breakdown by machine type and quarter
   - `Source_Data_with_Quarters` - Original data with added quarter information

### Sample Output
```
Q1 2024:
  Total Machines to Order: 25
  Total Orders: 9
  Machine Breakdown by Quantity:
    - Press Machine: 12 machines (3 orders)
    - Welding Robot: 5 machines (2 orders)
    - Quality Control Scanner: 4 machines (1 orders)
```

## Creating Sample Data

To create sample machine order data for testing:

```bash
python create_sample_data.py
```

This generates `machine_orders.xlsx` with random machine orders spanning multiple quarters.

## Error Handling

The analyzer includes robust error handling for:
- Missing or invalid date columns
- Invalid date formats
- Missing quantity data (defaults to 1)
- File reading errors
- Column detection failures

## Compatibility

- **Python 3.6+**
- **Works without xlwings** installed (falls back to pandas)
- **Cross-platform** (Windows, macOS, Linux)
- **Supports both .xlsx and .xls** files

## Examples

### Basic Timeline Analysis
```python
from machine_timeline_analyzer_lite import MachineOrderTimelineAnalyzer

analyzer = MachineOrderTimelineAnalyzer('orders.xlsx')
analyzer.load_data()
timeline_data = analyzer.analyze_timeline()
analyzer.print_timeline_report(timeline_data)
analyzer.export_timeline_report('quarterly_analysis.xlsx')
```

### Custom Column Mapping
```python
analyzer = MachineOrderTimelineAnalyzer('custom_data.xlsx')
analyzer.load_data(
    date_column='Purchase Date',
    quantity_column='Qty',
    machine_column='Equipment Type'
)
timeline_data = analyzer.analyze_timeline()
analyzer.print_timeline_report(timeline_data)
```