#!/usr/bin/env python3
"""
XLWings Lite Solution for Machine Order Timeline Analysis

This script reads machine order data from an Excel file and provides quarterly
timeline analysis showing how many machines are ordered per quarter.

Requirements:
- Excel file with 'Order Date' column (or similar date column)
- Machine/quantity data for aggregation
"""

import xlwings as xw
import pandas as pd
from datetime import datetime
from collections import defaultdict
import sys

class MachineOrderAnalyzer:
    """Analyze machine orders and generate quarterly timeline reports."""
    
    def __init__(self, excel_file):
        """Initialize with Excel file path."""
        self.excel_file = excel_file
        self.data = None
        
    def read_excel_data(self, sheet_name=None, date_column='Order Date'):
        """
        Read data from Excel file using xlwings lite approach.
        
        Args:
            sheet_name: Name of sheet to read (None for active sheet)
            date_column: Name of the date column to use for timeline analysis
        """
        try:
            # Open workbook with xlwings
            wb = xw.Book(self.excel_file)
            
            if sheet_name:
                ws = wb.sheets[sheet_name]
            else:
                ws = wb.sheets.active
            
            # Get used range
            used_range = ws.used_range
            
            # Read data as pandas DataFrame
            self.data = used_range.options(pd.DataFrame, header=1, index=False).value
            
            print(f"Successfully read {len(self.data)} rows from {self.excel_file}")
            print(f"Columns: {list(self.data.columns)}")
            
            # Ensure date column exists
            if date_column not in self.data.columns:
                available_date_cols = [col for col in self.data.columns if 'date' in col.lower()]
                if available_date_cols:
                    date_column = available_date_cols[0]
                    print(f"Date column '{date_column}' not found. Using '{date_column}' instead.")
                else:
                    raise ValueError(f"No date column found. Available columns: {list(self.data.columns)}")
            
            # Convert date column to datetime
            self.data[date_column] = pd.to_datetime(self.data[date_column])
            self.date_column = date_column
            
            wb.close()
            return True
            
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return False
    
    def read_excel_data_fallback(self, sheet_name=None, date_column='Order Date'):
        """
        Fallback method using pandas directly (when xlwings has issues).
        
        Args:
            sheet_name: Name of sheet to read (None for first sheet)
            date_column: Name of the date column to use for timeline analysis
        """
        try:
            # Read with pandas as fallback
            if sheet_name:
                self.data = pd.read_excel(self.excel_file, sheet_name=sheet_name)
            else:
                self.data = pd.read_excel(self.excel_file)
            
            print(f"Successfully read {len(self.data)} rows from {self.excel_file}")
            print(f"Columns: {list(self.data.columns)}")
            
            # Find date column
            if date_column not in self.data.columns:
                available_date_cols = [col for col in self.data.columns if 'date' in col.lower()]
                if available_date_cols:
                    date_column = available_date_cols[0]
                    print(f"Using date column: '{date_column}'")
                else:
                    raise ValueError(f"No date column found. Available columns: {list(self.data.columns)}")
            
            # Convert date column to datetime
            self.data[date_column] = pd.to_datetime(self.data[date_column])
            self.date_column = date_column
            
            return True
            
        except Exception as e:
            print(f"Error reading Excel file with fallback method: {e}")
            return False
    
    def get_quarter(self, date):
        """Get quarter string for a given date."""
        if pd.isna(date):
            return 'Unknown'
        quarter = (date.month - 1) // 3 + 1
        return f"Q{quarter} {date.year}"
    
    def analyze_quarterly_timeline(self, quantity_column='Quantity', machine_column='Machine Type'):
        """
        Analyze machine orders by quarter.
        
        Args:
            quantity_column: Column containing quantity data
            machine_column: Column containing machine type data
        """
        if self.data is None:
            print("No data loaded. Please read Excel data first.")
            return None
        
        # Add quarter column
        self.data['Quarter'] = self.data[self.date_column].apply(self.get_quarter)
        
        # Aggregate by quarter
        quarterly_summary = defaultdict(lambda: {'total_machines': 0, 'machine_types': defaultdict(int)})
        
        for _, row in self.data.iterrows():
            quarter = row['Quarter']
            quantity = row.get(quantity_column, 1)  # Default to 1 if no quantity column
            machine_type = row.get(machine_column, 'Unknown Machine')
            
            # Handle NaN quantities
            if pd.isna(quantity):
                quantity = 1
                
            quarterly_summary[quarter]['total_machines'] += int(quantity)
            quarterly_summary[quarter]['machine_types'][machine_type] += int(quantity)
        
        return quarterly_summary
    
    def generate_timeline_report(self, quantity_column='Quantity', machine_column='Machine Type'):
        """Generate and display quarterly timeline report."""
        
        quarterly_data = self.analyze_quarterly_timeline(quantity_column, machine_column)
        
        if not quarterly_data:
            return
        
        print("\n" + "="*80)
        print("MACHINE ORDER QUARTERLY TIMELINE REPORT")
        print("="*80)
        
        # Sort quarters chronologically
        sorted_quarters = sorted(quarterly_data.keys(), key=lambda x: (
            int(x.split()[1]) if len(x.split()) > 1 else 0,  # Year
            int(x[1]) if x.startswith('Q') else 0  # Quarter number
        ))
        
        total_machines_all = 0
        
        for quarter in sorted_quarters:
            data = quarterly_data[quarter]
            total_machines = data['total_machines']
            total_machines_all += total_machines
            
            print(f"\n{quarter}:")
            print(f"  Total Machines to Order: {total_machines}")
            print(f"  Machine Types:")
            
            # Sort machine types by quantity (descending)
            sorted_machines = sorted(data['machine_types'].items(), 
                                   key=lambda x: x[1], reverse=True)
            
            for machine_type, count in sorted_machines:
                print(f"    - {machine_type}: {count}")
        
        print(f"\n" + "-"*80)
        print(f"TOTAL MACHINES ACROSS ALL QUARTERS: {total_machines_all}")
        print("-"*80)
        
        return quarterly_data
    
    def export_timeline_to_excel(self, output_file='machine_timeline_report.xlsx'):
        """Export timeline analysis to Excel file."""
        
        quarterly_data = self.analyze_quarterly_timeline()
        
        if not quarterly_data:
            return False
        
        # Prepare data for Excel export
        summary_data = []
        detail_data = []
        
        for quarter, data in quarterly_data.items():
            # Summary row
            summary_data.append({
                'Quarter': quarter,
                'Total Machines': data['total_machines']
            })
            
            # Detail rows
            for machine_type, count in data['machine_types'].items():
                detail_data.append({
                    'Quarter': quarter,
                    'Machine Type': machine_type,
                    'Quantity': count
                })
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Quarterly Summary', index=False)
            
            # Detail sheet
            detail_df = pd.DataFrame(detail_data)
            detail_df.to_excel(writer, sheet_name='Detailed Breakdown', index=False)
            
            # Original data with quarters
            self.data.to_excel(writer, sheet_name='Source Data', index=False)
        
        print(f"\nTimeline report exported to {output_file}")
        return True

def main():
    """Main function to run the machine order timeline analysis."""
    
    # Default to sample file if no argument provided
    excel_file = 'machine_orders.xlsx'
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    
    print(f"Machine Order Timeline Analyzer")
    print(f"Input file: {excel_file}")
    
    # Initialize analyzer
    analyzer = MachineOrderAnalyzer(excel_file)
    
    # Try to read data with xlwings first, then fallback to pandas
    success = analyzer.read_excel_data_fallback()  # Using fallback for broader compatibility
    
    if not success:
        print("Failed to read Excel data. Please check the file and try again.")
        return
    
    # Generate timeline report
    analyzer.generate_timeline_report()
    
    # Export to Excel
    analyzer.export_timeline_to_excel()

if __name__ == "__main__":
    main()