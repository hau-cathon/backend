"""Speech to text routes"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
from app.utils.speech_to_text import get_stt_service
from app.utils.keyword_extractor import KeywordExtractor
from app.utils.animal_field_extractor import AnimalFieldExtractor
from app.utils.duplicate_detector import DuplicateDetector
from app.models.issue import Issue

stt_bp = Blueprint('stt', __name__)

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def map_incident_to_priority(incident_types, default_priority=1):
    """
    Maps incident types to priority levels
    
    Args:
        incident_types: list of incident type strings
        default_priority: fallback priority if no mapping found
        
    Returns:
        int: priority (0=low, 1=medium, 2=critical) or None if no override
    """
    if not incident_types:
        return None
    
    # Priority mapping for animal incidents
    INCIDENT_PRIORITY_MAP = {
        'ranny': 2,        # Injured animal - critical
        'martwy': 2,       # Dead animal - critical
        'agresywny': 2,    # Aggressive - critical (safety risk)
        'zamkniety': 1,    # Trapped - medium
        'glodny': 1,       # Hungry/neglected - medium
        'zablakany': 0,    # Stray - low
    }
    
    # Get highest priority from all detected incident types
    priorities = [INCIDENT_PRIORITY_MAP.get(itype) for itype in incident_types if itype in INCIDENT_PRIORITY_MAP]
    
    if priorities:
        return max(priorities)  # Return highest priority
    
    return None  # No override


@stt_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transkrybuje plik audio i analizuje treść
    
    Form data:
        audio: plik audio
        language: język (domyślnie 'pl')
        analyze: czy analizować treść (domyślnie true)
    """
    try:
        # Sprawdź czy plik został wysłany
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'error': 'Brak pliku audio'
            }), 400
        
        file = request.files['audio']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'error': 'Nie wybrano pliku'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'error': f'Niedozwolony format. Dozwolone: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Parametry
        language = request.form.get('language', 'pl')
        analyze = request.form.get('analyze', 'true').lower() == 'true'
        
        # Zapisz tymczasowo
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Transkrybuj
            stt = get_stt_service()
            result = stt.transcribe_file(tmp_path, language=language)
            
            response_data = {
                'status': 'success',
                'transcription': result['text'],
                'language': result['language'],
                'segments': result['segments']
            }
            
            # Analiza treści
            if analyze and result['text']:
                keyword_extractor = KeywordExtractor()
                animal_extractor = AnimalFieldExtractor()
                
                # Wyciągnij słowa kluczowe
                keywords = keyword_extractor.extract_keywords(result['text'])
                
                # Podświetl tekst
                highlighted = keyword_extractor.highlight_keywords(result['text'])
                
                # Sugeruj priorytet (na podstawie słów kluczowych)
                priority_suggestion = keyword_extractor.suggest_priority(result['text'])
                
                # Wyciągnij encje
                entities = keyword_extractor.extract_entities(result['text'])
                
                # NOWE: Wyciągnij pola zwierzęce z confidence
                animal_fields_with_confidence = animal_extractor.extract_all_fields_with_confidence(result['text'])
                
                # Get ML priority prediction with confidence
                from app.utils.model_predictor import predict_priority_with_confidence
                priority_prediction = predict_priority_with_confidence(result['text'])
                
                # Map incident types to priority (fallback/override)
                incident_types = animal_fields_with_confidence['fields']['incident_types']['value']
                incident_priority = map_incident_to_priority(incident_types, priority_prediction.get('prediction', 1))
                
                # Use incident-based priority if we have high confidence in incident type
                incident_conf = animal_fields_with_confidence['fields']['incident_types']['confidence']
                if incident_conf >= 0.90 and incident_priority is not None:
                    # Override ML prediction with rule-based priority
                    priority_prediction['prediction'] = incident_priority
                    priority_prediction['confidence'] = max(priority_prediction.get('confidence', 0.0), 0.85)
                    priority_prediction['priority'] = {
                        2: "potencjalnie krytyczny",
                        1: "potencjalnie średni",
                        0: "potencjalnie niski"
                    }.get(incident_priority, "potencjalnie średni")
                
                # Calculate combined overall confidence
                animal_conf = animal_fields_with_confidence['overall_confidence']
                priority_conf = priority_prediction.get('confidence', 0.0)
                
                # If animal fields are very confident (>0.90), don't let priority drag it down too much
                if animal_conf >= 0.90:
                    combined_confidence = animal_conf * 0.90 + priority_conf * 0.10
                else:
                    combined_confidence = animal_conf * 0.80 + priority_conf * 0.20
                
                # Auto-fill if confidence >= 75% (realistic for real calls), but never if < 50%
                should_auto_fill = combined_confidence >= 0.75 and combined_confidence >= 0.50
                
                response_data['analysis'] = {
                    'keywords': keywords,
                    'highlighted_text': highlighted,
                    'priority_suggestion': priority_suggestion,
                    'entities': entities
                }
                
                # NOWE: Dodaj pola zwierzęce z confidence
                response_data['animal_fields'] = {
                    'species': animal_fields_with_confidence['fields']['species']['value'],
                    'species_label': animal_extractor.get_species_label(animal_fields_with_confidence['fields']['species']['value']),
                    'species_confidence': animal_fields_with_confidence['fields']['species']['confidence'],
                    'location': animal_fields_with_confidence['fields']['location']['value'],
                    'location_confidence': animal_fields_with_confidence['fields']['location']['confidence'],
                    'incident_types': animal_fields_with_confidence['fields']['incident_types']['value'],
                    'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields_with_confidence['fields']['incident_types']['value']],
                    'incident_types_confidence': animal_fields_with_confidence['fields']['incident_types']['confidence'],
                    'description': animal_fields_with_confidence['fields']['description']['value'],
                    'description_confidence': animal_fields_with_confidence['fields']['description']['confidence'],
                    'caller_name': animal_fields_with_confidence['fields']['caller_name']['value'],
                    'caller_name_confidence': animal_fields_with_confidence['fields']['caller_name']['confidence'],
                    'caller_phone': animal_fields_with_confidence['fields']['caller_phone']['value'],
                    'caller_phone_confidence': animal_fields_with_confidence['fields']['caller_phone']['confidence'],
                    'animal_count': animal_fields_with_confidence['fields']['animal_count']['value'],
                    'animal_count_confidence': animal_fields_with_confidence['fields']['animal_count']['confidence']
                }
                
                response_data['priority_prediction'] = {
                    'prediction': priority_prediction.get('prediction'),
                    'priority': priority_prediction.get('priority'),
                    'confidence': priority_prediction.get('confidence'),
                    'all_probabilities': priority_prediction.get('all_probabilities')
                }
                
                response_data['overall_confidence'] = combined_confidence
                response_data['should_auto_fill'] = should_auto_fill
            
            return jsonify(response_data), 200
            
        finally:
            # Usuń plik tymczasowy
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Błąd transkrypcji: {str(e)}'
        }), 500


