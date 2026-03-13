import matplotlib.pyplot as plt
import numpy as np

def draw_vram_chart():
    print("Generating VRAM Utilization Line Chart...")
    
    # Modern professional colors
    line_color = '#2563eb'     # Blue 600
    fill_color = '#eff6ff'     # Blue 50
    text_dark = '#0f172a'      # Slate 900
    grid_color = '#e2e8f0'     # Slate 200
    accent_red = '#dc2626'     # Red 600
    
    # Define timeline phases and VRAM usage (in GB)
    # This is a representative curve of a typical offline multimodal RAG execution
    phases = [
        ('Idle', 0.8),                  # Baseline OS/FastAPI footprint
        ('ASR (Whisper)', 1.5),         # Whisper transcription spikes memory slightly
        ('KG Traverse', 1.6),           # SQLite query (CPU/RAM bound, VRAM stable)
        ('Embedding', 2.3),             # FAISS indexing/querying spikes VRAM
        ('Reranking', 2.8),             # Cross-encoder pulls substantial VRAM
        ('LLM Generate (Qwen)', 3.6),   # llama.cpp generation hits peak VRAM (capped under 4GB)
        ('Cleanup / Verify', 1.4),      # Model unloads/swaps, memory drops
        ('Idle', 0.8)
    ]
    
    x_labels = [p[0] for p in phases]
    y_values = [p[1] for p in phases]
    
    # Create smooth curve for continuous time representation
    x_ticks = np.arange(len(phases))
    x_smooth = np.linspace(0, len(phases) - 1, 300)
    y_smooth = np.interp(x_smooth, x_ticks, y_values)
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
    
    # Draw graph
    ax.plot(x_smooth, y_smooth, color=line_color, linewidth=4, zorder=3)
    ax.fill_between(x_smooth, y_smooth, 0, color=fill_color, alpha=0.8, zorder=2)
    
    # Add scatter points at major phase shifts
    ax.scatter(x_ticks, y_values, color=line_color, s=120, edgecolor='white', linewidth=2, zorder=4)
    
    # Annotate Peak Usage
    peak_idx = 5  # LLM Generate
    ax.annotate(f'Peak: {y_values[peak_idx]} GB', 
                xy=(peak_idx, y_values[peak_idx]), 
                xytext=(peak_idx - 0.5, y_values[peak_idx] + 0.5),
                arrowprops=dict(facecolor=accent_red, edgecolor=accent_red, arrowstyle='->', lw=2),
                fontsize=12, fontweight='bold', color=accent_red, zorder=5)

    # Styling Axes
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=11, fontweight='bold', color=text_dark)
    
    ax.set_ylim(0, 8)
    ax.set_ylabel('VRAM Utilization (GB)', fontsize=13, fontweight='bold', color=text_dark, labelpad=15)
    ax.set_xlabel('Query Pipeline Phases', fontsize=13, fontweight='bold', color=text_dark, labelpad=15)
    
    ax.grid(axis='y', linestyle='--', color=grid_color, alpha=0.7, zorder=1)
    ax.grid(axis='x', linestyle=':', color=grid_color, alpha=0.5, zorder=1)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['bottom'].set_color('#94a3b8')

    # Add Title
    plt.title('VRAM Utilization Over Time (Multimodal RAG Pipeline)', 
              fontsize=16, fontweight='bold', color=text_dark, pad=20)
              
    plt.figtext(0.5, -0.15, "Figure 6.5: Hardware resource utilization during a complete offline voice query execution lifecycle.", 
               ha='center', fontsize=12, fontstyle='italic', color='#475569')

    # Save Graph
    plt.tight_layout()
    filename = 'vram_utilization_chart.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Successfully generated '{filename}'")
    
    # Auto-download if in Google Colab
    try:
        from google.colab import files
        print(f"Triggering download of {filename}...")
        files.download(filename)
    except ImportError:
        print(f"File saved to current directory: {filename}")

if __name__ == "__main__":
    draw_vram_chart()
