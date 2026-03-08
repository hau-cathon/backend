"""Test comprehensive scenarios"""
from app.utils.animal_field_extractor import AnimalFieldExtractor

def test_comprehensive():
    extractor = AnimalFieldExtractor()
    
    print("=" * 80)
    print("TESTY KOMPLEKSOWE")
    print("=" * 80)
    
    test_scenarios = [
        {
            "name": "Kilka psów - wypadek",
            "text": "Dzień dobry, widzę kilka psów na ulicy Głównej 15. Jeden z nich został potrącony przez samochód i krwawi. Mój numer to 555-123-456"
        },
        {
            "name": "Parę kotów - bez polskich znaków",
            "text": "Widze pare kotow na parkingu. Sa chore i slabe. Moj numer 600.700.800"
        },
        {
            "name": "Wiele zwierząt - zaniedbane",
            "text": "Jest tam wiele psów w złym stanie. Są wychudzone i głodne. Adres: ul. Polna 34"
        },
        {
            "name": "Pojedyncze zwierzę - ranne po wypadku",
            "text": "Pies leży na jezdni i nie może się ruszyć. Wygląda jakby miał złamaną nogę po wypadku samochodowym. Nazywam się Jan Kowalski, tel 123-456-789"
        },
        {
            "name": "Grupa zwierząt - agresywne",
            "text": "Grupa 4 psów atakuje ludzi na ulicy Jasnej. Są bardzo agresywne i szczekają."
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 80)
        result = extractor.extract_all_fields_with_confidence(scenario['text'])
        
        print(f"Text: {scenario['text']}")
        print(f"\nWyniki:")
        print(f"  Gatunek: {result['fields']['species']['value']} (conf: {result['fields']['species']['confidence']:.2f})")
        print(f"  Ilość: {result['fields']['animal_count']['value']} (conf: {result['fields']['animal_count']['confidence']:.2f})")
        print(f"  Typy: {result['fields']['incident_types']['value']} (conf: {result['fields']['incident_types']['confidence']:.2f})")
        print(f"  Lokalizacja: {result['fields']['location']['value']} (conf: {result['fields']['location']['confidence']:.2f})")
        print(f"  Imię: {result['fields']['caller_name']['value']} (conf: {result['fields']['caller_name']['confidence']:.2f})")
        print(f"  Telefon: {result['fields']['caller_phone']['value']} (conf: {result['fields']['caller_phone']['confidence']:.2f})")
        print(f"\n  Overall confidence: {result['overall_confidence']:.2f}")
        print(f"  Should auto-fill: {result['should_auto_fill']}")

if __name__ == "__main__":
    test_comprehensive()
