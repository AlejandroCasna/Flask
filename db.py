from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Comunicacion con SQLite
engine = create_engine('sqlite:///database/tareas.db', connect_args={'check_same_thread': False})

# Crear una clase de sesión de SQLAlchemy
Session = sessionmaker(bind=engine)

# Crear una instancia de la clase de sesión (no es necesario crearla aquí)
# session = Session()

# Declarar la clase Base de SQLAlchemy
Base = declarative_base()