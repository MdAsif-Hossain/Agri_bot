import graphviz

def create_class_diagram():
    print("Generating Professional UML Class Diagram...")
    
    # Initialize the Digraph with high-res output settings
    dot = graphviz.Digraph('Class_Diagram', 
                           filename='class_diagram_ingestion',
                           format='png')
    
    # Graph settings for Top-to-Bottom layout, orthogonal edges, and clean spacing
    dot.attr(rankdir='TB', 
             splines='ortho', 
             nodesep='0.8', 
             ranksep='1.2', 
             pad='0.5',
             dpi='300') # High resolution for academic reports
    
    # Helper to build beautifully formatted HTML-like tables for UML classes
    def build_class_html(class_name, attributes, methods):
        # FIX: Ensure proper <BR ALIGN='LEFT'/> formatting for Graphviz
        attr_html = "".join([f"{attr}<BR ALIGN='LEFT'/>" for attr in attributes]) if attributes else " "
        meth_html = "".join([f"{meth}<BR ALIGN='LEFT'/>" for meth in methods]) if methods else " "
        
        # FIX: The string MUST start with exactly <<TABLE to be parsed as HTML by Graphviz.
        # Added BALIGN="LEFT" to ensure the text blocks strictly align to the left edge.
        return f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="10" COLOR="#cbd5e1">
          <TR>
            <TD BGCOLOR="#1e3a8a" ALIGN="CENTER">
              <FONT COLOR="white" FACE="Helvetica-Bold" POINT-SIZE="14">{class_name}</FONT>
            </TD>
          </TR>
          <TR>
            <TD BGCOLOR="#f8fafc" ALIGN="LEFT" BALIGN="LEFT">
              <FONT COLOR="#334155" FACE="Courier" POINT-SIZE="11">{attr_html}</FONT>
            </TD>
          </TR>
          <TR>
            <TD BGCOLOR="#ffffff" ALIGN="LEFT" BALIGN="LEFT">
              <FONT COLOR="#0f172a" FACE="Courier" POINT-SIZE="11">{meth_html}</FONT>
            </TD>
          </TR>
        </TABLE>>'''

    # --- Define Class Nodes ---
    dot.node('PDFIngestor', build_class_html(
        class_name='PDFIngestor',
        attributes=[
            '- data_dir: str',
            '- marker_extractor: MarkerExtractor',
            '- text_chunker: TextChunker',
            '- faiss_idx: FAISSIndexer',
            '- bm25_idx: BM25Indexer'
        ],
        methods=[
            '+ run_pipeline(directory: str)',
            '+ process_document(file_path: str)',
            '- save_artifacts(output_dir: str)'
        ]
    ))

    dot.node('MarkerExtractor', build_class_html(
        class_name='MarkerExtractor',
        attributes=[
            '- use_ocr: bool',
            '- preserve_layout: bool'
        ],
        methods=[
            '+ extract_pdf(pdf_path: str): Document',
            '- parse_tables(page: Page)',
            '- process_images(page: Page)'
        ]
    ))

    dot.node('TextChunker', build_class_html(
        class_name='TextChunker',
        attributes=[
            '- chunk_size: int = 512',
            '- chunk_overlap: int = 64'
        ],
        methods=[
            '+ split_documents(docs: List[Document]): List[Chunk]',
            '- recursive_split(text: str): List[str]'
        ]
    ))

    dot.node('FAISSIndexer', build_class_html(
        class_name='FAISSIndexer',
        attributes=[
            '- embedding_model: SentenceTransformer',
            '- index: faiss.IndexFlatIP',
            '- dimension: int'
        ],
        methods=[
            '+ encode_and_add(chunks: List[Chunk])',
            '+ save_index(path: str)'
        ]
    ))

    dot.node('BM25Indexer', build_class_html(
        class_name='BM25Indexer',
        attributes=[
            '- tokenized_corpus: List[List[str]]',
            '- bm25: BM25Okapi'
        ],
        methods=[
            '+ fit(chunks: List[Chunk])',
            '+ save_index(path: str)'
        ]
    ))

    # Overall Caption/Title
    dot.attr(label='Figure 6.4: Class Diagram representing the Multimodal Document Ingestion Pipeline.',
             labelloc='b', labeljust='c', fontsize='14', fontname='Helvetica-Oblique', fontcolor='#475569')

    # --- Define Edges (Composition Relationships) ---
    # PDFIngestor is composed of the other classes. 
    # dir='back' and arrowtail='diamond' creates the standard UML filled composition diamond.
    edge_attrs = {
        'dir': 'back', 
        'arrowtail': 'diamond', 
        'color': '#475569', 
        'penwidth': '1.5'
    }
    
    # Force the children classes to align on the same horizontal level
    with dot.subgraph() as s:
        s.attr(rank='same')
        s.node('MarkerExtractor')
        s.node('TextChunker')
        s.node('FAISSIndexer')
        s.node('BM25Indexer')

    # Draw the composition arrows from PDFIngestor to its components
    dot.edge('PDFIngestor', 'MarkerExtractor', **edge_attrs)
    dot.edge('PDFIngestor', 'TextChunker', **edge_attrs)
    dot.edge('PDFIngestor', 'FAISSIndexer', **edge_attrs)
    dot.edge('PDFIngestor', 'BM25Indexer', **edge_attrs)

    # Render the graph
    try:
        dot.render(cleanup=True)
        print("Successfully generated 'class_diagram_ingestion.png' on disk.")
        
        # Try to display inline if running in a Jupyter/Colab notebook
        try:
            from IPython.display import display, Image
            display(Image('class_diagram_ingestion.png'))
            print("Note: Download 'class_diagram_ingestion.png' from your file browser to use in your report.")
        except ImportError:
            pass # Not in a notebook environment
            
    except Exception as e:
        print(f"\\n[ERROR] Graphviz rendering failed.\\nEnsure the Graphviz system binaries are installed (e.g., 'sudo apt install graphviz' or 'brew install graphviz').\\nDetails: {e}")

if __name__ == '__main__':
    create_class_diagram()
