import requests
from geopy.geocoders import Nominatim

def test_polish_streets():
    """Test Nominatim geocoding for Polish streets"""
    geolocator = Nominatim(user_agent="nominatim_test")
    
    test_addresses = [
        "Krakowskie Przedmieście, Warszawa, Poland",
        "Mariensztat 1, Warszawa, Poland",
        "Mariensztat 30, Warszawa, Poland",
        "Nowy Świat 3, Warszawa, Poland",
        "Główny Urząd Statystyczny, Warszawa, Poland",
        "ul. Floriańska 13, Kraków, Poland",
        "Rynek Główny, Kraków, Poland",
        "ul. Lipowa 75, Rumia, Poland",
        "ul. Mostowa 10, Rumia, Poland",
        "ul. Subisława 70, Gdańsk, Poland",
        "ul. Subisława 30, Gdańsk, Poland",
    ]
    
    for address in test_addresses:
        try:
            location = geolocator.geocode(address)
            if location:
                print(f"✓ {address}")
                print(f"  Latitude: {location.latitude}, Longitude: {location.longitude}")
            else:
                print(f"✗ {address} - Not found")
        except Exception as e:
            print(f"✗ {address} - Error: {str(e)}")

if __name__ == "__main__":
    test_polish_streets()