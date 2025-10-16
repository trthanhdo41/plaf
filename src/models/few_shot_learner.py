"""
Few-Shot Learning for Student Risk Prediction

Quick adaptation to new courses/cohorts with limited examples.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtoNet:
    """
    Prototypical Networks for Few-Shot Learning.
    
    Learn class prototypes from support set and classify based on distance.
    """
    
    def __init__(self, n_way: int = 2, n_support: int = 5):
        """
        Initialize Prototypical Network.
        
        Args:
            n_way: Number of classes
            n_support: Number of support examples per class
        """
        self.n_way = n_way
        self.n_support = n_support
        self.prototypes = {}
    
    def compute_prototype(self, examples: np.ndarray) -> np.ndarray:
        """Compute prototype (mean) of examples."""
        return np.mean(examples, axis=0)
    
    def fit(self, X_support: np.ndarray, y_support: np.ndarray):
        """
        Learn prototypes from support set.
        
        Args:
            X_support: Support features
            y_support: Support labels
        """
        unique_classes = np.unique(y_support)
        
        for cls in unique_classes:
            class_examples = X_support[y_support == cls]
            self.prototypes[cls] = self.compute_prototype(class_examples)
        
        logger.info(f"Learned {len(self.prototypes)} prototypes")
    
    def euclidean_distance(self, x: np.ndarray, prototype: np.ndarray) -> float:
        """Calculate Euclidean distance."""
        return np.sqrt(np.sum((x - prototype) ** 2))
    
    def predict_proba(self, X_query: np.ndarray) -> np.ndarray:
        """
        Predict probabilities for query set.
        
        Args:
            X_query: Query features
            
        Returns:
            Probability matrix (n_samples, n_classes)
        """
        if not self.prototypes:
            raise ValueError("Model not fitted. Call fit() first.")
        
        n_samples = X_query.shape[0]
        n_classes = len(self.prototypes)
        probabilities = np.zeros((n_samples, n_classes))
        
        for i, x in enumerate(X_query):
            distances = {}
            for cls, prototype in self.prototypes.items():
                distances[cls] = self.euclidean_distance(x, prototype)
            
            # Convert distances to probabilities (softmax)
            dist_values = np.array(list(distances.values()))
            # Invert distances (closer = higher probability)
            scores = -dist_values
            exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
            probs = exp_scores / np.sum(exp_scores)
            
            for j, cls in enumerate(distances.keys()):
                probabilities[i, int(cls)] = probs[j]
        
        return probabilities
    
    def predict(self, X_query: np.ndarray) -> np.ndarray:
        """Predict classes for query set."""
        probabilities = self.predict_proba(X_query)
        return np.argmax(probabilities, axis=1)


class FewShotLearner:
    """
    Few-Shot Learning system for student risk prediction.
    
    Combines meta-learning with traditional ML for quick adaptation.
    """
    
    def __init__(self, base_model: str = 'rf'):
        """
        Initialize few-shot learner.
        
        Args:
            base_model: Base model type ('rf', 'lr', 'protonet')
        """
        self.base_model_type = base_model
        self.base_model = None
        self.meta_model = None
        self.is_fitted = False
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize base and meta models."""
        if self.base_model_type == 'rf':
            self.base_model = RandomForestClassifier(
                n_estimators=50,
                max_depth=5,
                random_state=42
            )
        elif self.base_model_type == 'lr':
            self.base_model = LogisticRegression(
                max_iter=500,
                random_state=42
            )
        elif self.base_model_type == 'protonet':
            self.base_model = ProtoNet(n_way=2, n_support=5)
        else:
            raise ValueError(f"Unknown model type: {self.base_model_type}")
        
        logger.info(f"Initialized {self.base_model_type} base model")
    
    def meta_train(
        self,
        X_meta: np.ndarray,
        y_meta: np.ndarray,
        n_episodes: int = 100,
        n_way: int = 2,
        n_support: int = 5,
        n_query: int = 15
    ):
        """
        Meta-training using episodic learning.
        
        Args:
            X_meta: Meta-training features
            y_meta: Meta-training labels
            n_episodes: Number of training episodes
            n_way: Number of classes per episode
            n_support: Number of support examples per class
            n_query: Number of query examples per class
        """
        logger.info(f"Starting meta-training with {n_episodes} episodes...")
        
        # Simple meta-training: train on full dataset
        # In practice, would do episodic sampling
        self.base_model.fit(X_meta, y_meta)
        self.is_fitted = True
        
        logger.info("Meta-training completed")
    
    def quick_adapt(
        self,
        X_support: np.ndarray,
        y_support: np.ndarray,
        adaptation_steps: int = 10
    ):
        """
        Quick adaptation to new task with few examples.
        
        Args:
            X_support: Support set features
            y_support: Support set labels
            adaptation_steps: Number of adaptation steps
        """
        if not self.is_fitted:
            logger.warning("Base model not meta-trained, training from scratch")
        
        # Fit on support set
        if self.base_model_type == 'protonet':
            self.base_model.fit(X_support, y_support)
        else:
            # For sklearn models, just retrain
            self.base_model.fit(X_support, y_support)
        
        logger.info(f"Adapted to new task with {len(X_support)} examples")
    
    def predict(self, X_query: np.ndarray) -> np.ndarray:
        """Predict classes for query set."""
        if self.base_model_type == 'protonet':
            return self.base_model.predict(X_query)
        else:
            return self.base_model.predict(X_query)
    
    def predict_proba(self, X_query: np.ndarray) -> np.ndarray:
        """Predict probabilities for query set."""
        if self.base_model_type == 'protonet':
            return self.base_model.predict_proba(X_query)
        else:
            return self.base_model.predict_proba(X_query)
    
    def evaluate_few_shot(
        self,
        X_support: np.ndarray,
        y_support: np.ndarray,
        X_query: np.ndarray,
        y_query: np.ndarray
    ) -> Dict:
        """
        Evaluate few-shot performance.
        
        Args:
            X_support: Support features
            y_support: Support labels
            X_query: Query features
            y_query: Query labels
            
        Returns:
            Dict with metrics
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        # Adapt to support set
        self.quick_adapt(X_support, y_support)
        
        # Predict on query set
        y_pred = self.predict(X_query)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_query, y_pred),
            'precision': precision_score(y_query, y_pred, zero_division=0),
            'recall': recall_score(y_query, y_pred, zero_division=0),
            'f1': f1_score(y_query, y_pred, zero_division=0),
            'n_support': len(X_support),
            'n_query': len(X_query)
        }
        
        return metrics


class FewShotEpisodeSampler:
    """Sample few-shot learning episodes from dataset."""
    
    def __init__(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_way: int = 2,
        n_support: int = 5,
        n_query: int = 15
    ):
        """
        Initialize episode sampler.
        
        Args:
            X: Full feature matrix
            y: Full labels
            n_way: Number of classes per episode
            n_support: Support examples per class
            n_query: Query examples per class
        """
        self.X = X
        self.y = y
        self.n_way = n_way
        self.n_support = n_support
        self.n_query = n_query
        
        # Group indices by class
        self.class_indices = {}
        for cls in np.unique(y):
            self.class_indices[cls] = np.where(y == cls)[0]
    
    def sample_episode(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Sample one episode.
        
        Returns:
            (X_support, y_support, X_query, y_query)
        """
        # Sample classes
        available_classes = list(self.class_indices.keys())
        sampled_classes = np.random.choice(
            available_classes,
            size=min(self.n_way, len(available_classes)),
            replace=False
        )
        
        X_support_list = []
        y_support_list = []
        X_query_list = []
        y_query_list = []
        
        for cls in sampled_classes:
            # Get indices for this class
            cls_indices = self.class_indices[cls]
            
            # Sample support + query examples
            n_total = min(self.n_support + self.n_query, len(cls_indices))
            sampled_indices = np.random.choice(
                cls_indices,
                size=n_total,
                replace=False
            )
            
            # Split into support and query
            support_indices = sampled_indices[:self.n_support]
            query_indices = sampled_indices[self.n_support:n_total]
            
            X_support_list.append(self.X[support_indices])
            y_support_list.append(np.full(len(support_indices), cls))
            
            X_query_list.append(self.X[query_indices])
            y_query_list.append(np.full(len(query_indices), cls))
        
        # Concatenate
        X_support = np.vstack(X_support_list)
        y_support = np.concatenate(y_support_list)
        X_query = np.vstack(X_query_list)
        y_query = np.concatenate(y_query_list)
        
        return X_support, y_support, X_query, y_query


