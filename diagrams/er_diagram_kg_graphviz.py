import graphviz
from IPython.display import display

def create_professional_er_diagram():
    print("Generating Professional ER Diagram...")
    
    # Initialize the Digraph
    dot = graphviz.Digraph('ER_Diagram', 
                           filename='agribot_er_diagram',
                           format='png',
                           node_attr={'shape': 'none', 'fontname': 'Helvetica'})
    
    # Graph settings for Left-to-Right layout, orthogonal edges for DB look
    dot.attr(rankdir='LR', splines='ortho', nodesep='0.8', ranksep='1.5')
    
    # Define Canonical_Term table with HTML-like label
    dot.node('Canonical_Term', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
      <TR>
        <TD COLSPAN="2" BGCOLOR="#3b82f6"><FONT COLOR="white"><B>Canonical_Term</B></FONT></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>PK (UUID)</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT">Scientific_Name</TD>
        <TD ALIGN="LEFT">VARCHAR</TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT">Category</TD>
        <TD ALIGN="LEFT">ENUM (Crop/Pest/Disease)</TD>
      </TR>
    </TABLE>>''')

    # Define Alias table
    dot.node('Alias', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
      <TR>
        <TD COLSPAN="2" BGCOLOR="#3b82f6"><FONT COLOR="white"><B>Alias</B></FONT></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>PK (UUID)</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>Canonical_ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>FK</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT">Dialect_Name</TD>
        <TD ALIGN="LEFT">VARCHAR</TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT">Language</TD>
        <TD ALIGN="LEFT">ENUM (BN/EN)</TD>
      </TR>
    </TABLE>>''')

    # Define Relationships table
    dot.node('Relationships', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
      <TR>
        <TD COLSPAN="2" BGCOLOR="#3b82f6"><FONT COLOR="white"><B>Relationships</B></FONT></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>PK (UUID)</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>Source_ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>FK (Canonical_Term)</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>Target_ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>FK (Canonical_Term)</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT">Relation_Type</TD>
        <TD ALIGN="LEFT">VARCHAR (e.g., TREATS)</TD>
      </TR>
    </TABLE>>''')

    # Define Document_Provenance table
    dot.node('Document_Provenance', '''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6">
      <TR>
        <TD COLSPAN="2" BGCOLOR="#3b82f6"><FONT COLOR="white"><B>Document_Provenance</B></FONT></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#eff6ff"><B>PK (UUID)</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>Relation_ID</B></TD>
        <TD ALIGN="LEFT" BGCOLOR="#f8fafc"><B>FK (Relationships)</B></TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT">Doc_ID</TD>
        <TD ALIGN="LEFT">VARCHAR (PDF Name)</TD>
      </TR>
      <TR>
        <TD ALIGN="LEFT">Page_Number</TD>
        <TD ALIGN="LEFT">INTEGER</TD>
      </TR>
    </TABLE>>''')

    # Define invisible nodes for title alignment if desired, or just use graph label
    dot.attr(label='\nFigure 6.2: Entity-Relationship diagram of the SQLite-based Dialect Knowledge Graph.',
             labelloc='b', labeljust='c', fontsize='16', fontname='Helvetica-Bold')

    # Define Edges (Relationships logic mapping)
    # Using 'arrowhead' and 'arrowtail' to simulate Crow's foot notation (1 to Many)
    dot.edge('Canonical_Term', 'Alias', label=' 1..M', dir='both', 
             arrowhead='crow', arrowtail='none', color='#1e3a8a')
             
    dot.edge('Canonical_Term', 'Relationships', label=' Source (1..M)', dir='both', 
             arrowhead='crow', arrowtail='none', color='#1e3a8a')
             
    dot.edge('Relationships', 'Document_Provenance', label=' Provenance (1..M)', dir='both', 
             arrowhead='crow', arrowtail='none', color='#1e3a8a')

    # Render to a file (will output agribot_er_diagram.png in exactly the current directory)
    dot.render(cleanup=True)
    
    # Try to display in Notebook
    try:
        display(dot)
        print("Success! Download agribot_er_diagram.png from the Colab file browser.")
    except Exception as e:
        print("Diagram saved to agribot_er_diagram.png")

if __name__ == '__main__':
    # You MUST install graphviz first in Colab!
    # !pip install graphviz
    create_professional_er_diagram()
