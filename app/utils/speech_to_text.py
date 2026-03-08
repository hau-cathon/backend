"""Speech to Text using Whisper"""
import whisper
import numpy as np
import io
import tempfile
import os
from flask import current_app
from pydub import AudioSegment


class SpeechToText:
    """Handles speech to text conversion using Whisper"""
    
    def __init__(self, model_size='base'):
        """
        Initialize Whisper model
        
        Args:
            model_size: 'tiny', 'base', 'small', 'medium', 'large'
                       tiny/base - szybkie, mniej dokładne (dobre do demo)
                       small/medium - wolniejsze, bardziej dokładne
        """
        self.model_size = model_size
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load model"""
        try:
            current_app.logger.info(f"Ładowanie modelu Whisper ({self.model_size})...")
            self.model = whisper.load_model(self.model_size)
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
        try:
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                fp16=False  # CPU compatibility
            )
            
            return {
                'text': result['text'].strip(),
                'language': result['language'],
                'segments': [
                    {
                        'start': seg['start'],
                        'end': seg['end'],
                        'text': seg['text'].strip()
                    }
                    for seg in result['segments']
                ]
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
        try:
            # Konwertuj do wav jeśli potrzeba
            if format != 'wav':
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
        try:
            # Połącz fragmenty
            if format == 'wav':
                combined_audio = b''.join(audio_chunks)
            else:
                # Użyj pydub do połączenia
                segments = [AudioSegment.from_file(io.BytesIO(chunk), format=format) 
                           for chunk in audio_chunks]
                combined = sum(segments)
                
                wav_io = io.BytesIO()
                combined.export(wav_io, format='wav')
                combined_audio = wav_io.getvalue()
            
            return self.transcribe_audio_data(combined_audio, format='wav', language=language)
            
        except Exception as e:
            current_app.logger.error(f"Błąd transkrypcji fragmentów: {str(e)}")
            raise


# Singleton instance
_stt_instance = None

def get_stt_service(model_size='base'):
    """Get or create STT service instance"""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = SpeechToText(model_size=model_size)
    return _stt_instance
