try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

from typing import List, Dict
from models import Rule, RuleResult

def generate_rule_graph(rules: List[Rule], results: List[RuleResult] = None) -> "graphviz.Digraph":
    """
    Generates a Graphviz Digraph visualizing the rules.
    If 'results' is provided, colors nodes green/red based on pass/fail.
    """
    if not GRAPHVIZ_AVAILABLE:
        return None

    dot = graphviz.Digraph(comment='Rule Logic')
    dot.attr(rankdir='LR')  # Left-to-Right orientation
    
    # Create a lookup for results if available
    result_map = {r.id: r.passed for r in results} if results else {}

    # 1. Start Node
    dot.node('Start', 'Start Evaluation', shape='oval', style='filled', fillcolor='lightblue')

    # 2. Rule Nodes
    for i, rule in enumerate(rules):
        color = 'white'
        if result_map:
            if rule.id in result_map:
                color = 'lightgreen' if result_map[rule.id] else 'lightpink'
        
        label = f"{rule.name}\n({rule.id})"
        dot.node(rule.id, label, shape='box', style='filled', fillcolor=color)

        # Connect Start to first rules, or chain them sequentially?
        # For simplicity in this linear list, we chain them, or connect Start to all 'High' priority?
        # Let's connect them sequentially for a "flow" effect, 
        # or all from Start if they calculate in parallel.
        # Parallel is more accurate to the engine logic.
        dot.edge('Start', rule.id)

    # 3. Decision Node (Conceptual)
    dot.node('End', 'Decision', shape='doubleoctagon', style='filled', fillcolor='gold')
    
    for rule in rules:
        dot.edge(rule.id, 'End')

    return dot
