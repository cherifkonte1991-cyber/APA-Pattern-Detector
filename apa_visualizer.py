import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np
from apa_detector import APAPatternDetector

class APAVisualizer:
    """
    Visualise les patterns APA détectés avec flèches et zones d'entrée
    """
    
    def __init__(self, prices, figsize=(16, 8)):
        """
        Initialise le visualiseur
        
        Args:
            prices: Liste des prix
            figsize: Taille de la figure (largeur, hauteur)
        """
        self.prices = prices
        self.figsize = figsize
        self.detector = None
        
    def detect_and_plot(self, tolerance=0.02, min_distance=10):
        """
        Détecte les patterns APA et les affiche avec flèches d'entrée
        
        Args:
            tolerance: Tolérance en % pour identifier les sommets
            min_distance: Distance minimale entre les points du pattern
        """
        # Détecte les patterns
        self.detector = APAPatternDetector(self.prices, tolerance=tolerance)
        patterns = self.detector.detect_apa_pattern(min_distance=min_distance)
        
        # Crée la figure
        fig, ax = plt.subplots(figsize=self.figsize, facecolor='#f8f9fa')
        
        # Affiche le graphique de prix
        x = np.arange(len(self.prices))
        ax.plot(x, self.prices, linewidth=2, color='#1e3a8a', label='Prix', zorder=1)
        ax.fill_between(x, self.prices, alpha=0.2, color='#3b82f6')
        
        # Couleurs pour les patterns
        colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#8b5cf6']
        
        # Affiche chaque pattern détecté
        for pattern_idx, pattern in enumerate(patterns):
            color = colors[pattern_idx % len(colors)]
            
            # Points du pattern
            idx_a1 = pattern['point_A1']['index']
            idx_p = pattern['point_P']['index']
            idx_a2 = pattern['point_A2']['index']
            
            price_a1 = pattern['point_A1']['price']
            price_p = pattern['point_P']['price']
            price_a2 = pattern['point_A2']['price']
            
            # Affiche les points du triangle
            ax.plot(idx_a1, price_a1, marker='o', markersize=12, color=color, 
                   markeredgecolor='black', markeredgewidth=2, zorder=5, label=f'Pattern #{pattern_idx+1} - A1')
            ax.plot(idx_p, price_p, marker='v', markersize=12, color=color, 
                   markeredgecolor='black', markeredgewidth=2, zorder=5, label=f'Pattern #{pattern_idx+1} - P')
            ax.plot(idx_a2, price_a2, marker='o', markersize=12, color=color, 
                   markeredgecolor='gold', markeredgewidth=3, zorder=5, label=f'Pattern #{pattern_idx+1} - A2 (Dernier Sommet)')
            
            # Trace les lignes du triangle
            ax.plot([idx_a1, idx_p], [price_a1, price_p], '--', color=color, linewidth=2, alpha=0.7, zorder=2)
            ax.plot([idx_p, idx_a2], [price_p, price_a2], '--', color=color, linewidth=2, alpha=0.7, zorder=2)
            ax.plot([idx_a1, idx_a2], [price_a1, price_a2], ':', color=color, linewidth=2, alpha=0.5, zorder=2)
            
            # ===== ZONE D'ENTRÉE =====
            entry_level = pattern['entry_zone']['level']
            entry_high = pattern['entry_zone']['tolerance_high']
            entry_low = pattern['entry_zone']['tolerance_low']
            
            # Zone d'entrée (rectangle hachuré)
            entry_zone_rect = mpatches.Rectangle(
                (idx_a2 - 2, entry_low), 
                20, 
                entry_high - entry_low,
                linewidth=2, 
                edgecolor=color, 
                facecolor=color,
                alpha=0.15,
                linestyle='--',
                zorder=3
            )
            ax.add_patch(entry_zone_rect)
            
            # Ligne horizontale de la zone d'entrée
            ax.axhline(y=entry_level, color=color, linestyle='-', linewidth=2, alpha=0.6, zorder=3)
            
            # ===== FLÈCHE D'ENTRÉE =====
            # Flèche pointant vers la zone d'entrée (du dernier sommet vers le bas)
            arrow_start_y = price_a2 + (price_a2 * 0.05)  # Un peu au-dessus du dernier sommet
            arrow_end_y = entry_level
            
            arrow = FancyArrowPatch(
                (idx_a2, arrow_start_y),
                (idx_a2, arrow_end_y),
                arrowstyle='-|>',
                mutation_scale=30,
                linewidth=3,
                color=color,
                zorder=6,
                alpha=0.8
            )
            ax.add_patch(arrow)
            
            # ===== LABELS =====
            # Label A1
            ax.annotate('A1\n(Sommet 1)', xy=(idx_a1, price_a1), 
                       xytext=(idx_a1-5, price_a1+price_a1*0.03),
                       fontsize=9, fontweight='bold', color=color,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.8),
                       ha='center', zorder=7)
            
            # Label P
            ax.annotate('P\n(Pivot)', xy=(idx_p, price_p), 
                       xytext=(idx_p, price_p-price_p*0.05),
                       fontsize=9, fontweight='bold', color=color,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.8),
                       ha='center', zorder=7)
            
            # Label A2 (Dernier Sommet)
            ax.annotate('A2\n(Dernier Sommet)', xy=(idx_a2, price_a2), 
                       xytext=(idx_a2+8, price_a2+price_a2*0.03),
                       fontsize=9, fontweight='bold', color=color,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='gold', edgecolor=color, alpha=0.9),
                       ha='left', zorder=7)
            
            # Label ZONE D'ENTRÉE
            ax.annotate('📍 ZONE D\'ENTRÉE\n(Niveau du Dernier Sommet)', 
                       xy=(idx_a2 + 5, entry_level),
                       xytext=(idx_a2 + 15, entry_level + price_a2*0.08),
                       fontsize=10, fontweight='bold', color=color,
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', edgecolor=color, linewidth=2, alpha=0.9),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2),
                       ha='left', zorder=7)
            
            # Label FLÈCHE D'ENTRÉE (SIGNAL)
            mid_arrow = (arrow_start_y + arrow_end_y) / 2
            ax.annotate('🎯 SIGNAL\nD\'ENTRÉE', 
                       xy=(idx_a2, mid_arrow),
                       xytext=(idx_a2 - 15, mid_arrow),
                       fontsize=11, fontweight='bold', color=color,
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#ff6b6b', edgecolor=color, linewidth=2, alpha=0.95),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2.5),
                       ha='right', zorder=7)
            
            # ===== NIVEAUX DE RISQUE =====
            stop_loss = pattern['stop_loss']
            profit_target = pattern['profit_target']
            
            # Stop Loss (ligne rouge pointillée)
            ax.axhline(y=stop_loss, color='red', linestyle=':', linewidth=2, alpha=0.7, zorder=3)
            ax.text(len(self.prices) - 1, stop_loss - price_a1*0.02, 
                   f'🛑 SL: {stop_loss:.2f}', fontsize=9, color='red', 
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                   ha='right', zorder=7)
            
            # Profit Target (ligne verte pointillée)
            ax.axhline(y=profit_target, color='green', linestyle=':', linewidth=2, alpha=0.7, zorder=3)
            ax.text(len(self.prices) - 1, profit_target + price_a1*0.02, 
                   f'🎯 TP: {profit_target:.2f}', fontsize=9, color='green',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                   ha='right', zorder=7)
        
        # Configuration du graphique
        ax.set_xlabel('Indice de Temps', fontsize=12, fontweight='bold')
        ax.set_ylabel('Prix', fontsize=12, fontweight='bold')
        ax.set_title('Détection du Pattern APA - Zones d\'Entrée avec Flèches de Signal', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#f8f9fa')
        
        plt.tight_layout()
        return fig, ax
    
    def show(self):
        """Affiche le graphique"""
        plt.show()
    
    def save(self, filename='apa_pattern_signals.png'):
        """Sauvegarde le graphique"""
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
        print(f"✅ Graphique sauvegardé: {filename}")
    
    def print_signals(self):
        """Affiche les signaux d'entrée détectés"""
        if not self.detector or not self.detector.patterns:
            print("❌ Aucun signal détecté")
            return
        
        print("\n" + "="*100)
        print("🎯 SIGNAUX D'ENTRÉE DÉTECTÉS".center(100))
        print("="*100 + "\n")
        
        entry_zones = self.detector.get_entry_zones()
        
        for idx, zone in enumerate(entry_zones, 1):
            print(f"\n📊 SIGNAL #{idx}")
            print(f"{'─'*100}")
            print(f"  ✓ Niveau d'entrée      : {zone['entry_level']:.4f}")
            print(f"  ✓ Range d'entrée       : {zone['entry_range_low']:.4f} - {zone['entry_range_high']:.4f}")
            print(f"  ✓ Stop Loss (SL)       : {zone['stop_loss']:.4f}")
            print(f"  ✓ Profit Target (TP)   : {zone['profit_target']:.4f}")
            print(f"  ✓ Ratio Risque/Reward  : {zone['risk_reward_ratio']:.2f}")
            print(f"\n  📈 Distance SL → Entrée : {(zone['entry_level'] - zone['stop_loss']):.4f}")
            print(f"  📈 Distance Entrée → TP : {(zone['profit_target'] - zone['entry_level']):.4f}")
            print(f"{'─'*100}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de données de prix
    prices = [100, 102, 101, 103, 102, 98, 97, 99, 100, 102, 
              103, 101, 102, 104, 105, 103, 104, 106, 105, 103,
              102, 104, 106, 105, 107, 108, 106, 107, 109, 110,
              108, 109, 111, 110, 112, 114, 113, 115, 114, 112,
              111, 113, 115, 114, 116, 118, 117, 119, 118, 116]
    
    # Crée le visualiseur
    visualizer = APAVisualizer(prices)
    
    # Détecte et affiche les patterns
    fig, ax = visualizer.detect_and_plot(tolerance=0.05, min_distance=5)
    
    # Affiche les signaux détectés
    visualizer.print_signals()
    
    # Sauvegarde le graphique
    visualizer.save('apa_pattern_signals.png')
    
    # Affiche le graphique
    visualizer.show()
