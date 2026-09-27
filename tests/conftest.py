import sys
from pathlib import Path

# Garante que a raiz do projeto (onde ficam app.py, database.py etc.)
# esteja no sys.path ao rodar `pytest` a partir de qualquer diretório.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