@stt_bp.route('/analyze-full', methods=['POST'])
def analyze_full():
    """
    Pełna analiza audio: transkrypcja + priorytet ML + duplikaty
    
    Form data:
        audio: plik audio
        language: język (domyślnie 'pl')
        check_duplicates: czy sprawdzać duplikaty (domyślnie true)
    """
    try:
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'error': 'Brak pliku audio'
            }), 400
        
        file = request.files['audio']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'error': 'Nieprawidłowy plik audio'
            }), 400
        
        language = request.form.get('language', 'pl')
        check_duplicates = request.form.get('check_duplicates', 'true').lower() == 'true'
        
        # Zapisz tymczasowo
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # 1. Transkrypcja
            stt = get_stt_service()
            transcription_result = stt.transcribe_file(tmp_path, language=language)
            text = transcription_result['text']
            
            # 2. Analiza słów kluczowych
            keyword_extractor = KeywordExtractor()
            keywords = keyword_extractor.extract_keywords(text)
            highlighted = keyword_extractor.highlight_keywords(text)
            keyword_priority = keyword_extractor.suggest_priority(text)
            entities = keyword_extractor.extract_entities(text)
            
            # 2b. NOWE: Analiza pól zwierzęcych
            animal_extractor = AnimalFieldExtractor()
            animal_fields = animal_extractor.extract_all_fields(text)
            
            # 3. Priorytet ML (z modelu)
            from app.routes.model_routes import PRIORITY_MAPPING
            import joblib
            
            model_path = os.path.join(
                os.path.dirname(__file__), '..', 'utils', 'model', 'model_priorytet.pkl'
            )
            vectorizer_path = os.path.join(
                os.path.dirname(__file__), '..', 'utils', 'model', 'vectorizer.pkl'
            )
            
            ml_priority = None
            ml_priority_text = None
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                model = joblib.load(model_path)
                vectorizer = joblib.load(vectorizer_path)
                vec = vectorizer.transform([text])
                ml_priority = int(model.predict(vec)[0])
                ml_priority_text = PRIORITY_MAPPING.get(ml_priority, "nieznany")
            
            # 4. Sprawdź duplikaty (jeśli w bazie są zgłoszenia)
            duplicates = []
            if check_duplicates:
                # Tutaj możesz stworzyć tymczasowy obiekt Issue i sprawdzić
                # Na razie zwracamy pustą listę
                pass
            
            # Sugerowany formularz - ZAKTUALIZOWANY dla zwierząt
            suggested_form = {
                'species': animal_fields['species'],  # OBOWIĄZKOWE
                'species_label': animal_extractor.get_species_label(animal_fields['species']),
                'location': animal_fields['location'],
                'description': animal_fields['description'],
                'incident_types': animal_fields['incident_types'],
                'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields['incident_types']],
                'animal_count': animal_fields.get('animal_count', 1),
                'priority': ml_priority_text or keyword_priority['priority'],
                'full_transcription': text
            }
            
            return jsonify({
                'status': 'success',
                'transcription': {
                    'text': text,
                    'language': transcription_result['language'],
                    'segments': transcription_result['segments']
                },
                'keyword_analysis': {
                    'keywords': keywords,
                    'highlighted_text': highlighted,
                    'priority_suggestion': keyword_priority,
                    'entities': entities
                },
                'animal_fields': {
                    'species': animal_fields['species'],
                    'species_label': animal_extractor.get_species_label(animal_fields['species']),
                    'location': animal_fields['location'],
                    'incident_types': animal_fields['incident_types'],
                    'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields['incident_types']],
                    'description': animal_fields['description'],
                    'animal_count': animal_fields.get('animal_count', 1)
                },
                'ml_analysis': {
                    'priority': ml_priority,
                    'priority_text': ml_priority_text
                } if ml_priority is not None else None,
                'duplicates': duplicates,
                'suggested_form': suggested_form
            }), 200
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Błąd analizy: {str(e)}'
        }), 500


