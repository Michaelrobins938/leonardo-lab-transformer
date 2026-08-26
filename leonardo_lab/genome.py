"""
Leonardo Lab — Initial Genome Ruleset
Implements the Da Vinci Ontological spine that recasts physical systems to 
abstract primitives: {source, sink, channel, apex, gradient, role}.

Prevents domain-specific nouns (e.g., 'blood', 'eye', 'water') from entering 
the abstract core optimization. Provides functions to strip/translate domain 
terminology and defines Da Vinci's core structural constraints as invariants:
  * i01 (Second-Law Compliance / Entropy Monotonicity)
  * i02 (Loop Closure / Path Integrity) 
  * i03 (Capacity Bound: Channel Capacity >= Message Variety)
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DaVinciPrimitive(Enum):
    """The six abstract primitives from Leonardo's notebooks"""
    SOURCE = "source"      # Primary moving force / driver
    SINK = "sink"          # Where flow terminates / resistance
    CHANNEL = "channel"    # Propagation pathway
    APEX = "apex"          # Convergence point / observation
    GRADIENT = "gradient"  # Potential difference / force
    ROLE = "role"          # Functional role in system


@dataclass
class DaVinciConstraint:
    """Represents a structural constraint derived from Leonardo's notebooks"""
    id: str
    name: str
    description: str
    formal_expression: str
    cross_domain_occurrences: List[str]


