"""
Leonardo Lab — Simulation Models
Implements simulated environments representing the two baseline case studies:
1. Wiener Cybernetics A4 Neural Model
2. Cybernetic Reasoning Engine (CRE) v2.0

These provide fitness functions and failure mechanisms for testing the 
GASO state machine evolutionary pipeline.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional


class WienerA4NeuralModel:
    """
    Wiener's Cybernetics A4 Neural Model - simulates neural alpha-rhythm 
    signal generation with predictor horizon and feedback coefficient.
    
    Based on Norbert Wiener's cybernetic alpha-rhythm neural model from 
    "Cybernetics" (1948/1950).
    """
    
    def __init__(self, predictor_horizon: float = 0.1, feedback_coefficient: float = 0.5):
        """
        Initialize the Wiener A4 neural model.
        
        Args:
            predictor_horizon: Temporal prediction window in seconds (baseline: 0.1s, target: 0.35s)
            feedback_coefficient: Feedback loop gain (0.0 to 1.0)
        """
        self.predictor_horizon = predictor_horizon
        self.feedback_coefficient = feedback_coefficient
        self.alpha_rhythm_frequency = 10.0  # Hz (typical alpha rhythm)
        self.alpha_rhythm_period = 1.0 / self.alpha_rhythm_frequency  # 0.1 seconds
        
    def compute_fitness(self) -> float:
        """
        Evaluate signal regeneration match against neural alpha-rhythm frequency.
        
        Returns:
            Fitness score between 0.0 and 1.0
        """
        # Base fitness calculation
        # Optimal predictor_horizon for alpha rhythm (0.1s period) is 0.35s
        # (allows 3.5 cycles of prediction)
        horizon_match = 1.0 - abs(self.predictor_horizon - 0.35) / 0.35
        
        # Feedback coefficient stability
        feedback_score = 1.0 - abs(self.feedback_coefficient - 0.7)
        
        # Combine scores with weighting
        fitness = 0.6 * horizon_match + 0.4 * feedback_score
        return max(0.0, min(1.0, fitness))
    
    def simulate(self, steps: int = 100) -> Dict[str, float]:
        """
        Run a simulation of the neural model for the given number of steps.
        
        Returns:
            Dictionary with simulation results
        """
        # Simulate alpha rhythm signal
        signal = []
        for t in range(steps):
            # Generate alpha rhythm component
            phase = 2 * math.pi * self.alpha_rhythm_frequency * t * 0.001  # ms to s
            amplitude = 1.0
            signal.append(amplitude * math.sin(phase))
        
        # Calculate signal regeneration quality
        signal_array = np.array(signal)
        mean_amplitude = np.mean(np.abs(signal_array))
        std_amplitude = np.std(signal_array)
        
        # Signal stability metric
        stability = 1.0 - (std_amplitude / mean_amplitude) if mean_amplitude > 0 else 0.0
        
        return {
            'mean_amplitude': float(mean_amplitude),
            'signal_stability': float(stability),
            'predictor_horizon': self.predictor_horizon,
            'feedback_coefficient': self.feedback_coefficient,
            'fitness_score': self.compute_fitness()
        }
    
    def check_entropy_violation(self, feedback_threshold: float) -> bool:
        """
        Check if a given feedback threshold would violate second-law compliance.
        
        An asymmetric threshold (e.g., negative or > 1.0) violates entropy monotonicity.
        
        Returns:
            True if violation occurs
        """
        if feedback_threshold < 0.0 or feedback_threshold > 1.0:
            return True
        # Asymmetric thresholds also violate
        if abs(feedback_threshold - 0.5) > 0.4:
            return True
        return False


class CyberneticReasoningEngine:
    """
    Cybernetic Reasoning Engine (CRE) / Generative Eigen-Engine v2.0
    Simulates attractor-state stability with stability threshold and 
    novelty injection rate.
    """
    
    def __init__(self, stability_threshold: float = 1e-3, novelty_injection_rate: float = 0.05):
        """
        Initialize the CRE model.
        
        Args:
            stability_threshold: Threshold for attractor stability (baseline: 1e-3, target: 1e-4)
            novelty_injection_rate: Rate of novelty injection (0.0 to 1.0)
        """
        self.stability_threshold = stability_threshold
        self.novelty_injection_rate = novelty_injection_rate
        self.attractor_count = 5
        self.history_compression_rate = 0.1
        
    def compute_fitness(self) -> float:
        """
        Evaluate stability and novelty injection effectiveness.
        
        Returns:
            Fitness score between 0.0 and 1.0
        """
        # Optimal stability threshold is 1e-4 (more precise)
        # Closer to 1e-4 = higher fitness
        threshold_diff = abs(self.stability_threshold - 1e-4)
        threshold_fitness = 1.0 - min(1.0, threshold_diff / 1e-3)
        
        # Novelty injection rate: optimal around 0.05
        novelty_diff = abs(self.novelty_injection_rate - 0.05)
        novelty_fitness = 1.0 - min(1.0, novelty_diff / 0.1)
        
        # Combine
        fitness = 0.7 * threshold_fitness + 0.3 * novelty_fitness
        return max(0.0, min(1.0, fitness))
    
    def simulate(self, steps: int = 1000) -> Dict[str, float]:
        """
        Simulate the reasoning engine dynamics.
        
        Returns:
            Dictionary with simulation results
        """
        # Simulate attractor state evolution
        states = []
        current_state = 0.0
        
        for step in range(steps):
            # Attractor dynamics with noise
            noise = np.random.normal(0, self.novelty_injection_rate)
            current_state += noise
            
            # Stability check
            if abs(current_state) < self.stability_threshold:
                current_state = 0.0  # Snap to attractor
            
            states.append(current_state)
        
        states = np.array(states)
        
        # Calculate stability metric
        stable_states = np.sum(np.abs(states) < self.stability_threshold * 10) / len(states)
        
        # Novelty rate (variance)
        novelty_metric = float(np.std(states))
        
        return {
            'stability_threshold': self.stability_threshold,
            'novelty_injection_rate': self.novelty_injection_rate,
            'stability_metric': float(stable_states),
            'novelty_metric': novelty_metric,
            'fitness_score': self.compute_fitness()
        }
    
    def check_market_transfer_viability(self) -> Tuple[bool, str]:
        """
        Check if transferring this model to a market domain is viable.
        
        Returns:
            (is_viable, reason)
        """
        # Market domain lacks biological-equivalent reset mechanism
        # Without a reset mechanism, the system cannot recover from novel states
        if self.novelty_injection_rate > 0.1:
            return (False, "Excessive novelty injection without biological reset mechanism")
        
        # The model requires an internal "attractor" concept that markets don't have
        return (False, "Market systems lack biological-equivalent attractor reset mechanism")


class WaterwheelModel:
    """
    Simple test model for the waterwheel - used in integration tests.
    Represents a physical system with channel_width and friction_coefficient.
    """
    
    def __init__(self, channel_width: float = 1.0, friction_coefficient: float = 0.1):
        self.channel_width = channel_width
        self.friction_coefficient = friction_coefficient
    
    def compute_fitness(self) -> float:
        """
        Fitness function: maximize throughput, minimize friction.

        Physics:
          - Channel width dominates throughput with a steep linear response
            up to saturation at 2.5 m (weight 0.75).
          - Friction is inert below the seizure threshold (0.30): variations
            in this regime do not affect output (dead zone). Beyond it,
            performance degrades steeply.
        """
        # Channel width: steep response saturating at 2.5 m
        width_fitness = min(1.0, self.channel_width / 2.5)

        # Friction dead zone below 0.30; steep penalty beyond
        if self.friction_coefficient <= 0.30:
            friction_fitness = 1.0
        else:
            friction_fitness = max(
                0.0, 1.0 - (self.friction_coefficient - 0.30) * 5.0)

        return 0.75 * width_fitness + 0.25 * friction_fitness


class DoorHingeModel:
    """
    Simple test model for door hinge - used in end-to-end tests.
    """
    
    def __init__(self, pivot_diameter: float = 0.5, friction_coefficient: float = 0.1):
        self.pivot_diameter = pivot_diameter
        self.friction_coefficient = friction_coefficient
    
    def compute_fitness(self) -> float:
        """
        Fitness function: optimize pivot diameter (larger is better) and 
        reduce friction.
        """
        pivot_fitness = min(1.0, self.pivot_diameter / 1.0)
        friction_fitness = 1.0 - min(1.0, self.friction_coefficient / 0.3)
        return 0.6 * pivot_fitness + 0.4 * friction_fitness


def simulate_wiener_a4(predictor_horizon: float, feedback_coefficient: float) -> Dict[str, float]:
    """Convenience function to run a Wiener A4 simulation"""
    model = WienerA4NeuralModel(predictor_horizon, feedback_coefficient)
    return model.simulate()


def simulate_cre(stability_threshold: float, novelty_injection_rate: float) -> Dict[str, float]:
    """Convenience function to run a CRE simulation"""
    model = CyberneticReasoningEngine(stability_threshold, novelty_injection_rate)
    return model.simulate()


def simulate_waterwheel(channel_width: float, friction_coefficient: float) -> Dict[str, float]:
    """Convenience function to run a waterwheel simulation"""
    model = WaterwheelModel(channel_width, friction_coefficient)
    return {
        'channel_width': channel_width,
        'friction_coefficient': friction_coefficient,
        'fitness_score': model.compute_fitness()
    }


def simulate_door_hinge(pivot_diameter: float, friction_coefficient: float) -> Dict[str, float]:
    """Convenience function to run a door hinge simulation"""
    model = DoorHingeModel(pivot_diameter, friction_coefficient)
    return {
        'pivot_diameter': pivot_diameter,
        'friction_coefficient': friction_coefficient,
        'fitness_score': model.compute_fitness()
    }