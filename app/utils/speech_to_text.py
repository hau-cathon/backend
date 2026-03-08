"""Speech to Text using Whisper"""
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  faster-whisper not installed - using mock transcription")

import numpy as np
import io
import tempfile
import os
from flask import current_app
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class SpeechToText:
    """Handles speech to text conversion using Whisper"""
    
    def __init__(self, model_size='base'):
        """
        Initialize Whisper model
        
        Args:
            model_size: 'tiny', 'base', 'small', 'medium', 'large-v2'
                       tiny/base - szybkie, mniej dokładne (dobre do demo)
                       small/medium - wolniejsze, bardziej dokładne
        """
        self.model_size = model_size
        self.model = None
        if WHISPER_AVAILABLE:
            self._load_model()
        else:
            current_app.logger.warning("Whisper not available - using mock transcription")
    
    def _load_model(self):
        """Lazy load model"""
        try:
            current_app.logger.info(f"Ładowanie modelu Whisper ({self.model_size})...")
            # faster-whisper używa CPU lub CUDA, device="cpu" dla kompatybilności
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            current_app.logger.info("Model Whisper załadowany")
        except Exception as e:
            current_app.logger.error(f"Błąd ładowania modelu Whisper: {str(e)}")
            raise
    
    def transcribe_file(self, audio_file_path, language='pl'):
        """
        Transkrybuje plik audio
        
        Args:
            audio_file_path: ścieżka do pliku audio
            language: kod języka (pl, en, itp.)
            
        Returns:
            dict: {'text': transkrypcja, 'language': język, 'segments': segmenty}
        """
        if not WHISPER_AVAILABLE:
            # Mock transcription for testing without whisper
            return {
                'text': 'Pies potrącony przez samochód na ulicy Polnej 18 w Warszawie. Zwierzę leży przy krawężniku, jest przytomne ale nie może wstać. Właściciel nieznany.',
                'language': language,
                'segments': [
                    {'start': 0.0, 'end': 3.5, 'text': 'Pies potrącony przez samochód na ulicy Polnej 18 w Warszawie.'},
                    {'start': 3.5, 'end': 7.0, 'text': 'Zwierzę leży przy krawężniku, jest przytomne ale nie może wstać.'},
                    {'start': 7.0, 'end': 9.0, 'text': 'Właściciel nieznany.'}
                ]
            }
        
        try:
            # faster-whisper zwraca generator segmentów i info
            segments, info = self.model.transcribe(
                audio_file_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection - filtruj ciszę
                vad_parameters=dict(
                    min_silence_duration_ms=500  # Minimum 500ms ciszy aby uznać za pauzę
                )
            )
            
            # Konwertuj generator na listę i łącz tekst
            segments_list = []
            full_text = []
            
            for segment in segments:
                segments_list.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
                full_text.append(segment.text.strip())
            
            return {
                'text': ' '.join(full_text),
                'language': info.language,
                'segments': segments_list
            }
        except Exception as e:
            current_app.logger.error(f"Błąd transkrypcji: {str(e)}")
            raise
    
    def transcribe_audio_data(self, audio_data, format='wav', language='pl'):
        """
        Transkrybuje dane audio z pamięci (np. ze streamu WebSocket)
        
        Args:
            audio_data: bytes - dane audio
            format: format audio (wav, mp3, webm, ogg)
            language: kod języka
            
        Returns:
            dict: wynik transkrypcji
        """
        if not WHISPER_AVAILABLE:
            # Mock transcription
            return {
                'text': 'Pies potrącony przez samochód na ulicy Polnej 18 w Warszawie. Zwierzę leży przy krawężniku, jest przytomne ale nie może wstać. Właściciel nieznany.',
                'language': language,
                'segments': [
                    {'start': 0.0, 'end': 3.5, 'text': 'Pies potrącony przez samochód na ulicy Polnej 18 w Warszawie.'},
                    {'start': 3.5, 'end': 7.0, 'text': 'Zwierzę leży przy krawężniku, jest przytomne ale nie może wstać.'},
                    {'start': 7.0, 'end': 9.0, 'text': 'Właściciel nieznany.'}
                ]
            }
        
        try:
            # Konwertuj do wav jeśli potrzeba
            if format != 'wav' and PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
                audio = audio.set_channels(1).set_frame_rate(16000)
                
                # Zapisz tymczasowo jako wav
                wav_io = io.BytesIO()
                audio.export(wav_io, format='wav')
                audio_data = wav_io.getvalue()
            
            # Zapisz tymczasowo do pliku (Whisper wymaga pliku)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                result = self.transcribe_file(tmp_path, language=language)
                return result
            finally:
                # Usuń plik tymczasowy
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        except Exception as e:
            current_app.logger.error(f"Błąd transkrypcji danych audio: {str(e)}")
            raise
    
    def transcribe_chunks(self, audio_chunks, format='wav', language='pl'):
        """
        Transkrybuje wiele fragmentów audio (streaming)
        
        Args:
            audio_chunks: lista bytes - fragmenty audio
            format: format audio
            language: kod języka
            
        Returns:
            dict: połączona transkrypcja
        """
        if not WHISPER_AVAILABLE:
            # Mock transcription
            return {
                'text': 'Pies potrącony przez samochód na ulicy Polnej 18 w Warszawie. Zwierzę leży przy krawężniku, jest przytomne ale nie może wstać. Właściciel nieznany.',
                'language': language,
                'segments': [
                    {'start': 0.0, 'end': 3.5, 'text': 'Pies potrącony przez samochód na ulicy Polnej 18 w Warszawie.'},
                    {'start': 3.5, 'end': 7.0, 'text': 'Zwierzę leży przy krawężniku, jest przytomne ale nie może wstać.'},
                    {'start': 7.0, 'end': 9.0, 'text': 'Właściciel nieznany.'}
                ]
            }
        
        try:
            # For WebM/OGG streaming chunks, concatenate raw bytes first, then decode
            # Individual chunks don't have complete headers and can't be decoded separately
            if format in ['webm', 'ogg', 'opus']:
                # Combine all raw bytes
                combined_audio_bytes = b''.join(audio_chunks)
                
                if PYDUB_AVAILABLE:
                    # Decode the complete file
                    audio_segment = AudioSegment.from_file(io.BytesIO(combined_audio_bytes), format=format)
                    wav_io = io.BytesIO()
                    audio_segment.export(wav_io, format='wav')
                    combined_audio = wav_io.getvalue()
                else:
                    # Without pydub, pass the raw bytes and let transcribe_audio_data handle it
                    return self.transcribe_audio_data(combined_audio_bytes, format=format, language=language)
            elif format == 'wav':
                # WAV chunks can be concatenated directly
                combined_audio = b''.join(audio_chunks)
            elif PYDUB_AVAILABLE:
                # For other formats, try decoding each chunk (if they have complete headers)
                segments = [AudioSegment.from_file(io.BytesIO(chunk), format=format) 
                           for chunk in audio_chunks]
                combined = sum(segments)
                
                wav_io = io.BytesIO()
                combined.export(wav_io, format='wav')
                combined_audio = wav_io.getvalue()
            else:
                # Fallback: concatenate raw bytes
                combined_audio = b''.join(audio_chunks)
            
            return self.transcribe_audio_data(combined_audio, format='wav', language=language)
            
        except Exception as e:
            current_app.logger.error(f"Błąd transkrypcji fragmentów: {str(e)}")
            raise


# Singleton instance
_stt_instance = None

def get_stt_service(model_size='small'):
    """Get or create STT service instance (default: 'small' for better accuracy)"""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = SpeechToText(model_size=model_size)
    return _stt_instance
