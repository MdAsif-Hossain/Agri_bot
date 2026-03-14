import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_er_diagram():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')
    
    # Define Canvas Dimensions
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    
    # Styling Variables
    box_w = 3.5
    box_h = 2.0
    
    header_color = '#3b82f6'  # Darker Blue for Headers
    edge_color = '#1e3a8a'
    text_color = '#1f2937'
    
    # Table Definitions
    tables = {
        'Canonical_Term': {
            'pos': (1.5, 7), 
            'attributes': ['* ID (PK)', 'Scientific_Name', 'Category (Crop/Pest/Disease)']
        },
        'Alias': {
            'pos': (9, 7), 
            'attributes': ['* ID (PK)', 'Canonical_ID (FK)', 'Dialect_Name', 'Language (BN/EN)']
        },
        'Relationships': {
            'pos': (1.5, 2.5), 
            'attributes': ['* ID (PK)', 'Source_ID (FK)', 'Target_ID (FK)', 'Relation_Type (e.g., TREATS)']
        },
        'Document_Provenance': {
            'pos': (9, 2.5), 
            'attributes': ['* ID (PK)', 'Relation_ID (FK)', 'Doc_ID (PDF Name)', 'Page_Number']
        }
    }

    # Draw ER Tables
    for name, data in tables.items():
        x, y = data['pos']
        data['center'] = (x + box_w/2, y + box_h/2)
        
        # Draw Main Box (Body)
        rect = patches.Rectangle((x, y), box_w, box_h, linewidth=2, edgecolor=edge_color, facecolor='white', zorder=2)
        ax.add_patch(rect)
        
        # Draw Header Box
        header_h = 0.5
        header_y = y + box_h - header_h
        header_rect = patches.Rectangle((x, header_y), box_w, header_h, linewidth=2, edgecolor=edge_color, facecolor=header_color, zorder=2)
        ax.add_patch(header_rect)
        
        # Table Name (Header Text)
        ax.text(x + box_w/2, header_y + header_h/2, name, ha='center', va='center', fontsize=12, fontweight='bold', color='white', zorder=3)
        
        # Attributes Text
        attr_y = header_y - 0.3
        for attr in data['attributes']:
            fw = 'bold' if '(PK)' in attr or '(FK)' in attr else 'normal'
            ax.text(x + 0.2, attr_y, attr, ha='left', va='center', fontsize=10, fontweight=fw, color=text_color, zorder=3)
            attr_y -= 0.35

    # Draw Relation Lines (Crow's Foot loosely styled)
    def draw_line(start_node, end_node, label="", style="<->"):
        x1, y1 = tables[start_node]['center']
        x2, y2 = tables[end_node]['center']
        
        # Offsets
        if x2 > x1:  # Horizontal line
            start_x, end_x = x1 + box_w/2, x2 - box_w/2
            start_y, end_y = y1, y2
        else:  # Vertical line
            start_x, end_x = x1, x2
            start_y, end_y = y1 - box_h/2, y2 + box_h/2
            
        ax.annotate(
            label,
            xy=(end_x, end_y), xycoords='data',
            xytext=(start_x, start_y), textcoords='data',
            arrowprops=dict(arrowstyle=style, lw=2, color=edge_color),
            ha='center', va='bottom', fontsize=10, fontweight='bold', color='#dc2626', zorder=1
        )

    # Define Relationships (1 to Many / Foreign Keys)
    # Canonical_Term (1) -> (N) Alias
    draw_line('Canonical_Term', 'Alias', label="1 : N", style="<-")
    
    # Canonical_Term (1) -> (N) Relationships (Source)
    draw_line('Canonical_Term', 'Relationships', label="1 : N", style="<-")
    
    # Relationships (1) -> (N) Document_Provenance
    draw_line('Relationships', 'Document_Provenance', label="1 : N", style="<-")

    # Titles
    plt.text(7, 9.6, "Figure 6.2: Entity-Relationship Diagram of the Dialect Knowledge Graph", fontsize=15, fontweight='bold', color='#111827', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('er_diagram_kg.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    draw_er_diagram()
