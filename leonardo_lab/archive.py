"""
Leonardo Lab — Evolution Archive Persistence
Implements the Evolution Archive (Phase 10) that persists evolutionary history 
to enable phenotypic memory and cumulative adaptation across execution sessions.

Tracks: generation, total_budget_spent, lineage (parent variant IDs + applied operators), 
and negative_constraints (failed variants and why they failed).

Provides load/save functionality and merge_generation for combining new data.
"""

import yaml
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import hashlib


@dataclass
class VariantRecord:
    """Record of a single variant in the evolutionary archive"""
    name: str
    generation: int
    mutation_operator: str  # M01, M02, M03, M04, M05
    changed_variable: str
    parent: str  # Parent variant name or "baseline"
    fitness_score: float
    effect_delta_fitness: float
    leverage_ratio: float
    environments_tested: List[str]
    key_insight: str
    status: str  # PASSED or REJECTED
    violated_invariant: Optional[str] = None
    failure_reason: Optional[str] = None
    negative_constraint_learned: Optional[str] = None
    mapping_confidence: Optional[str] = None  # For M02 transfers
    exceptions: Optional[str] = None  # For M02 - what does NOT transfer
    composition_risk: Optional[str] = None  # For queued variants
    individual_fitness: Optional[float] = None  # For queued variants


@dataclass
class GenerationData:
    """Record of a complete generation"""
    generation_number: int
    timestamp: str
    search_budget_consumed: Dict[str, float]
    iterations_remaining: int
    baseline_history: List[Dict[str, Any]]
    queued_for_composition: List[Dict[str, Any]]
    successful_mutations: List[Dict[str, Any]]
    failed_mutations: List[Dict[str, Any]]
    learned_constraints: List[str]
    parameter_sensitivity: Dict[str, List[Dict[str, Any]]]
    current_genome: Dict[str, Any]
    search_budget_remaining: Dict[str, Any]


