"""WebSocket handler for audio streaming"""
from flask_socketio import SocketIO, emit
from flask import request
import io
from app.utils.speech_to_text import get_stt_service
from app.utils.keyword_extractor import KeywordExtractor
from app.utils.animal_field_extractor import AnimalFieldExtractor

socketio = SocketIO(cors_allowed_origins="*")

# Storage dla chunków audio per sesja
audio_buffers = {}


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


@socketio.on('connect')
def handle_connect():
    """Klient się połączył"""
    print(f'Client connected: {request.sid}')
    audio_buffers[request.sid] = []
    emit('connected', {'status': 'ready', 'session_id': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Klient się rozłączył"""
    print(f'Client disconnected: {request.sid}')
    if request.sid in audio_buffers:
        del audio_buffers[request.sid]


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """
    Odbiera chunk audio ze streamu
    
    data: {
        'audio': base64 lub bytes,
        'format': 'wav' / 'webm' / 'ogg',
        'final': boolean (czy to ostatni chunk)
    }
    """
    try:
        session_id = request.sid
        
        # Dekoduj audio jeśli base64
        if isinstance(data.get('audio'), str):
            import base64
            audio_data = base64.b64decode(data['audio'])
        else:
            audio_data = data.get('audio')
        
        # Dodaj do bufora
        if session_id not in audio_buffers:
            audio_buffers[session_id] = []
        
        audio_buffers[session_id].append(audio_data)
        
        # Jeśli to ostatni chunk, przetwórz całość
        if data.get('final', False):
            emit('processing', {'status': 'transcribing'})
            
            # Transkrybuj
            stt = get_stt_service()
            audio_format = data.get('format', 'wav')
            
            result = stt.transcribe_chunks(
                audio_buffers[session_id],
                format=audio_format,
                language='pl'
            )
            
            # Analizuj
            keyword_extractor = KeywordExtractor()
            keywords = keyword_extractor.extract_keywords(result['text'])
            highlighted = keyword_extractor.highlight_keywords(result['text'])
            priority = keyword_extractor.suggest_priority(result['text'])
            entities = keyword_extractor.extract_entities(result['text'])
            
            # NOWE: Analizuj pola zwierzęce z confidence
            animal_extractor = AnimalFieldExtractor()
            animal_fields_with_confidence = animal_extractor.extract_all_fields_with_confidence(result['text'])
            
            # Get ML priority prediction with confidence
            from app.utils.model_predictor import predict_priority_with_confidence
            priority_prediction = predict_priority_with_confidence(result['text'])
            
            # Calculate combined overall confidence
            # Weight: animal fields 80%, priority prediction 20%
            # Animal fields are more reliable than ML priority model
            animal_conf = animal_fields_with_confidence['overall_confidence']
            priority_conf = priority_prediction.get('confidence', 0.0)
            
            # If animal fields are very confident (>0.90), don't let priority drag it down too much
            if animal_conf >= 0.90:
                combined_confidence = animal_conf * 0.90 + priority_conf * 0.10
            else:
                combined_confidence = animal_conf * 0.80 + priority_conf * 0.20
            
            # Auto-fill only if confidence >= 85%, but never if < 50%
            should_auto_fill = combined_confidence >= 0.85 and combined_confidence >= 0.50
            
            # Wyślij wynik
            emit('transcription_complete', {
                'status': 'success',
                'transcription': result['text'],
                'segments': result['segments'],
                'analysis': {
                    'keywords': keywords,
                    'highlighted_text': highlighted,
                    'priority_suggestion': priority,
                    'entities': entities
                },
                'animal_fields': {
                    'species': animal_fields_with_confidence['fields']['species']['value'],
                    'species_label': animal_extractor.get_species_label(animal_fields_with_confidence['fields']['species']['value']),
                    'species_confidence': animal_fields_with_confidence['fields']['species']['confidence'],
                    'location': animal_fields_with_confidence['fields']['location']['value'],
                    'location_confidence': animal_fields_with_confidence['fields']['location']['confidence'],
                    'incident_types': animal_fields_with_confidence['fields']['incident_types']['value'],
                    'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields_with_confidence['fields']['incident_types']['value']],
                    'incident_types_confidence': animal_fields_with_confidence['fields']['incident_types']['confidence'],
                    'description': animal_fields_with_confidence['fields']['description']['value'],
                    'description_confidence': animal_fields_with_confidence['fields']['description']['confidence']
                },
                'priority_prediction': {
                    'prediction': priority_prediction.get('prediction'),
                    'priority': priority_prediction.get('priority'),
                    'confidence': priority_prediction.get('confidence'),
                    'all_probabilities': priority_prediction.get('all_probabilities')
                },
                'overall_confidence': combined_confidence,
                'should_auto_fill': should_auto_fill
            })
            
            # Wyczyść bufor
            audio_buffers[session_id] = []
        else:
            # Potwierdź odbiór chunka
            emit('chunk_received', {'chunk_number': len(audio_buffers[session_id])})
    
    except Exception as e:
        emit('error', {'error': str(e)})


@socketio.on('start_recording')
def handle_start_recording():
    """Rozpocznij nagrywanie"""
    session_id = request.sid
    audio_buffers[session_id] = []
    emit('recording_started', {'session_id': session_id})


@socketio.on('stop_recording')
def handle_stop_recording():
    """Zatrzymaj nagrywanie i przetwórz"""
    try:
        session_id = request.sid
        
        if session_id not in audio_buffers or not audio_buffers[session_id]:
            emit('error', {'error': 'Brak danych audio'})
            return
        
        emit('processing', {'status': 'transcribing'})
        
        # Transkrybuj
        stt = get_stt_service()
        result = stt.transcribe_chunks(audio_buffers[session_id], format='wav', language='pl')
        
        # Analizuj
        keyword_extractor = KeywordExtractor()
        keywords = keyword_extractor.extract_keywords(result['text'])
        highlighted = keyword_extractor.highlight_keywords(result['text'])
        priority = keyword_extractor.suggest_priority(result['text'])
        entities = keyword_extractor.extract_entities(result['text'])
        
        # NOWE: Analizuj pola zwierzęce z confidence
        animal_extractor = AnimalFieldExtractor()
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
        # Weight: animal fields 80%, priority prediction 20%
        # Animal fields are more reliable than ML priority model
        animal_conf = animal_fields_with_confidence['overall_confidence']
        priority_conf = priority_prediction.get('confidence', 0.0)
        
        # If animal fields are very confident (>0.90), don't let priority drag it down too much
        if animal_conf >= 0.90:
            combined_confidence = animal_conf * 0.90 + priority_conf * 0.10
        else:
            combined_confidence = animal_conf * 0.80 + priority_conf * 0.20
        
        # Auto-fill only if confidence >= 85%, but never if < 50%
        should_auto_fill = combined_confidence >= 0.85 and combined_confidence >= 0.50
        
        # Wyślij wynik
        emit('transcription_complete', {
            'status': 'success',
            'transcription': result['text'],
            'segments': result['segments'],
            'analysis': {
                'keywords': keywords,
                'highlighted_text': highlighted,
                'priority_suggestion': priority,
                'entities': entities
            },
            'animal_fields': {
                'species': animal_fields_with_confidence['fields']['species']['value'],
                'species_label': animal_extractor.get_species_label(animal_fields_with_confidence['fields']['species']['value']),
                'species_confidence': animal_fields_with_confidence['fields']['species']['confidence'],
                'location': animal_fields_with_confidence['fields']['location']['value'],
                'location_confidence': animal_fields_with_confidence['fields']['location']['confidence'],
                'incident_types': animal_fields_with_confidence['fields']['incident_types']['value'],
                'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields_with_confidence['fields']['incident_types']['value']],
                'incident_types_confidence': animal_fields_with_confidence['fields']['incident_types']['confidence'],
                'description': animal_fields_with_confidence['fields']['description']['value'],
                'description_confidence': animal_fields_with_confidence['fields']['description']['confidence']
            },
            'priority_prediction': {
                'prediction': priority_prediction.get('prediction'),
                'priority': priority_prediction.get('priority'),
                'confidence': priority_prediction.get('confidence'),
                'all_probabilities': priority_prediction.get('all_probabilities')
            },
            'overall_confidence': combined_confidence,
            'should_auto_fill': should_auto_fill
        })
        
        # Wyczyść bufor
        audio_buffers[session_id] = []
        
    except Exception as e:
        print(f"Error in stop_recording: {str(e)}")
        emit('error', {'error': str(e)})
