"""Model prediction routes"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import joblib
import os

model_bp = Blueprint('model', __name__)

PRIORITY_MAPPING = {
    2: "potencjalnie krytyczny",
    1: "potencjalnie średni",
    0: "potencjalnie niski"
}


@model_bp.route('/predict', methods=['POST'])
def get_prediction():
    """Przewiduje priorytet zgłoszenia na podstawie opisu"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Brak wymaganego pola "text" w żądaniu',
                'status': 'error'
            }), 400
        
        text = data['text']
        
        if not text or not text.strip():
            return jsonify({
                'error': 'Pole "text" nie może być puste',
                'status': 'error'
            }), 400
        
        model_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'model', 'model_priorytet.pkl')
        vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'model', 'vectorizer.pkl')
        
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        
        vec = vectorizer.transform([text])
        prediction = int(model.predict(vec)[0])
        
        priority_text = PRIORITY_MAPPING.get(prediction, "nieznany")
        
        return jsonify({
            'prediction': prediction,
            'priority': priority_text,
            'text': text,
            'status': 'success'
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({
            'error': 'Model lub vectorizer nie został znaleziony. Upewnij się, że pliki model_priorytet.pkl i vectorizer.pkl istnieją.',
            'status': 'error'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Błąd podczas przewidywania: {str(e)}',
            'status': 'error'
        }), 500