from flask import Flask, flash , render_template , request , redirect , url_for , session
from models import *
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from db import Session







db_session = Session()


app = Flask(__name__)

@app.route('/')
def home():
    todas_las_tareas = db_session.query(Tarea).filter_by(eliminada=False).all()
    
    # Obtener el usuario actual (si está autenticado)
    usuario_actual = None
    if 'usuario_id' in session:
        usuario_actual = Usuario.query.get(session['usuario_id'])

    return render_template('index.html', lista_de_tareas=todas_las_tareas, datetime=datetime, usuario_actual=usuario_actual)



def obtener_categoria_por_id(categoria_id):
        categoria = Categoria.query.get(categoria_id)
        return categoria


@app.route('/crear-tarea', methods=["POST"])
def crear():
    contenido_tarea = request.form['contenido_tarea']
    descripcion_tarea = request.form.get('descripcion_tarea', '')
    fecha_limite_str = request.form.get('fecha_limite', '')
    categoria_id = request.form.get('categoria_id')
    

  
    fecha_limite = datetime.strptime(fecha_limite_str, '%Y-%m-%dT%H:%M') if fecha_limite_str else None

    tarea = Tarea(contenido=contenido_tarea, descripcion=descripcion_tarea, fecha_limite=fecha_limite, hecha=False)

  
    if categoria_id:
        categoria = obtener_categoria_por_id(categoria_id)
        tarea.categoria = categoria
    
    db_session.add(tarea)
    db_session.commit()

    usuario_actual = None
    if 'usuario_id' in session:
        usuario_actual = Usuario.query.get(session['usuario_id'])

    # Obtén todas las tareas y categorías desde la base de datos
    todas_las_tareas = db_session.query(Tarea).all()
    lista_de_categorias = db_session.query(Categoria).all()

    # Renderiza la página con las tareas y categorías actualizadas
    return render_template('index.html', lista_de_tareas=todas_las_tareas, lista_de_categorias=lista_de_categorias, datetime=datetime, usuario_actual=usuario_actual)


@app.route('/tarea-hecha/<id>')
def hecha(id):
    tarea = db_session.query(Tarea).filter_by(id=int(id)).first()
    tarea.hecha = not(tarea.hecha)
    db_session.commit()
    return redirect(url_for('home')) 




@app.route('/eliminar-tarea/<id>')
def eliminar(id):
    tarea = db_session.query(Tarea).filter_by(id=int(id)).first()
    tarea.eliminada = True
    db_session.commit()
    return redirect(url_for('home'))







@app.route('/obtener-todas-las-tareas')
def obtener_todas_las_tareas():
    tareas = Tarea.query.all()
    return render_template('tareas.html', lista_de_tareas=tareas)


@app.route('/filtrar_tareas', methods=['GET'])
def filtrar_tareas():
    filtro_estado = request.args.get('filtro_estado', 'todas')

    usuario_actual = None
    if 'usuario_id' in session:
        usuario_actual = Usuario.query.get(session['usuario_id'])

    if filtro_estado == 'todas':
        lista_de_tareas = db_session.query(Tarea).all()
    elif filtro_estado == 'pendientes':
        lista_de_tareas = db_session.query(Tarea).filter(Tarea.hecha == False).all()
    elif filtro_estado == 'completadas':
        lista_de_tareas = db_session.query(Tarea).filter(Tarea.hecha == True).all()

    return render_template('index.html', lista_de_tareas=lista_de_tareas, usuario_actual=usuario_actual)



def obtener_tarea_por_id(tarea_id):
    tarea = db_session.query(Tarea).get(tarea_id)
    return tarea

