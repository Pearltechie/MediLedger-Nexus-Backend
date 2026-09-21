"""
Federated Learning Engine for MediLedger Nexus
Privacy-preserving machine learning across healthcare institutions
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from mediledger_nexus.core.logging import get_logger
from mediledger_nexus.services.groq_ai import GroqAIService

logger = get_logger(__name__)


class ModelWeights:
    """Container for model weights and metadata"""
    
    def __init__(self, weights: Dict[str, np.ndarray], metadata: Dict[str, Any]):
        self.weights = weights
        self.metadata = metadata
        self.timestamp = datetime.utcnow()
        self.participant_id = metadata.get("participant_id")
        self.round_number = metadata.get("round_number", 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "weights": {k: v.tolist() for k, v in self.weights.items()},
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "participant_id": self.participant_id,
            "round_number": self.round_number
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelWeights":
        """Create from dictionary"""
        weights = {k: np.array(v) for k, v in data["weights"].items()}
        return cls(weights, data["metadata"])


class FederatedLearningRound:
    """Represents a federated learning round"""
    
    def __init__(self, round_id: str, study_type: str, min_participants: int = 3):
        self.round_id = round_id
        self.study_type = study_type
        self.min_participants = min_participants
        self.participants: List[str] = []
        self.model_updates: List[ModelWeights] = []
        self.global_model: Optional[ModelWeights] = None
        self.status = "waiting"  # waiting, training, aggregating, completed
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
    
    def add_participant(self, participant_id: str) -> bool:
        """Add participant to the round"""
        if participant_id not in self.participants:
            self.participants.append(participant_id)
            logger.info(f"Participant {participant_id} joined round {self.round_id}")
            return True
        return False
    
    def can_start(self) -> bool:
        """Check if round can start training"""
        return len(self.participants) >= self.min_participants
    
    def add_model_update(self, model_weights: ModelWeights) -> bool:
        """Add model update from participant"""
        if model_weights.participant_id in self.participants:
            self.model_updates.append(model_weights)
            logger.info(f"Received model update from {model_weights.participant_id}")
            return True
        return False
    
    def is_complete(self) -> bool:
        """Check if all participants have submitted updates"""
        return len(self.model_updates) >= len(self.participants)


class FederatedLearningEngine:
    """Federated Learning Engine for privacy-preserving ML"""
    
    def __init__(self):
        self.active_rounds: Dict[str, FederatedLearningRound] = {}
        self.completed_rounds: Dict[str, FederatedLearningRound] = {}
        self.groq_service = GroqAIService()
        self.supported_models = {
            "logistic_regression": LogisticRegression,
            "random_forest": RandomForestClassifier
        }
    
    async def create_learning_round(
        self,
        study_type: str,
        min_participants: int = 3,
        model_type: str = "logistic_regression"
    ) -> str:
        """Create a new federated learning round"""
        try:
            round_id = str(uuid4())
            learning_round = FederatedLearningRound(
                round_id=round_id,
                study_type=study_type,
                min_participants=min_participants
            )
            
            self.active_rounds[round_id] = learning_round
            
            logger.info(f"Created federated learning round: {round_id} for {study_type}")
            return round_id
        
        except Exception as e:
            logger.error(f"Error creating learning round: {e}")
            raise
    
    async def join_round(self, round_id: str, participant_id: str) -> bool:
        """Join a federated learning round"""
        try:
            if round_id not in self.active_rounds:
                logger.warning(f"Round {round_id} not found")
                return False
            
            learning_round = self.active_rounds[round_id]
            success = learning_round.add_participant(participant_id)
            
            # Start training if minimum participants reached
            if learning_round.can_start() and learning_round.status == "waiting":
                learning_round.status = "training"
                logger.info(f"Round {round_id} started training with {len(learning_round.participants)} participants")
            
            return success
        
        except Exception as e:
            logger.error(f"Error joining round {round_id}: {e}")
            return False
    
    async def submit_model_update(
        self,
        round_id: str,
        participant_id: str,
        local_model: BaseEstimator,
        training_metadata: Dict[str, Any]
    ) -> bool:
        """Submit local model update to federated learning round"""
        try:
            if round_id not in self.active_rounds:
                logger.warning(f"Round {round_id} not found")
                return False
            
            learning_round = self.active_rounds[round_id]
            
            # Extract model weights (simplified for demo)
            model_weights = self._extract_model_weights(local_model, participant_id, training_metadata)
            
            success = learning_round.add_model_update(model_weights)
            
            # Check if round is complete and aggregate
            if learning_round.is_complete():
                await self._aggregate_models(round_id)
            
            return success
        
        except Exception as e:
            logger.error(f"Error submitting model update for round {round_id}: {e}")
            return False
    
    async def _aggregate_models(self, round_id: str) -> None:
        """Aggregate model updates using federated averaging"""
        try:
            learning_round = self.active_rounds[round_id]
            learning_round.status = "aggregating"
            
            logger.info(f"Aggregating models for round {round_id}")
            
            # Federated averaging
            aggregated_weights = self._federated_average(learning_round.model_updates)
            
            # Create global model
            global_metadata = {
                "round_id": round_id,
                "participants": len(learning_round.participants),
                "aggregation_method": "federated_average",
                "study_type": learning_round.study_type
            }
            
            learning_round.global_model = ModelWeights(aggregated_weights, global_metadata)
            learning_round.status = "completed"
            learning_round.completed_at = datetime.utcnow()
            
            # Move to completed rounds
            self.completed_rounds[round_id] = learning_round
            del self.active_rounds[round_id]
            
            # Generate insights using Groq AI
            await self._generate_learning_insights(learning_round)
            
            logger.info(f"Completed federated learning round: {round_id}")
        
        except Exception as e:
            logger.error(f"Error aggregating models for round {round_id}: {e}")
    
    def _extract_model_weights(
        self,
        model: BaseEstimator,
        participant_id: str,
        metadata: Dict[str, Any]
    ) -> ModelWeights:
        """Extract weights from trained model"""
        try:
            weights = {}
            
            # Extract weights based on model type
            if hasattr(model, 'coef_'):
                weights['coefficients'] = model.coef_
            if hasattr(model, 'intercept_'):
                weights['intercept'] = model.intercept_
            if hasattr(model, 'feature_importances_'):
                weights['feature_importances'] = model.feature_importances_
            
            # Add participant metadata
            metadata.update({
                "participant_id": participant_id,
                "model_type": type(model).__name__,
                "n_features": getattr(model, 'n_features_in_', 0)
            })
            
            return ModelWeights(weights, metadata)
        
        except Exception as e:
            logger.error(f"Error extracting model weights: {e}")
            # Return empty weights as fallback
            return ModelWeights({}, {"participant_id": participant_id, "error": str(e)})
    
    def _federated_average(self, model_updates: List[ModelWeights]) -> Dict[str, np.ndarray]:
        """Perform federated averaging of model weights"""
        try:
            if not model_updates:
                return {}
            
            # Get all weight keys
            all_keys = set()
            for update in model_updates:
                all_keys.update(update.weights.keys())
            
            # Average weights for each key
            averaged_weights = {}
            for key in all_keys:
                weights_for_key = []
                for update in model_updates:
                    if key in update.weights:
                        weights_for_key.append(update.weights[key])
                
                if weights_for_key:
                    # Simple average (could be weighted by data size)
                    averaged_weights[key] = np.mean(weights_for_key, axis=0)
            
            logger.info(f"Averaged weights from {len(model_updates)} participants")
            return averaged_weights
        
        except Exception as e:
            logger.error(f"Error in federated averaging: {e}")
            return {}
    
    async def _generate_learning_insights(self, learning_round: FederatedLearningRound) -> None:
        """Generate insights from federated learning results using Groq AI"""
        try:
            if not learning_round.global_model:
                return
            
            # Prepare data for Groq analysis
            round_summary = {
                "study_type": learning_round.study_type,
                "participants": len(learning_round.participants),
                "model_updates": len(learning_round.model_updates),
                "global_model_weights": {
                    k: v.tolist() if isinstance(v, np.ndarray) else v
                    for k, v in learning_round.global_model.weights.items()
                }
            }
            
            # Get insights from Groq AI
            insights = await self.groq_service.federated_learning_insights([round_summary])
            
            # Store insights in global model metadata
            learning_round.global_model.metadata["ai_insights"] = insights
            
            logger.info(f"Generated AI insights for round {learning_round.round_id}")
        
        except Exception as e:
            logger.error(f"Error generating learning insights: {e}")
    
    async def get_round_status(self, round_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a federated learning round"""
        try:
            # Check active rounds
            if round_id in self.active_rounds:
                learning_round = self.active_rounds[round_id]
            elif round_id in self.completed_rounds:
                learning_round = self.completed_rounds[round_id]
            else:
                return None
            
            return {
                "round_id": round_id,
                "study_type": learning_round.study_type,
                "status": learning_round.status,
                "participants": len(learning_round.participants),
                "model_updates": len(learning_round.model_updates),
                "created_at": learning_round.created_at.isoformat(),
                "completed_at": learning_round.completed_at.isoformat() if learning_round.completed_at else None,
                "has_global_model": learning_round.global_model is not None
            }
        
        except Exception as e:
            logger.error(f"Error getting round status: {e}")
            return None
    
    async def get_available_rounds(self) -> List[Dict[str, Any]]:
        """Get list of available federated learning rounds"""
        try:
            available_rounds = []
            
            for round_id, learning_round in self.active_rounds.items():
                if learning_round.status == "waiting":
                    available_rounds.append({
                        "round_id": round_id,
                        "study_type": learning_round.study_type,
                        "current_participants": len(learning_round.participants),
                        "min_participants": learning_round.min_participants,
                        "can_join": True,
                        "created_at": learning_round.created_at.isoformat()
                    })
            
            return available_rounds
        
        except Exception as e:
            logger.error(f"Error getting available rounds: {e}")
            return []
    
    async def get_global_model(self, round_id: str) -> Optional[ModelWeights]:
        """Get global model from completed round"""
        try:
            if round_id in self.completed_rounds:
                return self.completed_rounds[round_id].global_model
            return None
        
        except Exception as e:
            logger.error(f"Error getting global model: {e}")
            return None
