from sqlalchemy.ext.declarative import declarative_base

# The simplest, most standard way to create the Base class in SQLAlchemy.
# This allows all models to inherit from a single foundation.
Base = declarative_base()