@app.route('/editar-tarea/<int:tarea_id>', methods=['GET', 'POST'])
def editar_tarea(tarea_id):
    tarea = obtener_tarea_por_id(tarea_id)

    if request.method == 'POST':
        # Obtener los datos del formulario y actualizar la tarea
        tarea.contenido = request.form['contenido_tarea']
        tarea.descripcion = request.form['descripcion_tarea']
        fecha_limite_str = request.form['fecha_limite']

        # Convierte la cadena de fecha y hora en un objeto de datetime
        tarea.fecha_limite = datetime.strptime(fecha_limite_str, '%Y-%m-%dT%H:%M') if fecha_limite_str else None

        # Guardar los cambios en la base de datos
        db_session.commit()

        # Redirigir a la página de detalles de la tarea
        return redirect(url_for('detalles_tarea', tarea_id=tarea.id))
    usuario_actual = None
    if 'usuario_id' in session:
        usuario_actual = Usuario.query.get(session['usuario_id'])
    # Renderiza la página de edición con la tarea específica
    return render_template('editar_tarea.html', tarea=tarea, usuario_actual=usuario_actual)


@app.route('/detalles-tarea/<int:tarea_id>')
def detalles_tarea(tarea_id):
    tarea = obtener_tarea_por_id(tarea_id)

    if tarea:
        usuario_actual = None
        if 'usuario_id' in session:
            usuario_actual = Usuario.query.get(session['usuario_id'])
        return render_template('detalles_tarea.html', tarea=tarea,usuario_actual=usuario_actual)
    else:
        # Manejar el caso donde la tarea no se encuentra
        return render_template('error.html', mensaje='Tarea no encontrada')


@app.route('/restaurar-tarea/<id>')
def restaurar_tarea(id):
    tarea = db_session.query(Tarea).filter_by(id=int(id)).first()
    tarea.eliminada = False
    db_session.commit()
    return redirect(url_for('papelera_de_reciclaje'))

@app.route('/eliminar-definitivamente/<id>')
def eliminar_definitivamente(id):
    tarea = db_session.query(Tarea).filter_by(id=int(id)).first()
    db_session.delete(tarea)
    db_session.commit()
    return redirect(url_for('papelera_de_reciclaje'))


@app.route('/papelera-de-reciclaje')
def papelera_de_reciclaje():
    tareas_eliminadas = db_session.query(Tarea).filter_by(eliminada=True).all()

    # Obtener el usuario actual (si está autenticado)
    usuario_actual = None
    if 'usuario_id' in session:
        usuario_actual = Usuario.query.get(session['usuario_id'])

    return render_template('papelera.html', tareas_eliminadas=tareas_eliminadas, usuario_actual=usuario_actual)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        email = request.form['email']

        
        # Cambia el método de hash a 'pbkdf2:sha256' o 'pbkdf2:sha512'
        contraseña = generate_password_hash(request.form['contrasena'], method='pbkdf2:sha256')
        
        print(f'Contraseña registrada: {contraseña}')

        # Crear nuevo usuario
        nuevo_usuario = Usuario(nombre=nombre, email=email, contraseña=contraseña)

        # Agregar el nuevo usuario a la sesión de la base de datos
        db_session.add(nuevo_usuario)

        # Confirmar la transacción en la base de datos
        db_session.commit()

        # Redirigir al inicio de sesión
        return redirect(url_for('login'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contrasena']
        print(f'Email: {email}')
        print(f'Contraseña: {contraseña}')
        
        # Buscar el usuario por correo electrónico
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.contraseña, contraseña, method='pbkdf2:sha256'):
            # Autenticación exitosa, almacenar información del usuario en la sesión
            session['usuario_id'] = usuario.id
            return redirect(url_for('home'))
        else:

            print(f'Usuario: {usuario}')  # Imprime el objeto de usuario para verificar si se encuentra
            print(f'Contraseña ingresada: {contraseña}')
            print(f'Contraseña almacenada: {usuario.contraseña}')
            print('Usuario no encontrado o contraseña incorrecta.')
            flash('Credenciales incorrectas', 'error')

    return render_template('index.html', usuario_actual=session.get('usuario_id'))
    
   




@app.route('/logout')
def logout():
    # Elimina la información del usuario de la sesión
    session.pop('usuario_id', None)
    return redirect(url_for('login'))























if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    app.run()



