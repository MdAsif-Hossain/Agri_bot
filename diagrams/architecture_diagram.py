import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture_diagram():
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.axis('off')
    
    # Adjust axis limits to give enough drawing canvas
    ax.set_xlim(0, 18)
    ax.set_ylim(1, 11)

    # Box styling variables
    box_w = 2.8
    box_h = 1.2
    
    client_color = '#dbeafe'    # Light blue
    api_color = '#fef08a'       # Yellow
    engine_color = '#fbcfe8'    # Pink
    model_color = '#d1fae5'     # Green
    db_color = '#f1f5f9'        # Gray
    edge_color = '#374151'
    text_color = '#1f2937'

    # Node definitions: name is the key, value is a dict with details
    nodes = {
        'Kiosk': {'title': 'React Kiosk (Desktop)', 'pos': (1, 8), 'color': client_color},
        'Mobile': {'title': 'Mobile Thin Client', 'pos': (1, 6), 'color': client_color},
        
        'API': {'title': 'FastAPI Orchestrator', 'pos': (5.5, 7), 'color': api_color},
        
        'ASR': {'title': 'ASR Module\n(faster-whisper)', 'pos': (10, 8.5), 'color': engine_color},
        'LangGraph': {'title': 'LangGraph Engine\n(Agent Workflow)', 'pos': (10, 6), 'color': engine_color},
        
        'LLM': {'title': 'Local LLM\n(llama.cpp + Qwen 2.5)', 'pos': (10, 3.5), 'color': model_color},
        
        'FAISS': {'title': 'FAISS + BM25\n(Document Index)', 'pos': (14.5, 7.5), 'color': db_color},
        'SQLite': {'title': 'SQLite Graph\n(Dialect KG)', 'pos': (14.5, 4.5), 'color': db_color}
    }

    # Define directional connections (from_node, to_node)
    edges = [
        ('Kiosk', 'API'),
        ('Mobile', 'API'),
        ('API', 'ASR'),
        ('API', 'LangGraph'),
        ('LangGraph', 'LLM'),
        ('LangGraph', 'FAISS'),
        ('LangGraph', 'SQLite')
    ]

    # Draw boxes
    for name, data in nodes.items():
        x, y = data['pos']
        # Calculate center for arrow endpoints
        data['center'] = (x + box_w/2, y + box_h/2)
        
        rect = patches.FancyBboxPatch(
            (x, y), box_w, box_h, 
            boxstyle="round,pad=0.1,rounding_size=0.15", 
            linewidth=2, edgecolor=edge_color, 
            facecolor=data['color'], zorder=2
        )
        ax.add_patch(rect)
        
        ax.text(x + box_w/2, y + box_h/2, data['title'], 
                ha='center', va='center', fontsize=11, fontweight='bold', color=text_color, zorder=3)

    # Function to draw an arrow between two node keys
    def draw_arrow(start_node, end_node):
        x1, y1 = nodes[start_node]['center']
        x2, y2 = nodes[end_node]['center']
        
        if abs(x2 - x1) > abs(y2 - y1):
            # Mainly right/left
            start_x = x1 + (box_w/2 + 0.1) * (1 if x2 > x1 else -1)
            end_x = x2 - (box_w/2 + 0.1) * (1 if x2 > x1 else -1)
            start_y, end_y = y1, y2
        else:
            # Mainly up/down
            start_x, end_x = x1, x2
            start_y = y1 + (box_h/2 + 0.1) * (1 if y2 > y1 else -1)
            end_y = y2 - (box_h/2 + 0.1) * (1 if y2 > y1 else -1)
            
        ax.annotate(
            "",
            xy=(end_x, end_y), xycoords='data',
            xytext=(start_x, start_y), textcoords='data',
            arrowprops=dict(arrowstyle="->", lw=2.5, color='#4b5563'),
            zorder=1
        )

    # Draw the connection lines
    for start, end in edges:
        draw_arrow(start, end)
        
    # Draw a bounding dashed box around the "Offline Runtime Scope"
    ax.add_patch(patches.Rectangle((4.5, 2.5), 13.2, 7.5, linewidth=2, linestyle='--', edgecolor='red', fill=False, zorder=0))
    ax.text(4.7, 2.8, "Offline Runtime Scope (Local Hardware)", fontsize=13, fontweight='bold', color='red')

    # Add descriptive title
    plt.text(9, 10.7, "AgriBot: System Architecture Diagram", fontsize=20, fontweight='bold', color='#111827', ha='center', va='bottom')
    plt.tight_layout()
    
    # Save diagram
    plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    draw_architecture_diagram()
