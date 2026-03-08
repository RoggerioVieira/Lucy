import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from core.lucy_assistant import Lucy
lucy = Lucy()
lucy.run()