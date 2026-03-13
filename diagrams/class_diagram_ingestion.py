import graphviz
from IPython.display import display

def create_class_diagram():
    print("Generating Professional UML Class Diagram...")
    
    # Initialize the Digraph
    dot = graphviz.Digraph('Class_Diagram', 
                           filename='class_diagram_ingestion',
                           format='png',
                           node_attr={'shape': 'none', 'fontname': 'Helvetica'})
    
    # Graph settings for Top-to-Bottom layout, orthogonal edges
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.6', ranksep='1.2')
    
    # Helper to build HTML-like tables for UML classes
    def build_class_html(class_name, attributes, methods):
        
        attr_rows = ""
        if attributes:
            for attr in attributes:
                attr_rows += f'<TR><TD ALIGN="LEFT" BGCOLOR="#f8fafc"><FONT COLOR="#334155" POINT-SIZE="11">{attr}</FONT></TD></TR>\n'
        else:
            attr_rows = '<TR><TD ALIGN="LEFT" BGCOLOR="#f8fafc"><FONT COLOR="#334155" POINT-SIZE="11"> </FONT></TD></TR>\n'
            
        meth_rows = ""
        if methods:
            for meth in methods:
                meth_rows += f'<TR><TD ALIGN="LEFT" BGCOLOR="#ffffff"><FONT COLOR="#0f172a" POINT-SIZE="11">{meth}</FONT></TD></TR>\n'
        else:
            meth_rows = '<TR><TD ALIGN="LEFT" BGCOLOR="#ffffff"><FONT COLOR="#0f172a" POINT-SIZE="11"> </FONT></TD></TR>\n'
            
        return f'''<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
          <TR>
            <TD ALIGN="CENTER" BGCOLOR="#1e3a8a"><FONT COLOR="white"><B>{class_name}</B></FONT></TD>
          </TR>
          {attr_rows}
          {meth_rows}
        </TABLE>>'''

    # Define Class Nodes
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

    # Optional Title
    dot.attr(label='\nFigure 6.4: Class Diagram representing the Multimodal Document Ingestion Pipeline.',
             labelloc='b', labeljust='c', fontsize='15', fontname='Helvetica-Bold', fontcolor='#0f172a')

    # Edges - Composition relationships (PDFIngestor is composed of the other classes)
    # Using dir='back' and arrowtail='diamond' for strict composition (filled black diamond)
    edge_attrs = {'dir': 'back', 'arrowtail': 'diamond', 'color': '#64748b', 'penwidth': '2.0'}
    
    # Aligning the children roughly on the same rank (invisible edges or subgraph if necessary,
    # but splines='ortho' will handle it dynamically)
    
    # We want PDFIngestor at the top.
    with dot.subgraph() as s:
        s.attr(rank='same')
        s.node('MarkerExtractor')
        s.node('TextChunker')
        s.node('FAISSIndexer')
        s.node('BM25Indexer')

    dot.edge('PDFIngestor', 'MarkerExtractor', **edge_attrs)
    dot.edge('PDFIngestor', 'TextChunker', **edge_attrs)
    dot.edge('PDFIngestor', 'FAISSIndexer', **edge_attrs)
    dot.edge('PDFIngestor', 'BM25Indexer', **edge_attrs)

    # Render logic
    dot.render(cleanup=True)
    
    # Try to render it inline if running in a Jupyter/Colab environment
    try:
        display(dot)
        print("Success! Downlaod 'class_diagram_ingestion.png' from the Colab file browser.")
    except Exception as e:
        print("Successfully generated 'class_diagram_ingestion.png' on disk.")

if __name__ == '__main__':
    create_class_diagram()
