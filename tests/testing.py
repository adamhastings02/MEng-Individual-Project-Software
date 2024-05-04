import pandas as pd
import re

# Sample DataFrame with dates in MM/DD/YYYY format
data = {'Date': ['12/31/2022', '03/15/2023', '07/04/2024', '11/05/2025']}
df = pd.DataFrame(data)

# Function to convert dates from MM/DD/YYYY to DD/MM/YYYY if the day part is between 13 and 31
def convert_date(date_str):
    # Regular expression to match MM/DD/YYYY format
    mm_dd_yyyy_pattern = r'(\d{2})/(\d{2})/(\d{4})'
    # Check if the date matches MM/DD/YYYY format
    if re.match(mm_dd_yyyy_pattern, date_str):
        # If it matches, extract month, day, and year
        month, day, year = re.match(mm_dd_yyyy_pattern, date_str).groups()
        # Check if the day part is between 13 and 31
        if 13 <= int(day) <= 31:
            # Return the date in DD/MM/YYYY format
            return f'{day}/{month}/{year}'
    # If the date does not match the condition, return as is
    return date_str

# Apply the conversion function to the Date column
df['Date'] = df['Date'].apply(convert_date)

# Display the DataFrame with converted dates
print(df)