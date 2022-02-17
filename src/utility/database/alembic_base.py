# Import all the models, so that Base has them before being
# imported by Alembic
from src.utility.database.database import Base  # noqa
from src.utility.database.models import *  # noqa