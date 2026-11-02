# Analog
from .analog import router as analog
from .billing import router as billing
from .drawing.elements import router as elements
from .drawing.figures import router as drawing

# Export
from .export.analog_export import router as analog_table
from .export.drawing_export import router as drawing_table
from .export.patent_export import router as patent_table
from .identity_prototype import router as identity_prototype
from .job import router as job
from .legal import router as legal
from .organization import router as organization
from .patent import router as patent
from .patent_application import router as patent_application

# Workflows
from .search import router as search
from .statistics import router as statistics
from .user import router as user

__all__ = [
    "patent",
    "job",
    "user",
    "billing",
    "legal",
    "organization",
    # Analog
    "analog",
    # Workflows
    "search",
    "statistics",
    "identity_prototype",
    "drawing",
    "elements",
    "patent_application",
    # Export
    "analog_table",
    "patent_table",
    "drawing_table",
]
