#!/usr/bin/env python3
"""
Create sample machine order data for testing the xlwings timeline solution.
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_machine_orders():
    """Create sample machine order data with dates spanning multiple quarters."""
    
    # Define machine types
    machine_types = [
        'CNC Lathe',
        'Milling Machine', 
        'Drill Press',
        'Grinder',
        'Press Machine',
        'Welding Robot',
        'Assembly Line Robot',
        'Quality Control Scanner'
    ]
    
    # Generate sample data
    orders = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(50):  # Create 50 sample orders
        # Random date within 2024-2025
        days_offset = random.randint(0, 730)  # 2 years
        order_date = start_date + timedelta(days=days_offset)
        
        order = {
            'Order ID': f'ORD-{1000 + i}',
            'Machine Type': random.choice(machine_types),
            'Order Date': order_date,
            'Quantity': random.randint(1, 5),
            'Priority': random.choice(['High', 'Medium', 'Low']),
            'Department': random.choice(['Production', 'Maintenance', 'Quality', 'Assembly']),
            'Cost': random.randint(50000, 500000)
        }
        orders.append(order)
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(orders)
    df = df.sort_values('Order Date')
    
    # Save to Excel file
    output_file = 'machine_orders.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Sample machine order data created in {output_file}")
    print(f"Generated {len(orders)} orders from {df['Order Date'].min()} to {df['Order Date'].max()}")
    print("\nFirst few rows:")
    print(df.head())
    
    return output_file

if __name__ == "__main__":
    create_sample_machine_orders()