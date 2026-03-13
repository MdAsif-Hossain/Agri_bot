import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_subscription_workflow():
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.axis('off')
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6)
    
    # Define styling
    box_w = 2.5
    box_h = 1.2
    
    # Colors
    coop_color = '#dbeafe'     # Blue
    setup_color = '#fef3c7'    # Yellow
    update_color = '#f3e8ff'   # Purple
    farmer_color = '#d1fae5'   # Green
    border_color = '#374151'
    text_color = '#111827'
    
    # Define steps
    steps = [
        {
            'title': '1. Seasonal Fee',
            'desc': 'Cooperative or NGO pays\nseasonal subscription fee',
            'pos': (1, 4),
            'color': coop_color
        },
        {
            'title': '2. Kiosk Setup',
            'desc': 'AgriBot hardware & Local\nAI Kiosk is deployed',
            'pos': (4.5, 4),
            'color': setup_color
        },
        {
            'title': '3. Offline Sync',
            'desc': 'Regular offline DB syncing\n& model patching via USB/LAN',
            'pos': (8, 4),
            'color': update_color
        },
        {
            'title': '4. Daily Usage',
            'desc': 'Farmers access voice/vision\nRAG daily without internet',
            'pos': (11.5, 4),
            'color': farmer_color
        }
    ]
    
    # Draw boxes
    box_centers = []
    for step in steps:
        x, y = step['pos']
        
        # Center coordinates for arrows later
        box_centers.append((x + box_w/2, y + box_h/2))
        
        # Draw box with rounded corners
        rect = patches.FancyBboxPatch(
            (x, y), box_w, box_h, 
            boxstyle="round,pad=0.1,rounding_size=0.2", 
            linewidth=2, edgecolor=border_color, 
            facecolor=step['color'], zorder=2
        )
        ax.add_patch(rect)
        
        # Title text
        ax.text(x + box_w/2, y + box_h - 0.3, step['title'], 
                ha='center', va='center', fontsize=12, fontweight='bold', color=text_color, zorder=3)
        
        # Description text
        ax.text(x + box_w/2, y + 0.5, step['desc'], 
                ha='center', va='center', fontsize=10, color=text_color, zorder=3)

    # Draw arrows connecting the boxes
    for i in range(len(box_centers) - 1):
        x1, y1 = box_centers[i]
        x2, y2 = box_centers[i+1]
        
        # Adjust start and end points so arrow doesn't overlap the box perfectly
        start_x = x1 + box_w/2 + 0.1
        end_x = x2 - box_w/2 - 0.2
        
        ax.annotate(
            "",
            xy=(end_x, y1), xycoords='data',
            xytext=(start_x, y1), textcoords='data',
            arrowprops=dict(arrowstyle="->", lw=3, color='#4b5563'),
            zorder=1
        )
    
    # Diagram Title
    plt.title("AgriBot: Subscription Business Model Workflow", fontsize=18, fontweight='bold', color='#1f2937', pad=20)
    
    # Save the diagram
    plt.savefig('subscription_workflow.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    draw_subscription_workflow()
