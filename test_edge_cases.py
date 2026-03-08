"""Test edge cases for animal field extractor"""
from app.utils.animal_field_extractor import AnimalFieldExtractor

def test_edge_cases():
    extractor = AnimalFieldExtractor()
    
    print("=" * 80)
    print("TEST 1: Numer telefonu z kropkami")
    print("=" * 80)
    text1 = "Mój numer to 353.123.231"
    result1 = extractor.extract_all_fields_with_confidence(text1)
    print(f"Text: {text1}")
    print(f"Phone: {result1['fields']['caller_phone']['value']}")
    print(f"Confidence: {result1['fields']['caller_phone']['confidence']:.2f}")
    print()
    
    print("=" * 80)
    print("TEST 2: Długa nazwa ulicy z numerem")
    print("=" * 80)
    text2 = "Mam na imię Piotr Kowalski. Mój kot aktualnie krwawi z powodu wypadku samochodowego na ulicy Aleja Grunwaldzka 252, obok Uniwersytetu Gdańskiego. Mój numer telefonu to 303-303-707."
    result2 = extractor.extract_all_fields_with_confidence(text2)
    print(f"Text: {text2}")
    print(f"Caller name: {result2['fields']['caller_name']['value']}")
    print(f"Location: {result2['fields']['location']['value']}")
    print(f"Phone: {result2['fields']['caller_phone']['value']}")
    print()
    
    print("=" * 80)
    print("TEST 3: Błędne wykrycie nazwiska po 'obok'")
    print("=" * 80)
    text3 = "Jest tam obok Uniwersytetu Gdańskiego"
    result3 = extractor.extract_all_fields_with_confidence(text3)
    print(f"Text: {text3}")
    print(f"Caller name (should be None): {result3['fields']['caller_name']['value']}")
    print(f"Location: {result3['fields']['location']['value']}")
    print()
    
    print("=" * 80)
    print("TEST 4: 'Tutaj' nie powinno być adresem")
    print("=" * 80)
    text4 = "Dzień dobry, tutaj Karol Nawrodzki. Mam wrażenie, że mój sąsiad na ulicy Grunwaldzkiej 303 znęca się nad swoim zwierzęciem. Pies ma bardzo krótki łańcuch, nie wiem co zrobić. Mój numer telefonu to 303-555-000."
    result4 = extractor.extract_all_fields_with_confidence(text4)
    print(f"Text: {text4}")
    print(f"Caller name: {result4['fields']['caller_name']['value']}")
    print(f"Location: {result4['fields']['location']['value']}")
    print(f"Phone: {result4['fields']['caller_phone']['value']}")
    print()
    
    print("=" * 80)
    print("TEST 5: Wykrywanie ilości zwierząt")
    print("=" * 80)
    
    test_animal_counts = [
        "Widzę jednego psa na ulicy",
        "Są tam dwa koty",
        "Widzę trzy psy",
        "Jest tam kilka kotów",
        "Jest tam pies",
        "Jest grupa 5 psów",
    ]
    
    for text in test_animal_counts:
        result = extractor.extract_all_fields_with_confidence(text)
        count = result['fields']['animal_count']['value']
        conf = result['fields']['animal_count']['confidence']
        print(f"Text: {text}")
        print(f"  Count: {count}, Confidence: {conf:.2f}")
    print()

if __name__ == "__main__":
    test_edge_cases()
