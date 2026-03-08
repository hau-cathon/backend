"""Prosty test ekstraktor pól zwierzęcych - bez serwera"""
from app.utils.animal_field_extractor import AnimalFieldExtractor

def test_examples():
    extractor = AnimalFieldExtractor()
    
    test_cases = [
        "Widzę zbłąkanego psa przy ulicy Głównej 15. Wygląda na wychudzonego i kuleje.",
        "Ranny kot w parku przy ul. Kwiatowej. Krwawi z łapy.",
        "Na balkonie sąsiada jest pies bez wody w upalny dzień.",
        "Znalazłem rannego pawia na drodze koło lasu",
        "Dzikie szczury w piwnicy przy ul. Słonecznej 5"
    ]
    
    print("=" * 80)
    print("TEST EKSTRAKTORA PÓL ZWIERZĘCYCH")
    print("=" * 80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}:")
        print(f"Tekst: {text}")
        print("-" * 80)
        
        result = extractor.extract_all_fields(text)
        
        print(f"\n📋 Gatunek: {result['species']}")
        if result['species']:
            print(f"   Label: {extractor.get_species_label(result['species'])}")
        
        print(f"\n📍 Lokalizacja: {result['location']}")
        
        print(f"\n🚨 Typy incydentów: {result['incident_types']}")
        if result['incident_types']:
            for inc_type in result['incident_types']:
                print(f"   - {extractor.get_incident_type_label(inc_type)}")
        
        print(f"\n📝 Opis: {result['description']}")
        
        print(f"\n{'='*80}")
    
    print("\n\n✅ Test zakończony!")

if __name__ == "__main__":
    test_examples()