class LeonardoGenome:
    """
    The Initial Genome Ruleset - extracts structural mechanics from 
    Leonardo da Vinci's scientific notebooks and maps them to 
    domain-agnostic computational primitives.
    """
    
    def __init__(self):
        # Domain-specific terms to avoid in abstract core (from Leonardo's texts)
        self.domain_specific_terms: Set[str] = {
            'eye', 'blood', 'water', 'soul', 'body', 'organ', 'instrument',
            'pyramid', 'furrow', 'vein', 'artery', 'nerve', 'muscle',
            'tide', 'ocean', 'spring', 'rain', 'evaporation', 'absorption',
            'weight', 'force', 'impulse', 'resistance',  # These are the 4 external powers
            'necessity', 'potency',  # Constraint generators
            'light', 'shade', 'shadow', 'reflection',
            'temperature', 'heat', 'cold',
            'sound', 'noise', 'pitch', 'tone',
            'color', 'hue', 'saturation', 'brightness',
            'smell', 'odor', 'fragrance', 'stench',
            'taste', 'flavor', 'sweet', 'sour', 'bitter', 'salty',
            'touch', 'pressure', 'texture', 'rough', 'smooth',
            'time', 'duration', 'frequency', 'period',
            'space', 'distance', 'length', 'width', 'height', 'depth',
            'motion', 'movement', 'velocity', 'speed', 'acceleration',
            'position', 'location', 'direction', 'angle', 'orientation',
            'mass', 'volume', 'density', 'pressure', 'temperature',
            'energy', 'work', 'power', 'heat', 'entropy'
        }
        
        # Da Vinci's core structural constraints (invariants)
        self.constraints: Dict[str, DaVinciConstraint] = {
            'i01': DaVinciConstraint(
                id='i01',
                name='Second-Law Compliance / Entropy Monotonicity',
                description='Prevents thermodynamic violations - entropy must not decrease in isolated systems',
                formal_expression='ΔS ≥ 0 for isolated systems',
                cross_domain_occurrences=['thermodynamics', 'information theory', 'statistical mechanics']
            ),
            'i02': DaVinciConstraint(
                id='i02',
                name='Loop Closure / Path Integrity',
                description='Ensures all feedback paths form a closed, complete loop',
                formal_expression='∮ F·dr = 0 for conservative fields',
                cross_domain_occurrences=['vector calculus', 'electromagnetism', 'fluid dynamics', 'control theory']
            ),
            'i03': DaVinciConstraint(
                id='i03',
                name='Capacity Bound',
                description='Ensures total communication channel capacity matches or exceeds message variety',
                formal_expression='C ≥ log₂(M) where C=capacity, M=message variety',
                cross_domain_occurrences=['information theory', 'communication theory', 'network theory', 'coding theory']
            )
        }
        
        # Leonardo's Four Primitive External Powers (from Philosophical Maxims)
        self.external_powers = {
            'weight': 'state-bias / inertia',
            'force': 'driver / primary moving force', 
            'casual_impulse': 'perturbation / external disturbance',
            'resistance': 'constraint / opposition to flow'
        }
        
        # Necessity as Supreme Constraint-Generator
        self.necessity_principle = {
            'description': 'Necessity is the mistress and guide of nature - the eternal curb and law of nature',
            'formal_expression': 'Transition function is total and single-valued',
            'generates': ['determinism', 'role_preservation']
        }

    def strip_domain_terminology(self, text: str) -> str:
        """
        Remove domain-specific terminology to extract abstract structural essence.
        Based on Leonardo's approach of removing terms like 'eye', 'blood', 'water'.
        """
        # Convert to lowercase for matching
        lower_text = text.lower()
        
        # Remove domain-specific terms
        cleaned_text = lower_text
        for term in self.domain_specific_terms:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text if cleaned_text else text  # Return original if all stripped

    def map_to_primitives(self, system_description: str) -> Dict[DaVinciPrimitive, List[str]]:
        """
        Map a system description to Leonardo's six abstract primitives.
        This is the core ontological reduction function.
        """
        # Initialize mapping
        primitive_mapping: Dict[DaVinciPrimitive, List[str]] = {
            primitive: [] for primitive in DaVinciPrimitive
        }
        
        # Clean the description
        cleaned_desc = self.strip_domain_terminology(system_description)
        
        # Simple heuristic mapping based on semantic roles
        # In practice, this would use more sophisticated NLP or rule-based extraction
        words = cleaned_desc.lower().split()
        
        # Mapping heuristics (simplified for implementation)
        source_indicators = ['source', 'origin', 'beginning', 'start', 'input', 'driver', 'force', 'power']
        sink_indicators = ['sink', 'end', 'termination', 'output', 'load', 'resistance', 'ground']
        channel_indicators = ['channel', 'path', 'way', 'route', 'conduit', 'medium', 'link', 'connection']
        apex_indicators = ['apex', 'peak', 'summit', 'top', 'point', 'focus', 'center', 'convergence']
        gradient_indicators = ['gradient', 'difference', 'delta', 'change', 'slope', 'rate', 'potential']
        role_indicators = ['role', 'function', 'purpose', 'role', 'job', 'task', 'duty']
        
        for word in words:
            if any(indicator in word for indicator in source_indicators):
                primitive_mapping[DaVinciPrimitive.SOURCE].append(word)
            elif any(indicator in word for indicator in sink_indicators):
                primitive_mapping[DaVinciPrimitive.SINK].append(word)
            elif any(indicator in word for indicator in channel_indicators):
                primitive_mapping[DaVinciPrimitive.CHANNEL].append(word)
            elif any(indicator in word for indicator in apex_indicators):
                primitive_mapping[DaVinciPrimitive.APEX].append(word)
            elif any(indicator in word for indicator in gradient_indicators):
                primitive_mapping[DaVinciPrimitive.GRADIENT].append(word)
            elif any(indicator in word for indicator in role_indicators):
                primitive_mapping[DaVinciPrimitive.ROLE].append(word)
        
        # Remove duplicates
        for primitive in primitive_mapping:
            primitive_mapping[primitive] = list(set(primitive_mapping[primitive]))
            
        return primitive_mapping

    def get_constraint(self, constraint_id: str) -> Optional[DaVinciConstraint]:
        """Get a specific Da Vinci constraint by ID"""
        return self.constraints.get(constraint_id)

    def get_all_constraints(self) -> Dict[str, DaVinciConstraint]:
        """Get all Da Vinci structural constraints"""
        return self.constraints.copy()

    def validate_against_constraints(self, system_state: Dict) -> List[str]:
        """
        Validate a system state against Da Vinci's structural constraints.
        Returns list of violated constraint IDs.
        """
        violated = []
        
        # Simplified validation - in practice would be more sophisticated
        # For i01: Check entropy monotonicity (placeholder)
        if 'entropy_change' in system_state and system_state['entropy_change'] < 0:
            violated.append('i01')
            
        # For i02: Check loop closure (placeholder)  
        if 'loop_integral' in system_state and abs(system_state['loop_integral']) > 1e-10:
            violated.append('i02')
            
        # For i03: Check capacity bound (placeholder)
        if 'channel_capacity' in system_state and 'message_variety' in system_state:
            import math
            required_capacity = math.log2(system_state['message_variety'])
            if system_state['channel_capacity'] < required_capacity:
                violated.append('i03')
                
        return violated

    def get_external_powers(self) -> Dict[str, str]:
        """Get Leonardo's Four Primitive External Powers"""
        return self.external_powers.copy()

    def get_necessity_principle(self) -> Dict:
        """Get the Necessity as Supreme Constraint-Generator principle"""
        return self.necessity_principle.copy()


# Convenience functions for external use
def create_genome() -> LeonardoGenome:
    """Factory function to create a LeonardoGenome instance"""
    return LeonardoGenome()

def strip_domain_terms(text: str) -> str:
    """Convenience function to strip domain-specific terminology"""
    genome = LeonardoGenome()
    return genome.strip_domain_terminology(text)

def map_to_da_vinci_primitives(system_description: str) -> Dict[DaVinciPrimitive, List[str]]:
    """Convenience function to map system to Da Vinci's six primitives"""
    genome = LeonardoGenome()
    return genome.map_to_primitives(system_description)