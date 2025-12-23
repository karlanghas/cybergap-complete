"""
Servicio de Detección de Divergencias
Core del negocio - Detecta contradicciones en respuestas
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
import statistics

from ..models import (
    QuestionAssignment, Response, Question, User, Area, 
    DivergenceAlert, AlertSeverity, QuestionnaireAssignment
)


class DivergenceService:
    """Servicio para detectar y analizar divergencias en respuestas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_divergences(self, questionnaire_id: int) -> List[DivergenceAlert]:
        """
        Calcular divergencias para un cuestionario
        
        Detecta cuando la misma pregunta asignada a múltiples usuarios
        tiene respuestas diferentes.
        
        Returns:
            Lista de alertas de divergencia creadas
        """
        # Obtener todas las preguntas del cuestionario que fueron asignadas a múltiples usuarios
        questions_with_multiple_assignments = self._get_questions_with_multiple_responses(questionnaire_id)
        
        alerts = []
        
        for question_id, responses_data in questions_with_multiple_assignments.items():
            if len(responses_data) < 2:
                continue
            
            # Analizar divergencia
            divergence_info = self._analyze_divergence(responses_data)
            
            if divergence_info["has_divergence"]:
                # Verificar si ya existe una alerta para esta pregunta
                existing_alert = self.db.query(DivergenceAlert).filter(
                    DivergenceAlert.questionnaire_id == questionnaire_id,
                    DivergenceAlert.question_id == question_id,
                    DivergenceAlert.is_resolved == False
                ).first()
                
                if existing_alert:
                    # Actualizar alerta existente
                    existing_alert.responses_data = divergence_info["responses"]
                    existing_alert.variance = divergence_info["variance"]
                    existing_alert.severity = divergence_info["severity"]
                    alerts.append(existing_alert)
                else:
                    # Crear nueva alerta
                    alert = DivergenceAlert(
                        questionnaire_id=questionnaire_id,
                        question_id=question_id,
                        severity=divergence_info["severity"],
                        responses_data=divergence_info["responses"],
                        variance=divergence_info["variance"]
                    )
                    self.db.add(alert)
                    alerts.append(alert)
        
        self.db.commit()
        return alerts
    
    def _get_questions_with_multiple_responses(self, questionnaire_id: int) -> Dict[int, List[Dict]]:
        """
        Obtener preguntas con múltiples respuestas
        
        Returns:
            Dict con question_id como key y lista de respuestas como value
        """
        # Query para obtener respuestas agrupadas por pregunta
        results = self.db.query(
            QuestionAssignment.question_id,
            User.id.label("user_id"),
            User.full_name.label("user_name"),
            Area.name.label("area_name"),
            Response.answer,
            Response.score,
            Question.question_type,
            Question.options
        ).join(
            Response, QuestionAssignment.id == Response.assignment_id
        ).join(
            User, QuestionAssignment.user_id == User.id
        ).join(
            Area, User.area_id == Area.id
        ).join(
            Question, QuestionAssignment.question_id == Question.id
        ).filter(
            QuestionAssignment.questionnaire_id == questionnaire_id
        ).all()
        
        # Agrupar por pregunta
        grouped = defaultdict(list)
        question_types = {}
        question_options = {}
        
        for row in results:
            grouped[row.question_id].append({
                "user_id": row.user_id,
                "user_name": row.user_name,
                "area_name": row.area_name,
                "answer": row.answer,
                "score": row.score
            })
            question_types[row.question_id] = row.question_type
            question_options[row.question_id] = row.options
        
        # Filtrar solo preguntas con múltiples respuestas
        return {
            qid: {
                "responses": responses,
                "question_type": question_types[qid],
                "options": question_options[qid]
            }
            for qid, responses in grouped.items()
            if len(responses) > 1
        }
    
    def _analyze_divergence(self, data: Dict) -> Dict[str, Any]:
        """
        Analizar si hay divergencia en las respuestas
        
        Returns:
            Dict con información de divergencia
        """
        responses = data["responses"]
        question_type = data["question_type"]
        options = data.get("options", [])
        
        # Extraer solo las respuestas
        answers = [r["answer"] for r in responses]
        scores = [r["score"] for r in responses if r["score"] is not None]
        
        has_divergence = False
        variance = None
        severity = AlertSeverity.LOW
        
        if question_type in ["single_choice", "yes_no"]:
            # Para opciones únicas, verificar si todas son iguales
            unique_answers = set(str(a) for a in answers)
            has_divergence = len(unique_answers) > 1
            
            if has_divergence:
                # Calcular severidad basada en diferencia de scores
                if scores and len(scores) > 1:
                    variance = statistics.variance(scores) if len(scores) > 1 else 0
                    score_range = max(scores) - min(scores)
                    
                    if score_range > 75:
                        severity = AlertSeverity.CRITICAL
                    elif score_range > 50:
                        severity = AlertSeverity.HIGH
                    elif score_range > 25:
                        severity = AlertSeverity.MEDIUM
                    else:
                        severity = AlertSeverity.LOW
        
        elif question_type == "multiple_choice":
            # Para múltiple, calcular overlap
            answer_sets = [set(a) if isinstance(a, list) else {a} for a in answers]
            
            # Calcular índice de Jaccard promedio
            similarities = []
            for i in range(len(answer_sets)):
                for j in range(i + 1, len(answer_sets)):
                    intersection = len(answer_sets[i] & answer_sets[j])
                    union = len(answer_sets[i] | answer_sets[j])
                    if union > 0:
                        similarities.append(intersection / union)
            
            if similarities:
                avg_similarity = sum(similarities) / len(similarities)
                has_divergence = avg_similarity < 0.8  # 80% de similitud
                variance = 1 - avg_similarity
                
                if avg_similarity < 0.3:
                    severity = AlertSeverity.CRITICAL
                elif avg_similarity < 0.5:
                    severity = AlertSeverity.HIGH
                elif avg_similarity < 0.7:
                    severity = AlertSeverity.MEDIUM
        
        elif question_type == "scale":
            # Para escalas, calcular varianza
            numeric_answers = [float(a) for a in answers if a is not None]
            if len(numeric_answers) > 1:
                variance = statistics.variance(numeric_answers)
                std_dev = statistics.stdev(numeric_answers)
                mean = statistics.mean(numeric_answers)
                
                # Coeficiente de variación
                cv = (std_dev / mean * 100) if mean > 0 else 0
                
                has_divergence = cv > 20  # >20% de variación
                
                if cv > 50:
                    severity = AlertSeverity.CRITICAL
                elif cv > 40:
                    severity = AlertSeverity.HIGH
                elif cv > 30:
                    severity = AlertSeverity.MEDIUM
        
        elif question_type == "text":
            # Para texto, siempre marcar si hay diferencias significativas
            # (simplificado - en producción usar NLP)
            unique_answers = set(str(a).lower().strip() for a in answers)
            has_divergence = len(unique_answers) > 1
            severity = AlertSeverity.LOW  # Texto siempre LOW, requiere revisión manual
        
        return {
            "has_divergence": has_divergence,
            "variance": variance,
            "severity": severity,
            "responses": responses
        }
    
    def get_divergence_summary(self, questionnaire_id: int) -> Dict[str, Any]:
        """Obtener resumen de divergencias"""
        alerts = self.db.query(DivergenceAlert).filter(
            DivergenceAlert.questionnaire_id == questionnaire_id
        ).all()
        
        return {
            "total_alerts": len(alerts),
            "unresolved": sum(1 for a in alerts if not a.is_resolved),
            "by_severity": {
                "critical": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
                "high": sum(1 for a in alerts if a.severity == AlertSeverity.HIGH),
                "medium": sum(1 for a in alerts if a.severity == AlertSeverity.MEDIUM),
                "low": sum(1 for a in alerts if a.severity == AlertSeverity.LOW)
            }
        }
    
    def resolve_alert(self, alert_id: int, admin_id: int, notes: str) -> Optional[DivergenceAlert]:
        """Marcar alerta como resuelta"""
        from datetime import datetime
        
        alert = self.db.query(DivergenceAlert).filter(
            DivergenceAlert.id == alert_id
        ).first()
        
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = admin_id
            alert.resolution_notes = notes
            self.db.commit()
        
        return alert