def benchmark_few_shot(
    X: np.ndarray,
    y: np.ndarray,
    n_episodes: int = 50,
    n_support: int = 5
) -> Dict:
    """
    Benchmark few-shot learning performance.
    
    Args:
        X: Feature matrix
        y: Labels
        n_episodes: Number of test episodes
        n_support: Support examples per class
        
    Returns:
        Dict with average metrics
    """
    logger.info(f"Benchmarking few-shot learning with {n_episodes} episodes...")
    
    # Initialize sampler
    sampler = FewShotEpisodeSampler(
        X, y,
        n_way=2,
        n_support=n_support,
        n_query=15
    )
    
    # Test different models
    models = {
        'RandomForest': FewShotLearner('rf'),
        'LogisticRegression': FewShotLearner('lr'),
        'ProtoNet': FewShotLearner('protonet')
    }
    
    results = {name: [] for name in models.keys()}
    
    for episode in range(n_episodes):
        # Sample episode
        X_sup, y_sup, X_qry, y_qry = sampler.sample_episode()
        
        # Test each model
        for name, model in models.items():
            metrics = model.evaluate_few_shot(X_sup, y_sup, X_qry, y_qry)
            results[name].append(metrics)
        
        if (episode + 1) % 10 == 0:
            logger.info(f"Completed {episode + 1}/{n_episodes} episodes")
    
    # Aggregate results
    summary = {}
    for name, episodes in results.items():
        summary[name] = {
            'accuracy': np.mean([e['accuracy'] for e in episodes]),
            'f1': np.mean([e['f1'] for e in episodes]),
            'std_accuracy': np.std([e['accuracy'] for e in episodes])
        }
    
    return summary


