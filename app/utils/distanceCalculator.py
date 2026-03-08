from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from flask import current_app
import re


def validate_address_format(address):
    """
    Validate address has city, street, and number components.
    Expected format: "City Street Number" or "Street Number, City"
    
    Args:
        address: string like "Kraków Pulaskiego 10" or "Gdańsk Subisława 50" or "ul. Pulaskiego 10, Kraków"
    
    Returns:
        tuple: (is_valid: bool, address_parts: dict)
    """
    if not address or not isinstance(address, str):
        return False, {}
    
    address = address.strip()
    
    # Remove common prefixes
    cleaned = re.sub(r'^(ul\.|ul|ulica|al\.|al|aleja|plac|pl\.)\s*', '', address, flags=re.IGNORECASE).strip()
    
    # Try to parse address components
    # Look for patterns with comma separation (Polish format: "Street number, City")
    if ',' in cleaned:
        parts = [p.strip() for p in cleaned.split(',')]
        if len(parts) >= 2:
            # Last part is usually city
            city = parts[-1]
            street_part = ' '.join(parts[:-1])
            has_number = bool(re.search(r'\d', street_part))
        else:
            return False, {}
    else:
        # No comma - format is "City Street Number"
        parts = cleaned.split()
        if len(parts) < 3:  # Need at least city, street, number
            return False, {}
        
        # Last part should be number
        if not re.search(r'\d', parts[-1]):
            return False, {}
        
        # First part is city, remaining parts form street with number
        city = parts[0]
        street_part = ' '.join(parts[1:])  # Everything after city
        has_number = True  # We already checked last part has digit
    
    # Validate we have all components
    has_city = len(city) > 1
    has_street = len(street_part) > 1
    
    is_valid = has_city and has_street and has_number
    
    return is_valid, {
        'city': city if has_city else None,
        'street': street_part if has_street else None,
        'has_number': has_number
    }


def calculate_distance(loc1, loc2):
    """
    Calculate distance between two locations.
    Also returns confidence levels to check if geocoding was accurate.
    
    Args:
        loc1: dict with 'x','y' OR 'address'
        loc2: dict with 'x','y' OR 'address'
    
    Returns:
        tuple: (distance_km, confidence1, confidence2)
        confidence: 'coordinates' (exact coords), 'full' (street+number), 'city', 'partial'
    """
    
    # Get coordinates for location 1
    if 'x' in loc1 and 'y' in loc1:
        coords_1 = (float(loc1['x']), float(loc1['y']))
        conf_1 = 'coordinates'
    elif 'address' in loc1:
        result = _geocode_address(loc1['address'])
        coords_1 = (result[0], result[1])
        conf_1 = result[2]  # Extract confidence level
    else:
        raise ValueError("Location 1 must have 'x','y' or 'address' field")
    
    # Get coordinates for location 2
    if 'x' in loc2 and 'y' in loc2:
        coords_2 = (float(loc2['x']), float(loc2['y']))
        conf_2 = 'coordinates'
    elif 'address' in loc2:
        result = _geocode_address(loc2['address'])
        coords_2 = (result[0], result[1])
        conf_2 = result[2]  # Extract confidence level
    else:
        raise ValueError("Location 2 must have 'x','y' or 'address' field")
    
    # Calculate distance
    distance = geodesic(coords_1, coords_2).km
    return distance, conf_1, conf_2


def _geocode_address(address):
    """
    Convert address string to coordinates (lat, lng).
    Tries full address first, then partial matches.
    Returns confidence level to track geocoding accuracy.
    
    Args:
        address: string like "ul. Pulaskiego 10, Kraków"
    
    Returns:
        tuple: (latitude, longitude, confidence_level)
        confidence_level: 'full' (street+number), 'city' (city only), 'partial' (first word)
    """
    try:
        geolocator = Nominatim(user_agent="pieski_app", timeout=5)
        
        # Add Poland to address if not already there
        search_address = address
        if 'poland' not in address.lower() and 'polska' not in address.lower():
            search_address = f"{address}, Poland"
        
        # Try full address first
        location = geolocator.geocode(search_address, timeout=5)
        
        if location:
            current_app.logger.info(f"Geocoded (FULL) '{search_address}' -> ({location.latitude}, {location.longitude})")
            return (location.latitude, location.longitude, 'full')
        
        # If full address fails, try with only city
        parts = address.split(',')
        if len(parts) > 1:
            city = parts[-1].strip()
        else:
            # No comma - try first word as city
            words = address.split()
            city = words[0] if words else ""
        
        if city and 'poland' not in city.lower():
            city_search = f"{city}, Poland"
        else:
            city_search = city
        
        if city_search:
            current_app.logger.warning(
                f"Full address '{address}' not found, trying with city only: '{city_search}'"
            )
            location = geolocator.geocode(city_search, timeout=5)
            
            if location:
                current_app.logger.info(
                    f"Geocoded (CITY ONLY) '{city_search}' -> ({location.latitude}, {location.longitude})"
                )
                return (location.latitude, location.longitude, 'city')
        
        # If still not found, try just the first word
        first_word = address.split()[0] if address else ""
        if first_word and len(first_word) > 1:
            current_app.logger.warning(
                f"City not found, trying first word: '{first_word}'"
            )
            location = geolocator.geocode(f"{first_word}, Poland", timeout=5)
            
            if location:
                current_app.logger.info(
                    f"Geocoded (FIRST WORD) '{first_word}' -> ({location.latitude}, {location.longitude})"
                )
                return (location.latitude, location.longitude, 'partial')
        
        # If all else fails, log and raise error
        current_app.logger.error(f"Could not geocode address: {address}")
        raise ValueError(f"Address not found: {address}")
            
    except ValueError:
        raise
    except Exception as e:
        current_app.logger.error(f"Geocoding error for '{address}': {str(e)}")
        raise