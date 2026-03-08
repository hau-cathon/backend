"""Test API response for animal_count"""
from app.utils.animal_field_extractor import AnimalFieldExtractor

def test_api_response():
    extractor = AnimalFieldExtractor()
    
    test_text = "Jest tam wiele psów, są głodne i wychudzone, adres polna 64."
    
    # Test extract_all_fields
    print("=" * 80)
    print("TEST: extract_all_fields")
    print("=" * 80)
    result = extractor.extract_all_fields(test_text)
    print(f"Text: {test_text}")
    print(f"\nResult keys: {result.keys()}")
    print(f"Animal count: {result.get('animal_count', 'BRAK')}")
    print()
    
    # Test extract_all_fields_with_confidence
    print("=" * 80)
    print("TEST: extract_all_fields_with_confidence")
    print("=" * 80)
    result_conf = extractor.extract_all_fields_with_confidence(test_text)
    print(f"Text: {test_text}")
    print(f"\nResult fields keys: {result_conf['fields'].keys()}")
    print(f"Animal count: {result_conf['fields'].get('animal_count', {}).get('value', 'BRAK')}")
    print(f"Animal count confidence: {result_conf['fields'].get('animal_count', {}).get('confidence', 'BRAK')}")
    print()
    
    # Symulacja response API
    print("=" * 80)
    print("SYMULACJA RESPONSE API")
    print("=" * 80)
    animal_fields_with_confidence = result_conf
    
    api_response = {
        'animal_fields': {
            'species': animal_fields_with_confidence['fields']['species']['value'],
            'location': animal_fields_with_confidence['fields']['location']['value'],
            'incident_types': animal_fields_with_confidence['fields']['incident_types']['value'],
            'description': animal_fields_with_confidence['fields']['description']['value'],
            'caller_name': animal_fields_with_confidence['fields']['caller_name']['value'],
            'caller_phone': animal_fields_with_confidence['fields']['caller_phone']['value'],
            'animal_count': animal_fields_with_confidence['fields']['animal_count']['value'],
            'animal_count_confidence': animal_fields_with_confidence['fields']['animal_count']['confidence']
        }
    }
    
    print(f"API Response animal_count: {api_response['animal_fields']['animal_count']}")
    print(f"API Response animal_count_confidence: {api_response['animal_fields']['animal_count_confidence']:.2f}")
    print()

if __name__ == "__main__":
    test_api_response()
