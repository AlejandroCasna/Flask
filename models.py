import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime , func , Text , ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask import Flask, render_template, request


'''
Creamos una clase llamada Tarea
Esta clase va a ser nuestro modelo de datos de la tarea (el cual nos servirá
luego para la base de datos)
Esta clase va a almacenar toda la información referente a una tarea
'''
Base = declarative_base()

class Tarea(Base):
    __tablename__ = "tarea"
    id = Column(Integer, primary_key=True,autoincrement=True)
    contenido = Column(String(200), nullable=False)
    hecha = Column(Boolean)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_limite = Column(DateTime, nullable=True)
    descripcion = Column(Text)
    categoria_id = Column(Integer, ForeignKey('categoria.id'))
    categoria = relationship('Categoria', back_populates='tareas')
    eliminada = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', back_populates='tareas')
    
    def __init__(self, contenido, hecha, fecha_limite=None, descripcion=None):
        self.contenido = contenido
        self.hecha = hecha
        self.fecha_limite = fecha_limite
        self.descripcion = descripcion

    def filtrar_tareas():
        filtro_estado = request.args.get('filtro_estado', 'todas')

        # Lógica de filtrado según el estado
        if filtro_estado == 'todas':
            lista_de_tareas = Tarea.query.all()
        elif filtro_estado == 'pendientes':
            lista_de_tareas = Tarea.query.filter_by(hecha=False).all()
        elif filtro_estado == 'completadas':
            lista_de_tareas = Tarea.query.filter_by(hecha=True).all()

        # Pasa la lista filtrada a la plantilla
        return render_template('tu_plantilla.html', lista_de_tareas=lista_de_tareas)

class Categoria(Base):
    __tablename__ = 'categoria'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    # Definir la relación con la clase Tarea
    tareas = relationship('Tarea', back_populates='categoria')

    def __init__(self, nombre):
        self.nombre = nombre



    
    
class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    contraseña = Column(String(100), nullable=False)
    
    # Relación con la clase Tarea
    tareas = relationship('Tarea', back_populates='usuario')