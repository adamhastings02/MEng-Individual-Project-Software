from datetime import datetime

def change_date_format(date_str):
    try:
        # Attempt to parse the date string as mm/dd/yyyy
        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        # Format the date object as dd/mm/yyyy
        new_date_str = date_obj.strftime('%d/%m/%Y')
        return new_date_str
    except ValueError:
        # If parsing fails, return the original string
        return date_str

# Test the function
date_str = '12/25/2023'
new_date_str = change_date_format(date_str)
print(new_date_str)  # Output: '25/12/2023'

# Test the function
date_str = '12/02/2023'
new_date_str = change_date_format(date_str)
print(new_date_str)