class EvolutionArchive:
    """
    The Evolution Archive - phenotypic memory of the Leonardo Lab system.
    By persisting lineage, parameters, search budgets, and negative constraints 
    across runs, the lab behaves like a true computational organism capable 
    of cumulative adaptation.
    """
    
    def __init__(self, archive_path: str = "./.leonardo-lab/evolution_archive.yaml"):
        self.archive_path = Path(archive_path)
        self.archive_path.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = self._load_or_initialize()
    
    def _load_or_initialize(self) -> Dict[str, Any]:
        """Load existing archive or initialize new one"""
        if self.archive_path.exists():
            try:
                with open(self.archive_path, 'r') as f:
                    data = yaml.safe_load(f)
                return data if data else self._get_default_structure()
            except Exception as e:
                print(f"Warning: Could not load archive {self.archive_path}: {e}")
                return self._get_default_structure()
        else:
            return self._get_default_structure()
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """Get the default structure for a new archive"""
        return {
            'evolution_archive': {
                'system_identity': {},
                'generation': {
                    'number': 0,
                    'timestamp': '',
                    'search_budget_consumed': {'mutations': 0.0, 'simulations': 0.0, 'total': 0.0, 'remaining': 0.0},
                    'iterations_remaining': 0
                },
                'baseline_history': [],
                'queued_for_composition': [],
                'successful_mutations': [],
                'failed_mutations': [],
                'learned_constraints': [],
                'parameter_sensitivity': {
                    'high_leverage': [],
                    'low_leverage': []
                },
                'current_genome': {
                    'GASO': {
                        'generator': '',
                        'action': '',
                        'state': '',
                        'observer': '',
                        'feedback': ''
                    }
                },
                'search_budget_remaining': {
                    'generations_used': 0,
                    'max_iterations': 0,
                    'iterations_remaining': 0,
                    'budget_per_iteration': 0.0,
                    'budget_used_this_generation': 0.0,
                    'budget_accumulated_remaining': 0.0
                }
            }
        }
    
    def load(self) -> Dict[str, Any]:
        """Load the archive from disk"""
        self.data = self._load_or_initialize()
        return self.data
    
    def save(self) -> bool:
        """Save the archive to disk"""
        try:
            with open(self.archive_path, 'w') as f:
                yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving archive to {self.archive_path}: {e}")
            return False
    
    def merge_generation(self, new_generation_data: Dict[str, Any]) -> bool:
        """
        Merge a new generation's data into the archive.
        Increments generation number, aggregates expenditures, and appends discoveries.
        """
        try:
            archive = self.data['evolution_archive']
            
            # Increment generation number
            current_gen = archive['generation']['number']
            new_gen_num = current_gen + 1
            
            # Update system identity if provided
            if 'system_identity' in new_generation_data:
                archive['system_identity'].update(new_generation_data['system_identity'])
            
            # Create new generation record
            new_generation_record = {
                'number': new_gen_num,
                'timestamp': new_generation_data.get('timestamp', datetime.now().isoformat()),
                'search_budget_consumed': new_generation_data.get('search_budget_consumed', 
                                                              {'mutations': 0.0, 'simulations': 0.0, 'total': 0.0}),
                'iterations_remaining': new_generation_data.get('iterations_remaining', 0)
            }
            
            # Add to baseline history if winner data provided
            if 'winner' in new_generation_data:
                winner = new_generation_data['winner']
                baseline_entry = {
                    'generation': new_gen_num,
                    'label': winner.get('label', f'Generation {new_gen_num} Winner'),
                    'configuration': winner.get('configuration', {}),
                    'fitness_score': winner.get('fitness_score', 0.0),
                    'selected_variant': winner.get('selected_variant', f'Variant_{new_gen_num}'),
                    'delta_from_previous': winner.get('delta_from_previous', '')
                }
                archive['baseline_history'].append(baseline_entry)
            
            # Add successful mutations
            if 'successful_mutations' in new_generation_data:
                archive['successful_mutations'].extend(new_generation_data['successful_mutations'])
            
            # Add failed mutations (for negative constraint extraction)
            if 'failed_mutations' in new_generation_data:
                archive['failed_mutations'].extend(new_generation_data['failed_mutations'])
            
            # Add learned constraints
            if 'learned_constraints' in new_generation_data:
                archive['learned_constraints'].extend(new_generation_data['learned_constraints'])
            
            # Update parameter sensitivity
            if 'parameter_sensitivity' in new_generation_data:
                sensitivity = new_generation_data['parameter_sensitivity']
                if 'high_leverage' in sensitivity:
                    archive['parameter_sensitivity']['high_leverage'].extend(sensitivity['high_leverage'])
                if 'low_leverage' in sensitivity:
                    archive['parameter_sensitivity']['low_leverage'].extend(sensitivity['low_leverage'])
            
            # Update current genome
            if 'current_genome' in new_generation_data:
                archive['current_genome'] = new_generation_data['current_genome']
            
            # Update search budget remaining
            if 'search_budget_remaining' in new_generation_data:
                archive['search_budget_remaining'] = new_generation_data['search_budget_remaining']
            else:
                # Calculate remaining budget
                budget_per_iteration = archive['search_budget_remaining'].get('budget_per_iteration', 15.0)
                generations_used = archive['search_budget_remaining'].get('generations_used', 0) + 1
                iterations_remaining = archive['search_budget_remaining'].get('iterations_remaining', 9)
                budget_used = archive['search_budget_remaining'].get('budget_used_this_generation', 0.0)
                
                archive['search_budget_remaining'].update({
                    'generations_used': generations_used,
                    'iterations_remaining': iterations_remaining,
                    'budget_accumulated_remaining': budget_per_iteration * iterations_remaining
                })
            
            # Update generation counter
            archive['generation'] = new_generation_record
            
            # Save to disk
            return self.save()
            
        except Exception as e:
            print(f"Error merging generation data: {e}")
            return False
    
    def get_next_generation_number(self) -> int:
        """Get the next generation number to be used"""
        return self.data['evolution_archive']['generation']['number'] + 1
    
    def get_lineage(self, variant_name: str) -> List[str]:
        """
        Get the lineage (parent chain) for a variant.
        Returns list of variant names from oldest to newest.
        """
        lineage = []
        # This would search through successful/failed mutations to build lineage
        # Simplified implementation
        all_mutations = self.data['evolution_archive']['successful_mutations'] + \
                       self.data['evolution_archive']['failed_mutations']
        
        # Find the variant and trace parents
        visited = set()
        current = variant_name
        
        while current and current not in visited:
            visited.add(current)
            lineage.append(current)
            
            # Find parent of current variant
            parent_found = False
            for mutation in all_mutations:
                if mutation.get('name') == current:
                    parent = mutation.get('lineage', {}).get('parent', '')
                    if parent and parent != 'N/A — initial configuration':
                        current = parent
                        parent_found = True
                        break
            if not parent_found:
                break
                
        return lineage[::-1]  # Reverse to show oldest first
    
    def get_negative_constraints(self) -> List[str]:
        """Get all learned negative constraints from failed mutations"""
        constraints = []
        for mutation in self.data['evolution_archive']['failed_mutations']:
            if 'negative_constraint_learned' in mutation:
                constraints.append(mutation['negative_constraint_learned'])
        return constraints
    
    def get_high_leverage_variables(self) -> List[Dict[str, Any]]:
        """Get all high-leverage variables discovered"""
        return self.data['evolution_archive']['parameter_sensitivity']['high_leverage']
    
    def get_low_leverage_variables(self) -> List[Dict[str, Any]]:
        """Get all low-leverage variables discovered"""
        return self.data['evolution_archive']['parameter_sensitivity']['low_leverage']
    
    def get_current_genome(self) -> Dict[str, Any]:
        """Get the current GASO genome state"""
        return self.data['evolution_archive']['current_genome']
    
    def get_archive_summary(self) -> Dict[str, Any]:
        """Get a summary of the archive contents"""
        archive = self.data['evolution_archive']
        return {
            'current_generation': archive['generation']['number'],
            'total_variants_explored': len(archive['successful_mutations']) + len(archive['failed_mutations']),
            'successful_variants': len(archive['successful_mutations']),
            'failed_variants': len(archive['failed_mutations']),
            'learned_constraints_count': len(archive['learned_constraints']),
            'high_leverage_discoveries': len(archive['parameter_sensitivity']['high_leverage']),
            'low_leverage_discoveries': len(archive['parameter_sensitivity']['low_leverage']),
            'search_budget_used': archive['generation']['search_budget_consumed']['total'],
            'search_budget_remaining': archive['search_budget_remaining']['budget_accumulated_remaining']
        }


# Convenience functions
def create_archive(archive_path: str = "./.leonardo-lab/evolution_archive.yaml") -> EvolutionArchive:
    """Factory function to create an EvolutionArchive instance"""
    return EvolutionArchive(archive_path)

def load_archive(archive_path: str = "./.leonardo-lab/evolution_archive.yaml") -> Dict[str, Any]:
    """Load an existing archive"""
    archive = EvolutionArchive(archive_path)
    return archive.load()

def save_archive(data: Dict[str, Any], archive_path: str = "./.leonardo-lab/evolution_archive.yaml") -> bool:
    """Save data to archive"""
    archive = EvolutionArchive(archive_path)
    archive.data = data
    return archive.save()