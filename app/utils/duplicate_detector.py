"""Duplicate issue detection using cosine similarity"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from flask import current_app
import numpy as np


class DuplicateDetector:
    """Detects potential duplicate issues based on description similarity"""
    
    def __init__(self, similarity_threshold=0.32):
        """
        Args:
            similarity_threshold: próg podobieństwa (0-1), powyżej którego uznajemy za duplikat
            Default: 0.32 (32%) - adjusted for Polish text with TF-IDF
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1000,
            stop_words=None  # Możesz dodać polskie stop words
        )

    @staticmethod
    def _build_issue_text(issue):
        """Build a comparable text representation from Issue fields that exist in the model."""
        parts = [
            issue.event_type or '',
            issue.species or '',
            issue.incident_address or '',
            issue.description or '',
            ' '.join(issue.options) if issue.options else '',
            'pilne' if issue.urgency else ''
        ]
        return ' '.join(part for part in parts if part).strip()
    
    def find_duplicates(self, issue, days_back=7):
        """
        Znajduje potencjalne duplikaty dla danego zgłoszenia
        
        Args:
            issue: obiekt Issue do sprawdzenia
            days_back: ile dni wstecz sprawdzać (domyślnie 7)
            
        Returns:
            lista słowników z potencjalnymi duplikatami i ich podobieństwem
        """
        from app.models.issue import Issue
        
        try:
            # Pobierz zgłoszenia z ostatnich N dni (wykluczając aktualne)
            date_threshold = datetime.utcnow() - timedelta(days=days_back)
            
            recent_issues = Issue.objects(
                created_at__gte=date_threshold,
                id__ne=issue.id  # Wyklucz aktualne zgłoszenie
            ).only(
                'id',
                'event_type',
                'species',
                'incident_address',
                'description',
                'options',
                'urgency',
                'status',
                'created_at'
            )
            
            if not recent_issues:
                return []
            
            # Przygotuj teksty do porównania
            current_text = self._build_issue_text(issue)
            other_texts = [self._build_issue_text(i) for i in recent_issues]
            
            # Jeśli jest tylko jedno zgłoszenie do porównania
            if len(other_texts) == 0:
                return []
            
            # Dodaj aktualny tekst na początku
            all_texts = [current_text] + other_texts
            
            # Wektoryzacja
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Oblicz podobieństwo cosinusowe między aktualnym a pozostałymi
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            
            # Znajdź duplikaty powyżej progu
            duplicates = []
            for idx, similarity in enumerate(similarities):
                if similarity >= self.similarity_threshold:
                    similar_issue = recent_issues[idx]
                    duplicates.append({
                        'id': str(similar_issue.id),
                        'event_type': similar_issue.event_type,
                        'species': similar_issue.species,
                        'incident_address': similar_issue.incident_address,
                        'description': (similar_issue.description or '')[:200],  # Pierwsze 200 znaków
                        'status': similar_issue.status,
                        'urgency': bool(similar_issue.urgency),
                        'created_at': similar_issue.created_at.isoformat(),
                        'similarity': float(similarity),
                        'similarity_percent': float(similarity * 100)
                    })
            
            # Sortuj według podobieństwa (malejąco)
            duplicates.sort(key=lambda x: x['similarity'], reverse=True)
            
            current_app.logger.info(
                f"Znaleziono {len(duplicates)} potencjalnych duplikatów "
                f"dla zgłoszenia {issue.id}"
            )
            
            return duplicates
            
        except Exception as e:
            current_app.logger.error(f"Błąd podczas szukania duplikatów: {str(e)}")
            raise
    
    def get_similarity_score(self, text1, text2):
        """
        Oblicz podobieństwo między dwoma tekstami
        
        Args:
            text1: pierwszy tekst
            text2: drugi tekst
            
        Returns:
            float: podobieństwo (0-1)
        """
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            current_app.logger.error(f"Błąd obliczania podobieństwa: {str(e)}")
            return 0.0