import re
from typing import Dict, Any, Optional
from datetime import datetime

def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number format"""
    pattern = r'^\+?[1-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_time(time_str: str) -> bool:
    """Validate time format (HH:MM)"""
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def format_booking_details(booking: Dict[str, Any]) -> str:
    """Format booking details for display"""
    return f"""
    Restaurant: {booking.get('restaurant', 'N/A')}
    Date: {booking.get('date', 'N/A')}
    Time: {booking.get('time', 'N/A')}
    Guests: {booking.get('guests', 'N/A')}
    Contact: {booking.get('contact', 'N/A')}
    """

def generate_booking_reference() -> str:
    """Generate a unique booking reference"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join([str(ord(c)) for c in timestamp[-4:]])
    return f"BN{timestamp}{random_suffix}"

def parse_user_input(input_text: str) -> Dict[str, Any]:
    """Parse user input to extract relevant information"""
    result = {
        'date': None,
        'time': None,
        'guests': None,
        'contact': None
    }
    
    # Extract date (YYYY-MM-DD format)
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', input_text)
    if date_match:
        result['date'] = date_match.group()
    
    # Extract time (HH:MM format)
    time_match = re.search(r'\d{2}:\d{2}', input_text)
    if time_match:
        result['time'] = time_match.group()
    
    # Extract number of guests
    guests_match = re.search(r'(\d+)\s*(?:guests?|people|persons?)', input_text.lower())
    if guests_match:
        result['guests'] = int(guests_match.group(1))
    
    # Extract phone number
    phone_match = re.search(r'\+?[1-9]\d{9}', input_text)
    if phone_match:
        result['contact'] = phone_match.group()
    
    return result

def calculate_booking_duration(start_time: str, end_time: str) -> float:
    """Calculate duration of booking in hours"""
    try:
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        duration = (end - start).total_seconds() / 3600
        return round(duration, 2)
    except ValueError:
        return 0.0

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove any potentially harmful characters
    sanitized = re.sub(r'[<>{}[\]\\]', '', text)
    return sanitized.strip()

def format_currency(amount: float) -> str:
    """Format amount in Indian Rupees"""
    return f"₹{amount:,.2f}"

def get_time_slot(time: str) -> str:
    """Get time slot (Morning/Afternoon/Evening/Night)"""
    hour = int(time.split(':')[0])
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 22:
        return "Evening"
    else:
        return "Night" 