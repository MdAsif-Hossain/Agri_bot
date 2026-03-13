import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_sequence_diagram():
    print("Generating Professional Sequence Diagram...")
    # Set up the figure with high resolution
    fig, ax = plt.subplots(figsize=(16, 13), dpi=300)
    ax.axis('off')
    
    # Canvas Coordinates
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 26)
    
    # Professional Color Palette
    header_bg = '#1e3a8a'     # Deep Academic Blue
    text_dark = '#0f172a'     # Slate 900
    line_gray = '#94a3b8'     # Slate 400
    alt_bg = '#f8fafc'        # Slate 50
    alt_border = '#cbd5e1'    # Slate 300
    fail_color = '#dc2626'    # Red 600
    pass_color = '#059669'    # Emerald 600
    self_loop = '#2563eb'     # Blue 600
    
    # Lifelines and X coordinates
    entities = [
        ("User\n(Client/UI)", 1.5),
        ("FastAPI\n(Orchestrator)", 4.5),
        ("Query\nExpansion (KG)", 7.5),
        ("Hybrid\nRetrieval", 10.5),
        ("Evidence\nGrader", 13.5),
        ("Generate &\nVerify", 16.5)
    ]
    
    # 1. Draw Headers and Lifelines
    for name, x in entities:
        # Draw dashed lifeline
        ax.plot([x, x], [24, 1], linestyle='--', color=line_gray, zorder=1, lw=1.5)
        
        # Draw rounded header box
        box = patches.FancyBboxPatch((x-1.3, 23.5), 2.6, 1.2, 
                                     boxstyle="round,pad=0.1,rounding_size=0.2", 
                                     facecolor=header_bg, edgecolor='none', zorder=2)
        ax.add_patch(box)
        
        # Header Text
        ax.text(x, 24.1, name, color='white', ha='center', va='center', fontweight='bold', fontsize=11, zorder=3)

    # Helper: Standard Messages
    def draw_msg(y, start_idx, end_idx, text, color=text_dark, ls='-'):
        x_start = entities[start_idx][1]
        x_end = entities[end_idx][1]
        
        # Solid filled arrow for sequence flows
        ax.annotate("", xy=(x_end, y), xytext=(x_start, y),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2, linestyle=ls, mutation_scale=15), zorder=2)
        
        # Floating text label with white background
        mid_x = (x_start + x_end) / 2
        ax.text(mid_x, y + 0.2, text, ha='center', va='bottom', fontsize=10, 
                color=color, fontweight='bold', 
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='none', alpha=0.9), zorder=3)

    # Helper: Self-Execution Loops (Orthogonal)
    def draw_self(y, idx, text, color=self_loop):
        x = entities[idx][1]
        drop = 0.8
        
        # Draw 3 right-angled line segments
        ax.plot([x, x+1.1, x+1.1, x], [y, y, y-drop, y-drop], color=color, lw=2, zorder=2)
        
        # Arrowhead pointing back to lifeline
        ax.annotate("", xy=(x, y-drop), xytext=(x+0.1, y-drop),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2, mutation_scale=15), zorder=2)
        
        # Action Text
        ax.text(x + 1.3, y - (drop/2), text, ha='left', va='center', fontsize=9.5, 
                color=text_dark, fontstyle='italic', 
                bbox=dict(facecolor='white', edgecolor=color, boxstyle='round,pad=0.3', lw=1.5), zorder=3)
        return drop

    # --- EXECUTION TIMELINE ---
    y = 22.5
    draw_msg(y, 0, 1, "1. POST /v1/chat API")
    
    y -= 1.6
    draw_msg(y, 1, 2, "2. LangGraph Query Dispatch")
    
    y -= 1.2
    drop = draw_self(y, 2, "Traverse SQLite:\nAlias -> Canonical", color=self_loop)
    
    y -= (drop + 1.2)
    draw_msg(y, 2, 3, "3. Synthesized Expanded Query")
    
    y -= 1.2
    drop = draw_self(y, 3, "Compute Vectors:\nFAISS + BM25 + Rerank", color=self_loop)
    
    y -= (drop + 1.2)
    draw_msg(y, 3, 4, "4. Retrieved Doc Chunks", color=text_dark)
    
    # ---------------- ALTERNATIVE / LOOP UML FRAME ---------------- #
    y -= 1.0
    frame_y_top = y
    frame_h = 11.5
    frame_x_start = 6.0
    frame_x_end = 17.5
    
    # Frame Background
    rect = patches.Rectangle((frame_x_start, frame_y_top - frame_h), 
                             frame_x_end - frame_x_start, frame_h, 
                             facecolor=alt_bg, edgecolor=alt_border, linewidth=2, zorder=0)
    ax.add_patch(rect)
    
    # UML Alt Tab
    tab_w = 2.5
    tab_h = 0.8
    tab = patches.Rectangle((frame_x_start, frame_y_top - tab_h), tab_w, tab_h, 
                            facecolor='#e2e8f0', edgecolor=alt_border, linewidth=2, zorder=1)
    ax.add_patch(tab)
    ax.text(frame_x_start + tab_w/2, frame_y_top - tab_h/2, "ALT / LOOP", 
            ha='center', va='center', fontsize=10, fontweight='bold', color=text_dark)
    
    # --- IF FAIL BLOCK ---
    y -= 1.5
    ax.text(frame_x_start + 0.3, y + 0.4, "[ Condition: Evidence Grader = Fail ]", 
            color=fail_color, fontweight='bold', fontsize=10.5)
    
    drop = draw_self(y, 4, "Evaluate: No Relevance\nto User Query", color=fail_color)
    
    y -= (drop + 1.4)
    draw_msg(y, 4, 3, "5a. Query Rewrite Node", color=fail_color)
    
    y -= 1.2
    # HERE IS THE FIX: Routing from Retrieval (3) forward to Grader (4) instead of parsing back to KG
    draw_msg(y, 3, 4, "Trigger Retrieval Loop & Retry Grade", ls='--', color=fail_color)
    
    # --- DIVIDER ---
    y -= 1.2
    ax.plot([frame_x_start, frame_x_end], [y, y], linestyle='--', color=alt_border, lw=2, zorder=1)
    
    # --- IF PASS BLOCK ---
    y -= 1.5
    ax.text(frame_x_start + 0.3, y + 0.4, "[ Condition: Evidence Grader = Pass ]", 
            color=pass_color, fontweight='bold', fontsize=10.5)
    
    drop = draw_self(y, 4, "Evaluate: Strong\nEvidence Match", color=pass_color)
    
    y -= (drop + 1.4)
    draw_msg(y, 4, 5, "5b. Pass Chunks to Gen Node", color=pass_color)
    
    y -= 1.2
    drop = draw_self(y, 5, "LLM Synthesize &\nStrict Verify Citations", color=self_loop)
    
    y -= (drop + 1.5)
    # ---------------- END FRAME ---------------- #
    
    # Return Messages (Dashed)
    draw_msg(y, 5, 1, "6. Verified Output JSON", ls='--', color=text_dark)
    
    y -= 1.8
    draw_msg(y, 1, 0, "7. Render UI & TTS Voice", ls='--', color=text_dark)

    # Overall Titles
    plt.text(9, 25.5, "Sequence Diagram: LangGraph Bounded Self-Correction Loop", 
             fontsize=18, fontweight='bold', color=text_dark, ha='center', va='center')
    
    
    # Save and Show
    plt.tight_layout()
    plt.savefig('sequence_diagram_agribot_professional.png', dpi=300, bbox_inches='tight', transparent=False, facecolor='white')
    print("Successfully generated 'sequence_diagram_agribot_professional.png'")

if __name__ == "__main__":
    draw_sequence_diagram()
