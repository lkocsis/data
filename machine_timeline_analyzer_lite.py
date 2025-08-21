#!/usr/bin/env python3
"""
XLWings Lite Machine Order Timeline Analyzer - Enhanced Version

This script provides comprehensive machine order timeline analysis with both
xlwings and pandas support for maximum compatibility.

Features:
- Reads Excel files with machine order data
- Analyzes orders by quarter and machine type
- Generates timeline reports showing quarterly machine requirements
- Exports results to Excel with multiple sheets
- Supports flexible column naming

Usage:
    python machine_timeline_analyzer_lite.py [excel_file] [options]

Examples:
    python machine_timeline_analyzer_lite.py machine_orders.xlsx
    python machine_timeline_analyzer_lite.py data.xlsx --date-col "Order Date" --quantity-col "Qty"
"""

import argparse
import pandas as pd
from datetime import datetime
from collections import defaultdict
import sys
import os

# Try to import xlwings, but make it optional for lite usage
try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False
    print("Note: xlwings not available, using pandas-only mode")

class MachineOrderTimelineAnalyzer:
    """
    Comprehensive machine order timeline analyzer supporting both xlwings and pandas.
    """
    
    def __init__(self, excel_file, use_xlwings=False):
        """
        Initialize analyzer.
        
        Args:
            excel_file: Path to Excel file
            use_xlwings: Whether to use xlwings (requires Excel/LibreOffice)
        """
        self.excel_file = excel_file
        self.use_xlwings = use_xlwings and XLWINGS_AVAILABLE
        self.data = None
        self.date_column = None
        
    def detect_date_column(self, columns):
        """Auto-detect date column from available columns."""
        date_candidates = [
            'Order Date', 'order date', 'Date', 'date',
            'OrderDate', 'order_date', 'Purchase Date',
            'Delivery Date', 'Required Date'
        ]
        
        for candidate in date_candidates:
            if candidate in columns:
                return candidate
        
        # Look for columns containing 'date'
        for col in columns:
            if 'date' in col.lower():
                return col
                
        return None
    
    def detect_quantity_column(self, columns):
        """Auto-detect quantity column from available columns."""
        quantity_candidates = [
            'Quantity', 'quantity', 'Qty', 'qty', 'Amount',
            'Count', 'Number', 'Units', 'Pieces'
        ]
        
        for candidate in quantity_candidates:
            if candidate in columns:
                return candidate
                
        return None
    
    def detect_machine_column(self, columns):
        """Auto-detect machine type column from available columns."""
        machine_candidates = [
            'Machine Type', 'Machine', 'machine type', 'Equipment',
            'Product', 'Item', 'Description', 'Type'
        ]
        
        for candidate in machine_candidates:
            if candidate in columns:
                return candidate
                
        return None
    
    def read_data_with_xlwings(self, sheet_name=None):
        """Read data using xlwings."""
        try:
            app = xw.App(visible=False)
            wb = app.books.open(self.excel_file)
            
            if sheet_name:
                ws = wb.sheets[sheet_name]
            else:
                ws = wb.sheets[0]  # First sheet
            
            # Get the used range and convert to DataFrame
            used_range = ws.used_range
            data = used_range.options(pd.DataFrame, header=1, index=False).value
            
            wb.close()
            app.quit()
            
            return data
            
        except Exception as e:
            print(f"Error reading with xlwings: {e}")
            return None
    
    def read_data_with_pandas(self, sheet_name=None):
        """Read data using pandas (fallback method)."""
        try:
            if sheet_name:
                data = pd.read_excel(self.excel_file, sheet_name=sheet_name)
            else:
                data = pd.read_excel(self.excel_file)
            return data
        except Exception as e:
            print(f"Error reading with pandas: {e}")
            return None
    
    def load_data(self, sheet_name=None, date_column=None, quantity_column=None, machine_column=None):
        """
        Load data from Excel file with automatic column detection.
        
        Args:
            sheet_name: Sheet name to read (None for first sheet)
            date_column: Date column name (auto-detected if None)
            quantity_column: Quantity column name (auto-detected if None)
            machine_column: Machine type column name (auto-detected if None)
        """
        print(f"Loading data from {self.excel_file}...")
        
        # Try xlwings first if requested, then fallback to pandas
        if self.use_xlwings:
            self.data = self.read_data_with_xlwings(sheet_name)
            if self.data is None:
                print("xlwings failed, falling back to pandas...")
                self.data = self.read_data_with_pandas(sheet_name)
        else:
            self.data = self.read_data_with_pandas(sheet_name)
        
        if self.data is None:
            raise ValueError("Could not load data from Excel file")
        
        print(f"Loaded {len(self.data)} rows with {len(self.data.columns)} columns")
        print(f"Columns: {list(self.data.columns)}")
        
        # Auto-detect columns if not specified
        if date_column is None:
            date_column = self.detect_date_column(self.data.columns)
        if quantity_column is None:
            quantity_column = self.detect_quantity_column(self.data.columns)
        if machine_column is None:
            machine_column = self.detect_machine_column(self.data.columns)
        
        # Validate required columns
        if date_column is None or date_column not in self.data.columns:
            raise ValueError(f"Date column not found. Available columns: {list(self.data.columns)}")
        
        self.date_column = date_column
        self.quantity_column = quantity_column
        self.machine_column = machine_column
        
        print(f"Using columns:")
        print(f"  Date: {self.date_column}")
        print(f"  Quantity: {self.quantity_column}")
        print(f"  Machine Type: {self.machine_column}")
        
        # Convert date column
        self.data[self.date_column] = pd.to_datetime(self.data[self.date_column])
        
        # Remove rows with invalid dates
        initial_count = len(self.data)
        self.data = self.data.dropna(subset=[self.date_column])
        final_count = len(self.data)
        
        if final_count < initial_count:
            print(f"Removed {initial_count - final_count} rows with invalid dates")
        
        return True
    
    def get_quarter_info(self, date):
        """Get quarter and year information for a date."""
        if pd.isna(date):
            return 'Unknown', 0, 0
        
        quarter = (date.month - 1) // 3 + 1
        return f"Q{quarter} {date.year}", date.year, quarter
    
    def analyze_timeline(self):
        """Analyze machine orders by quarter."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Add quarter information
        quarter_info = self.data[self.date_column].apply(
            lambda x: self.get_quarter_info(x)
        )
        
        self.data['Quarter'] = [info[0] for info in quarter_info]
        self.data['Year'] = [info[1] for info in quarter_info]
        self.data['Quarter_Num'] = [info[2] for info in quarter_info]
        
        # Aggregate data
        timeline_data = defaultdict(lambda: {
            'total_quantity': 0,
            'total_orders': 0,
            'machine_breakdown': defaultdict(int),
            'order_breakdown': defaultdict(int)
        })
        
        for _, row in self.data.iterrows():
            quarter = row['Quarter']
            quantity = 1  # Default quantity
            machine_type = 'Unknown Machine'
            
            # Get quantity if column exists
            if self.quantity_column and self.quantity_column in row:
                qty_val = row[self.quantity_column]
                if not pd.isna(qty_val):
                    quantity = int(qty_val)
            
            # Get machine type if column exists
            if self.machine_column and self.machine_column in row:
                machine_val = row[self.machine_column]
                if not pd.isna(machine_val):
                    machine_type = str(machine_val)
            
            # Update aggregates
            timeline_data[quarter]['total_quantity'] += quantity
            timeline_data[quarter]['total_orders'] += 1
            timeline_data[quarter]['machine_breakdown'][machine_type] += quantity
            timeline_data[quarter]['order_breakdown'][machine_type] += 1
        
        return timeline_data
    
    def print_timeline_report(self, timeline_data):
        """Print comprehensive timeline report."""
        print("\n" + "="*90)
        print("MACHINE ORDER QUARTERLY TIMELINE REPORT")
        print("="*90)
        
        # Sort quarters chronologically
        sorted_quarters = sorted(timeline_data.keys(), key=lambda x: (
            int(x.split()[1]) if len(x.split()) > 1 and x.split()[1].isdigit() else 0,
            int(x[1]) if x.startswith('Q') and len(x) > 1 and x[1].isdigit() else 0
        ))
        
        total_machines = 0
        total_orders = 0
        
        for quarter in sorted_quarters:
            data = timeline_data[quarter]
            quarter_machines = data['total_quantity']
            quarter_orders = data['total_orders']
            
            total_machines += quarter_machines
            total_orders += quarter_orders
            
            print(f"\n{quarter}:")
            print(f"  Total Machines to Order: {quarter_machines}")
            print(f"  Total Orders: {quarter_orders}")
            print(f"  Machine Breakdown by Quantity:")
            
            # Sort by quantity (descending)
            sorted_machines = sorted(
                data['machine_breakdown'].items(),
                key=lambda x: x[1], reverse=True
            )
            
            for machine_type, quantity in sorted_machines:
                orders = data['order_breakdown'][machine_type]
                print(f"    - {machine_type}: {quantity} machines ({orders} orders)")
        
        print(f"\n" + "-"*90)
        print(f"SUMMARY:")
        print(f"  Total Machines Across All Quarters: {total_machines}")
        print(f"  Total Orders Across All Quarters: {total_orders}")
        print(f"  Average Machines per Quarter: {total_machines/len(sorted_quarters):.1f}")
        print("-"*90)
    
    def export_timeline_report(self, output_file='machine_timeline_analysis.xlsx', timeline_data=None):
        """Export comprehensive timeline analysis to Excel."""
        if timeline_data is None:
            timeline_data = self.analyze_timeline()
        
        # Prepare summary data
        summary_rows = []
        detail_rows = []
        
        for quarter, data in timeline_data.items():
            # Summary
            summary_rows.append({
                'Quarter': quarter,
                'Total_Machines': data['total_quantity'],
                'Total_Orders': data['total_orders'],
                'Avg_Machines_Per_Order': data['total_quantity'] / max(data['total_orders'], 1)
            })
            
            # Details
            for machine_type, quantity in data['machine_breakdown'].items():
                orders = data['order_breakdown'][machine_type]
                detail_rows.append({
                    'Quarter': quarter,
                    'Machine_Type': machine_type,
                    'Total_Quantity': quantity,
                    'Number_of_Orders': orders,
                    'Avg_Quantity_Per_Order': quantity / max(orders, 1)
                })
        
        # Create DataFrames
        summary_df = pd.DataFrame(summary_rows)
        detail_df = pd.DataFrame(detail_rows)
        
        # Export to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Quarterly_Summary', index=False)
            detail_df.to_excel(writer, sheet_name='Machine_Breakdown', index=False)
            
            # Add source data with quarter info
            if self.data is not None:
                self.data.to_excel(writer, sheet_name='Source_Data_with_Quarters', index=False)
        
        print(f"\nDetailed timeline analysis exported to {output_file}")
        return output_file

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description='Machine Order Timeline Analyzer using xlwings lite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s machine_orders.xlsx
  %(prog)s data.xlsx --date-col "Purchase Date" --quantity-col "Qty"
  %(prog)s orders.xlsx --sheet "Sheet2" --machine-col "Equipment Type"
        """
    )
    
    parser.add_argument('excel_file', help='Path to Excel file containing machine order data')
    parser.add_argument('--sheet', help='Sheet name to read (default: first sheet)')
    parser.add_argument('--date-col', help='Date column name (auto-detected if not specified)')
    parser.add_argument('--quantity-col', help='Quantity column name (auto-detected if not specified)')
    parser.add_argument('--machine-col', help='Machine type column name (auto-detected if not specified)')
    parser.add_argument('--output', help='Output Excel file name', default='machine_timeline_analysis.xlsx')
    parser.add_argument('--use-xlwings', action='store_true', help='Use xlwings instead of pandas')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.excel_file):
        print(f"Error: File {args.excel_file} not found")
        return 1
    
    try:
        print("Machine Order Timeline Analyzer (Enhanced)")
        print(f"Input file: {args.excel_file}")
        print(f"Using xlwings: {args.use_xlwings and XLWINGS_AVAILABLE}")
        
        # Initialize analyzer
        analyzer = MachineOrderTimelineAnalyzer(args.excel_file, args.use_xlwings)
        
        # Load data
        analyzer.load_data(
            sheet_name=args.sheet,
            date_column=args.date_col,
            quantity_column=args.quantity_col,
            machine_column=args.machine_col
        )
        
        # Analyze timeline
        timeline_data = analyzer.analyze_timeline()
        
        # Print report
        analyzer.print_timeline_report(timeline_data)
        
        # Export to Excel
        analyzer.export_timeline_report(args.output, timeline_data)
        
        print(f"\nAnalysis complete! Results saved to {args.output}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())