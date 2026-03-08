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
            
            # NOWE: Analizuj pola zwierzęce
            animal_extractor = AnimalFieldExtractor()
            animal_fields = animal_extractor.extract_all_fields(result['text'])
            
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
                    'species': animal_fields['species'],
                    'species_label': animal_extractor.get_species_label(animal_fields['species']),
                    'location': animal_fields['location'],
                    'incident_types': animal_fields['incident_types'],
                    'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields['incident_types']],
                    'description': animal_fields['description']
                }
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
        
        # NOWE: Analizuj pola zwierzęce
        animal_extractor = AnimalFieldExtractor()
        animal_fields = animal_extractor.extract_all_fields(result['text'])
        
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
                'species': animal_fields['species'],
                'species_label': animal_extractor.get_species_label(animal_fields['species']),
                'location': animal_fields['location'],
                'incident_types': animal_fields['incident_types'],
                'incident_types_labels': [animal_extractor.get_incident_type_label(t) for t in animal_fields['incident_types']],
                'description': animal_fields['description']
            }
        })
        
        # Wyczyść bufor
        audio_buffers[session_id] = []
        
    except Exception as e:
        emit('error', {'error': str(e)})
