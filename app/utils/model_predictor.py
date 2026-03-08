"""ML Model prediction utilities"""
import joblib
import os


# Cache for loaded models
_model_cache = {}


def get_model_and_vectorizer():
    """Load and cache the priority prediction model and vectorizer"""
    if 'model' not in _model_cache:
        model_path = os.path.join(
            os.path.dirname(__file__), 
            'model', 
            'model_priorytet.pkl'
        )
        vectorizer_path = os.path.join(
            os.path.dirname(__file__), 
            'model', 
            'vectorizer.pkl'
        )
        
        _model_cache['model'] = joblib.load(model_path)
        _model_cache['vectorizer'] = joblib.load(vectorizer_path)
    
    return _model_cache['model'], _model_cache['vectorizer']


def predict_priority_with_confidence(text):
    """
    Predict priority with confidence scores
    
    Args:
        text: Input text to predict priority for
        
    Returns:
        dict: {
            'prediction': int (0-2),
            'priority': str,
            'confidence': float (0.0-1.0),
            'all_probabilities': dict
        }
    """
    PRIORITY_MAPPING = {
        2: "potencjalnie krytyczny",
        1: "potencjalnie średni",
        0: "potencjalnie niski"
    }
    
    try:
        model, vectorizer = get_model_and_vectorizer()
        
        # Vectorize and predict
        vec = vectorizer.transform([text])
        prediction = int(model.predict(vec)[0])
        probabilities = model.predict_proba(vec)[0]
        
        # Get confidence for the predicted class
        confidence = float(probabilities[prediction])
        
        # Get all class probabilities
        all_probabilities = {
            'critical': float(probabilities[2]),
            'medium': float(probabilities[1]),
            'low': float(probabilities[0])
        }
        
        priority_text = PRIORITY_MAPPING.get(prediction, "nieznany")
        
        return {
            'prediction': prediction,
            'priority': priority_text,
            'confidence': confidence,
            'all_probabilities': all_probabilities
        }
        
    except FileNotFoundError:
        return {
            'prediction': 1,  # Default to medium
            'priority': "potencjalnie średni",
            'confidence': 0.0,
            'all_probabilities': {
                'critical': 0.0,
                'medium': 0.0,
                'low': 0.0
            },
            'error': 'Model not found'
        }
    except Exception as e:
        return {
            'prediction': 1,
            'priority': "potencjalnie średni",
            'confidence': 0.0,
            'all_probabilities': {
                'critical': 0.0,
                'medium': 0.0,
                'low': 0.0
            },
            'error': str(e)
        }
