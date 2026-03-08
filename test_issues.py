"""Test reported issues"""
from app.utils.animal_field_extractor import AnimalFieldExtractor

def test_issues():
    extractor = AnimalFieldExtractor()
    
    print("=" * 80)
    print("TEST: Kilka zwierząt - różne warianty")
    print("=" * 80)
    
    test_cases = [
        "Widzę kilka psów na ulicy",
        "Jest tam kilka kotów",
        "Są tam kilka zwierząt",
        "Kilka psów biega po parku",
        "Na ulicy jest parę psów",
        "Widzę pare kotów",
        "Wiele psów jest tam",
        "Jest tam dużo kotów",
    ]
    
    for text in test_cases:
        result = extractor.extract_all_fields_with_confidence(text)
        count = result['fields']['animal_count']['value']
        conf = result['fields']['animal_count']['confidence']
        print(f"Text: {text}")
        print(f"  Count: {count}, Confidence: {conf:.2f}")
        if count == 1:
            print(f"  ⚠️  PROBLEM: Wykryto 1 zamiast kilku!")
    print()
    
    print("=" * 80)
    print("TEST: Typy zdarzeń - domyślne wykrywanie")
    print("=" * 80)
    
    incident_tests = [
        "Pies jest ranny",
        "Kot krwawi",
        "Zwierzę zostało potrącone przez samochód",
        "Pies leży na ulicy i nie może się ruszyć",
        "Kot jest chory",
        "Zwierzę ma ranę",
        "Pies został ugryzione przez inne zwierzę",
        "Kot jest słaby i nie może chodzić",
    ]
    
    for text in incident_tests:
        result = extractor.extract_all_fields_with_confidence(text)
        types = result['fields']['incident_types']['value']
        conf = result['fields']['incident_types']['confidence']
        print(f"Text: {text}")
        print(f"  Types: {types}, Confidence: {conf:.2f}")
    print()

if __name__ == "__main__":
    test_issues()