if __name__ == "__main__":
    # Test few-shot learning
    print("="*70)
    print("FEW-SHOT LEARNING TEST")
    print("="*70)
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 200
    n_features = 10
    
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, 2, n_samples)
    
    print(f"\nDataset: {n_samples} samples, {n_features} features")
    print(f"Class distribution: {np.bincount(y)}")
    
    # Test Prototypical Networks
    print("\n[1/3] Testing Prototypical Networks...")
    protonet = ProtoNet(n_way=2, n_support=5)
    
    # Split into support and query
    n_support = 10
    X_support, X_query = X[:n_support], X[n_support:n_support+20]
    y_support, y_query = y[:n_support], y[n_support:n_support+20]
    
    protonet.fit(X_support, y_support)
    predictions = protonet.predict(X_query)
    accuracy = np.mean(predictions == y_query)
    print(f"  Accuracy: {accuracy:.3f}")
    
    # Test Few-Shot Learner
    print("\n[2/3] Testing Few-Shot Learner...")
    learner = FewShotLearner('rf')
    metrics = learner.evaluate_few_shot(X_support, y_support, X_query, y_query)
    print(f"  Accuracy: {metrics['accuracy']:.3f}")
    print(f"  F1-Score: {metrics['f1']:.3f}")
    
    # Benchmark
    print("\n[3/3] Running Few-Shot Benchmark (10 episodes)...")
    summary = benchmark_few_shot(X, y, n_episodes=10, n_support=5)
    
    print("\nBenchmark Results:")
    for model, metrics in summary.items():
        print(f"  {model}:")
        print(f"    Accuracy: {metrics['accuracy']:.3f} ± {metrics['std_accuracy']:.3f}")
        print(f"    F1-Score: {metrics['f1']:.3f}")
    
    print("\n[SUCCESS] Few-shot learning test completed!")

