import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_sequence_diagram():
    print("Generating Academic Sequence Diagram...")
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    ax.axis('off')
    
    # Coordinates
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 24)
    
    # Colors
    header_bg = '#1e3a8a'     # Deep blue
    text_dark = '#0f172a'
    line_gray = '#94a3b8'
    alt_bg = '#f8fafc'
    alt_border = '#cbd5e1'
    fail_color = '#b91c1c'
    pass_color = '#047857'
    self_loop = '#2563eb'
    
    # Lifelines X coordinates
    entities = [
        ("User\n(Client/UI)", 1.5),
        ("FastAPI\n(api.py)", 4.5),
        ("Query\nExpansion (KG)", 7.5),
        ("Hybrid\nRetrieval", 10.5),
        ("Evidence\nGrader", 13.5),
        ("Generate &\nVerify", 16.5)
    ]
    
    # Draw Headers and Lifeline dashed lines
    for name, x in entities:
        # Box
        rect = patches.Rectangle((x-1.3, 22), 2.6, 1.4, facecolor=header_bg, edgecolor='white', lw=2)
        ax.add_patch(rect)
        ax.text(x, 22.7, name, color='white', ha='center', va='center', fontweight='bold', fontsize=11)
        
        # Lifeline (vertical dashed)
        ax.plot([x, x], [22, 1], linestyle='--', color=line_gray, zorder=0, lw=1.5)

    # Helper function for regular messages
    def draw_msg(y, start_idx, end_idx, text, color=text_dark, ls='-'):
        x_start = entities[start_idx][1]
        x_end = entities[end_idx][1]
        
        # Arrow
        ax.annotate("", xy=(x_end, y), xytext=(x_start, y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2.5, linestyle=ls))
        
        # Text mapping
        mid_x = (x_start + x_end) / 2
        ax.text(mid_x, y + 0.15, text, ha='center', va='bottom', fontsize=10, 
                color=color, fontweight='bold', bbox=dict(facecolor='white', edgecolor='none', alpha=0.9, pad=1))
        
    # Helper for self-execution loops
    def draw_self(y, idx, text, color=self_loop):
        x = entities[idx][1]
        
        # Arc
        ax.annotate("", xy=(x, y-0.9), xytext=(x, y),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.8", color=color, lw=2))
        
        # Text Box
        ax.text(x + 0.5, y - 0.45, text, ha='left', va='center', fontsize=9, 
                color=color, style='italic', bbox=dict(facecolor='#f1f5f9', edgecolor=color, boxstyle='round,pad=0.3', alpha=0.9))

    # Y timeline execution
    y = 21
    draw_msg(y, 0, 1, "1. POST /v1/chat API")
    
    y -= 1.5
    draw_msg(y, 1, 2, "2. LangGraph Query Dispatch")
    
    y -= 1.5
    draw_self(y, 2, "Traverse SQLite:\nAlias -> Canonical", color=self_loop)
    
    y -= 1.8
    draw_msg(y, 2, 3, "3. Synthesized Expanded Query")
    
    y -= 1.5
    draw_self(y, 3, "Compute Vectors:\nFAISS + BM25 + Rerank", color=self_loop)
    
    y -= 1.8
    draw_msg(y, 3, 4, "4. Retrieved Doc Chunks", color=text_dark)
    
    y -= 1.0
    
    # ---------------- ALTERNATIVE / LOOP FRAME ---------------- #
    frame_y_top = y + 0.5
    frame_h = 9.5
    
    # Main Box
    rect = patches.Rectangle((6, frame_y_top - frame_h), 11.5, frame_h, 
                             facecolor=alt_bg, edgecolor=alt_border, linestyle='-', linewidth=2, zorder=0)
    ax.add_patch(rect)
    
    # Tab Label
    tab_w = 2.5
    tab_h = 0.8
    tab = patches.Rectangle((6, frame_y_top - tab_h), tab_w, tab_h, 
                            facecolor='#e2e8f0', edgecolor=alt_border, zorder=0)
    ax.add_patch(tab)
    ax.text(6 + tab_w/2, frame_y_top - tab_h/2, "ALT / LOOP", ha='center', va='center', fontsize=10, fontweight='bold')
    
    # --- IF FAIL ---
    y -= 0.5
    ax.text(6.5, y, "[ If Evidence Grader = Fail ]", color=fail_color, fontweight='bold', fontsize=11)
    
    y -= 1.5
    draw_self(y, 4, "Evaluate: No Relevance\nto User Query", color=fail_color)
    
    y -= 1.8
    draw_msg(y, 4, 3, "5a. Query Rewrite Node", color=fail_color)
    
    y -= 1.2
    draw_msg(y, 3, 2, "Loop Execution", ls='--', color=fail_color)
    
    # Divider Line
    y -= 0.8
    ax.plot([6, 17.5], [y, y], linestyle=':', color=alt_border, lw=2)
    
    # --- IF PASS ---
    y -= 0.8
    ax.text(6.5, y, "[ If Evidence Grader = Pass ]", color=pass_color, fontweight='bold', fontsize=11)
    
    y -= 1.2
    draw_self(y, 4, "Evaluate: Strong\nEvidence Match", color=pass_color)
    
    y -= 1.8
    draw_msg(y, 4, 5, "5b. Pass Chunks to Gen Node", color=pass_color)
    
    y -= 1.6
    draw_self(y, 5, "LLM Synthesize &\nStrict Verify citations", color=self_loop)
    y -= 1.2
    # -------------------------------------------------------- #
    
    y -= 1.5
    draw_msg(y, 5, 1, "6. Verified Output JSON", ls='--', color=text_dark)
    
    y -= 1.5
    draw_msg(y, 1, 0, "7. Render UI & TTS Voice", ls='--', color=text_dark)

    # Overall Title
    plt.text(9, 23.5, "Figure 6.3: Sequence Diagram of the LangGraph Bounded Self-Correction Loop", 
             fontsize=16, fontweight='bold', color='#0f172a', ha='center', va='center')
    
    plt.tight_layout()
    plt.savefig('sequence_diagram_agribot.png', dpi=300, bbox_inches='tight', transparent=False, facecolor='white')
    print("Successfully generated 'sequence_diagram_agribot.png'")

if __name__ == "__main__":
    draw_sequence_diagram()
