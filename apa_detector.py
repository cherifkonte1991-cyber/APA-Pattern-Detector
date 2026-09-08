import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class APAPatternDetector:
    """
    Détecteur de pattern APA (Triangle) pour l'analyse technique des marchés
    
    Le pattern APA se compose de :
    - Point A : Premier sommet (haut)
    - Point P : Pivot bas (point bas du triangle)
    - Point A : Dernier sommet (haut)
    
    Zone d'entrée : détectée au niveau du dernier sommet du A
    """
    
    def __init__(self, prices: List[float], tolerance: float = 0.02):
        """
        Initialise le détecteur
        
        Args:
            prices: Liste des prix
            tolerance: Tolérance en % pour identifier les sommets (défaut: 2%)
        """
        self.prices = np.array(prices)
        self.tolerance = tolerance
        self.patterns = []
        
    def find_peaks_valleys(self, window: int = 5) -> Tuple[List[int], List[int]]:
        """
        Identifie les pics (sommets) et les vallées (creux)
        
        Args:
            window: Taille de la fenêtre pour déterminer les extrema
            
        Returns:
            Tuple (indices_pics, indices_vallees)
        """
        peaks = []
        valleys = []
        
        for i in range(window, len(self.prices) - window):
            # Cherche les pics (sommets)
            if self.prices[i] == max(self.prices[i-window:i+window+1]):
                peaks.append(i)
            # Cherche les vallées (creux)
            if self.prices[i] == min(self.prices[i-window:i+window+1]):
                valleys.append(i)
        
        return peaks, valleys
    
    def detect_apa_pattern(self, min_distance: int = 10) -> List[Dict]:
        """
        Détecte les patterns APA dans les données de prix
        
        Args:
            min_distance: Distance minimale entre les points du pattern
            
        Returns:
            Liste des patterns détectés avec leurs caractéristiques
        """
        peaks, valleys = self.find_peaks_valleys()
        
        self.patterns = []
        
        # Cherche les combinaisons A-P-A
        for i in range(len(peaks)):
            for j in range(i + 1, len(valleys)):
                for k in range(j + 1, len(peaks)):
                    idx_a1 = peaks[i]
                    idx_p = valleys[j]
                    idx_a2 = peaks[k]
                    
                    # Vérifie les distances minimales
                    if (idx_p - idx_a1 < min_distance or 
                        idx_a2 - idx_p < min_distance):
                        continue
                    
                    price_a1 = self.prices[idx_a1]
                    price_p = self.prices[idx_p]
                    price_a2 = self.prices[idx_a2]
                    
                    # Vérifie que les deux A sont proches (tolérance)
                    diff_percent = abs(price_a1 - price_a2) / price_a1
                    
                    if diff_percent <= self.tolerance:
                        pattern = {
                            'type': 'APA',
                            'point_A1': {
                                'index': idx_a1,
                                'price': price_a1,
                                'position': 'Sommet 1'
                            },
                            'point_P': {
                                'index': idx_p,
                                'price': price_p,
                                'position': 'Pivot Bas'
                            },
                            'point_A2': {
                                'index': idx_a2,
                                'price': price_a2,
                                'position': 'Sommet 2 (Dernier Sommet)'
                            },
                            'entry_zone': {
                                'level': price_a2,
                                'description': f'Zone d\'entrée au niveau du dernier sommet A: {price_a2:.2f}',
                                'tolerance_high': price_a2 * (1 + self.tolerance),
                                'tolerance_low': price_a2 * (1 - self.tolerance)
                            },
                            'stop_loss': price_p,
                            'profit_target': price_p + (price_a1 - price_p) * 1.5,
                            'ratio_hauteur': (price_a1 - price_p) / price_p
                        }
                        self.patterns.append(pattern)
        
        return self.patterns
    
    def get_entry_zones(self) -> List[Dict]:
        """
        Retourne les zones d'entrée (niveau du dernier sommet A)
        
        Returns:
            Liste des zones d'entrée recommandées
        """
        entry_zones = []
        
        for pattern in self.patterns:
            entry_zones.append({
                'pattern_id': len(entry_zones),
                'entry_level': pattern['entry_zone']['level'],
                'entry_range_high': pattern['entry_zone']['tolerance_high'],
                'entry_range_low': pattern['entry_zone']['tolerance_low'],
                'stop_loss': pattern['stop_loss'],
                'profit_target': pattern['profit_target'],
                'risk_reward_ratio': (pattern['profit_target'] - pattern['entry_zone']['level']) / 
                                    (pattern['entry_zone']['level'] - pattern['stop_loss'])
                if pattern['entry_zone']['level'] > pattern['stop_loss'] else 0
            })
        
        return entry_zones
    
    def print_detected_patterns(self):
        """Affiche les patterns détectés de manière lisible"""
        if not self.patterns:
            print("❌ Aucun pattern APA détecté")
            return
        
        print(f"\n✅ {len(self.patterns)} pattern(s) APA détecté(s)\n")
        print("="*80)
        
        for idx, pattern in enumerate(self.patterns, 1):
            print(f"\n🔷 PATTERN #{idx}")
            print(f"{'─'*80}")
            print(f"  Point A1 (Sommet 1)     : Indice={pattern['point_A1']['index']:<4} | Prix={pattern['point_A1']['price']:.2f}")
            print(f"  Point P  (Pivot Bas)    : Indice={pattern['point_P']['index']:<4} | Prix={pattern['point_P']['price']:.2f}")
            print(f"  Point A2 (Dernier Sommet): Indice={pattern['point_A2']['index']:<4} | Prix={pattern['point_A2']['price']:.2f}")
            print(f"\n  📍 ZONE D'ENTRÉE (au niveau du dernier sommet A):")
            print(f"     Niveau d'entrée    : {pattern['entry_zone']['level']:.2f}")
            print(f"     Range d'entrée     : {pattern['entry_zone']['tolerance_low']:.2f} - {pattern['entry_zone']['tolerance_high']:.2f}")
            print(f"  🛑 Stop Loss            : {pattern['stop_loss']:.2f}")
            print(f"  🎯 Profit Target        : {pattern['profit_target']:.2f}")
            print(f"  📊 Ratio Risque/Reward : {(pattern['profit_target'] - pattern['entry_zone']['level']) / (pattern['entry_zone']['level'] - pattern['stop_loss']):.2f}")
            print(f"{'─'*80}")
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convertit les patterns en DataFrame pandas"""
        data = []
        
        for idx, pattern in enumerate(self.patterns, 1):
            data.append({
                'Pattern_ID': idx,
                'A1_Index': pattern['point_A1']['index'],
                'A1_Price': pattern['point_A1']['price'],
                'P_Index': pattern['point_P']['index'],
                'P_Price': pattern['point_P']['price'],
                'A2_Index': pattern['point_A2']['index'],
                'A2_Price': pattern['point_A2']['price'],
                'Entry_Level': pattern['entry_zone']['level'],
                'Entry_High': pattern['entry_zone']['tolerance_high'],
                'Entry_Low': pattern['entry_zone']['tolerance_low'],
                'Stop_Loss': pattern['stop_loss'],
                'Profit_Target': pattern['profit_target'],
                'Risk_Reward': (pattern['profit_target'] - pattern['entry_zone']['level']) / 
                              (pattern['entry_zone']['level'] - pattern['stop_loss'])
            })
        
        return pd.DataFrame(data)
