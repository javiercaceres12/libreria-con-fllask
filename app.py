from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

#Con app creamos nuestra aplicacion
app = Flask(__name__) 
app.secret_key="javiercaceres"
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sitio'
app.config['MYSQL_DATABASE_PORT'] = 3307
mysql.init_app(app)

#SECCION SITIO

@app.route('/')
def inicio(): # <- capturamos lo que el usuario va a escribir en su navegador
    return render_template('sitio/index.html') # <- mostramos el index.html

@app.route('/img/<imagen>')
def imagenes(imagen):
    import os
    print(imagen) 
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route("/css/<archivo>")
def css_archivo(archivo):
    import os
    return send_from_directory(os.path.join('templates/sitio/css'),archivo)

@app.route('/libros')
def libros():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall()
    conexion.commit()

    return render_template('sitio/libros.html', lista_libros = libros)

@app.route('/contacto')
def contacto():
    return render_template('sitio/contacto.html')

#SECCION ADMINISTRADOR

@app.route('/admin/')
def inicio_admin():
    if not 'login' in session:
        return redirect('/admin/login')

    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['txtusuario']
    _password = request.form['txtpassword']
    print(_usuario)
    print(_password)

    if _usuario == "admindelsitio" and _password == "1169351191":
        session["login"] = True
        session["usuario"] = "Administrador"
        return redirect('/admin')

    return render_template("admin/login.html", mensaje = "Acceso Denegado") 

@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template('admin/libros.html', lista_libros=libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():
    if not 'login' in session:
        return redirect('/admin/login')
    
    _nombre = request.form['txtnombre']
    _url = request.form['txtURL']
    _archivo = request.files['txtimagen']

    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M%S')

    if _archivo.filename != "":
        nuevoNombre = horaActual+""+_archivo.filename
        _archivo.save('templates/sitio/img/' + nuevoNombre)

    sql = "INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, nuevoNombre, _url)

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()

    print(_nombre)
    print(_archivo)
    print(_url)

    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods = ['POST'])
def admin_libros_borrar():
    if not 'login' in session:
        return redirect('/admin/login')

    import os
    _id = request.form['txtID']
    print(_id)

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s", (_id))
    libro = cursor.fetchall()
    conexion.commit()
    print(libro)

    if os.path.exists('templates/sitio/img/'+str(libro[0][0])):
        os.unlink('templates/sitio/img/'+str(libro[0][0]))

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id=%s", (_id))
    conexion.commit()

    return redirect('/admin/libros')

#si la aplicacion esta lista le decimos que corra e inicie debug.
if __name__ == '__main__': 
    app.run(debug=True)