@stt_bp.route('/text-analyze', methods=['POST'])
def analyze_text():
    """
    Analizuje tekst (bez audio) - dla przypadków gdy masz już transkrypcję
    
    Body:
        text: tekst do analizy
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Brak pola "text"'
            }), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify({
                'status': 'error',
                'error': 'Tekst nie może być pusty'
            }), 400
        
        # Analiza słów kluczowych
        keyword_extractor = KeywordExtractor()
        keywords = keyword_extractor.extract_keywords(text)
        highlighted = keyword_extractor.highlight_keywords(text)
        priority_suggestion = keyword_extractor.suggest_priority(text)
        entities = keyword_extractor.extract_entities(text)
        
        # NOWE: Analiza pól zwierzęcych
        animal_extractor = AnimalFieldExtractor()
        animal_fields = animal_extractor.extract_all_fields(text)
        
        return jsonify({
            'status': 'success',
            'analysis': {
                'keywords': keywords,
                'highlighted_text': highlighted,
                'priority_suggestion': priority_suggestion,
                'entities': entities
            },
            'animal_fields': {
                'species': animal_fields['species'],
                'species_label': animal_extractor.get_species_label(animal_fields['species']),
                'location': animal_fields['location'],
                'incident_types': animal_fields['incident_types'],
                'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields['incident_types']],
                'description': animal_fields['description'],
                'animal_count': animal_fields.get('animal_count', 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Błąd analizy: {str(e)}'
        }), 500
