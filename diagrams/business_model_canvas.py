import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap

def create_business_model_canvas():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.axis('off')
    
    # Define box colors and styling
    box_color = '#ecfdf5' # Light emerald
    edge_color = '#059669' # Darker emerald for borders
    title_color = '#064e3b'

    # Box coordinates (x, y, width, height)
    boxes = {
        'Key Partners': (0, 0.4, 0.2, 0.6),
        'Key Activities': (0.2, 0.7, 0.2, 0.3),
        'Key Resources': (0.2, 0.4, 0.2, 0.3),
        'Value Proposition': (0.4, 0.4, 0.2, 0.6),
        'Customer Relationships': (0.6, 0.7, 0.2, 0.3),
        'Channels': (0.6, 0.4, 0.2, 0.3),
        'Customer Segments': (0.8, 0.4, 0.2, 0.6),
        'Cost Structure': (0, 0, 0.5, 0.4),
        'Revenue Streams': (0.5, 0, 0.5, 0.4)
    }

    # Content for the canvas
    content = {
        'Key Partners': "• NGOs and Local Charites\n• Ministry of Agriculture\n• Local Extension Offices\n• Agricultural Research Institutes\n• Local Hardware Vendors",
        'Key Activities': "• Model fine-tuning & NLP translation\n• Software updates & patching\n• Periodic offline database syncing\n• Knowledge Graph expansion",
        'Key Resources': "• Local Edge Hardware (Kiosks/GPUs)\n• Pre-trained Foundation Models\n• Curated Agricultural PDF Database\n• Software Engineers & Agronomists",
        'Value Proposition': "• 100% Offline, verifiable agricultural advice\n• Native dialect voice recognition (Bengali)\n• Multimodal (Voice, Image, Text) diagnosis\n• Data privacy & zero cloud dependency",
        'Customer Relationships': "• Automated self-serve kiosks\n• Human-assisted extension support\n• Transparent, citation-backed trust\n• Community-driven feedback loop",
        'Channels': "• Deployed Kiosk / Desktop applications\n• Mobile Native Thin Client (LAN/WiFi)\n• Field Officer demonstrations",
        'Customer Segments': "• Rural Farmers (Low literacy)\n• Agricultural Extension Officers\n• NGO Field Workers\n• Researchers and Policy Makers",
        'Cost Structure': "• Initial Edge Hardware deployment (Capital Exp.)\n• Development & Maintenance costs\n• Evaluation and model training compute\n• Field-worker training & onboarding",
        'Revenue Streams': "• Government & NGO Grants\n• B2B licensing for distinct crop sectors\n• Analytics dashboards for state-level monitoring\n• CSR (Corporate Social Responsibility) funding"
    }

    # Draw the boxes and text
    for title, (x, y, w, h) in boxes.items():
        # Draw rectangle
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor=edge_color, facecolor=box_color, zorder=1)
        ax.add_patch(rect)
        
        # Add Title
        ax.text(x + 0.01, y + h - 0.02, title, fontsize=13, fontweight='bold', color=title_color, verticalalignment='top', zorder=2)
        
        # Calculate character wrap width roughly based on box width
        # A width of 0.2 units mapped to 16in fig roughly equals 30-35 characters depending on font size
        char_width = int(w * 170)
        
        # Process Content: wrap each bullet point separately
        bullets = content[title].split('\n')
        wrapped_bullets = []
        for bullet in bullets:
            # Wrap the bullet but keep the bullet point indent
            wrapped = textwrap.fill(bullet, width=char_width, subsequent_indent='  ')
            wrapped_bullets.append(wrapped)
            
        final_text = '\n'.join(wrapped_bullets)
        
        # Add Content
        text_y = y + h - 0.07
        ax.text(x + 0.01, text_y, final_text, fontsize=10, color='#1f2937', verticalalignment='top', zorder=2, linespacing=1.4)

    # Adding a main title
    plt.suptitle("AgriBot: Business Model Canvas", fontsize=22, fontweight='bold', color='#065f46')
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    # Save the diagram
    plt.savefig('business_model_canvas.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    create_business_model_canvas()
