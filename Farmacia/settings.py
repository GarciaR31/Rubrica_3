"""
Django settings for Farmacia project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-el@dr+w00qr0x_-e0e6v!(lj^gu=!dfmr@ftafg3lu$o3r0^ud'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Farmacia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Farmacia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
from flask import Flask, flash, render_template, request, redirect, url_for
from __init__ import app, conn
import pyodbc
#
def obtener_datos(tabla):
    cursor = conn.cursor()
    
    query = f'SELECT * FROM {tabla}'
    
    cursor.execute(query)
    data = cursor.fetchall()
    return data

#
import pyodbc

def crear(tabla):
    cursor = conn.cursor()

    try:
        cursor.execute(f'CREATE TABLE {tabla} (id AUTOINCREMENT PRIMARY KEY, productos TEXT, cantidades INTEGER, precios INTEGER)')
        conn.commit()
        print(f"Tabla '{tabla}' creada exitosamente.")
    except pyodbc.ProgrammingError as e:
        if 'Tabla ya existe' in str(e):  # Ajusta el mensaje según el mensaje de error real
            print(f"La tabla '{tabla}' ya existe.")
        else:
            print(f"No se pudo crear la tabla: {str(e)}")
#   
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombres = request.form['nombres']
        edad = request.form['edad']
        malestar = request.form['malestar']
        genero = request.form['genero']
        
        crear(nombres)
        
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Usuario (nombres, edad, malestar, genero) VALUES (?, ?, ?, ?)", (nombres, edad, malestar, genero))
        conn.commit()
        return redirect(url_for('agregar_pro',nombre=nombres))
    return render_template('Index.html')

#
@app.route('/agregar/<nombre>', methods=['GET', 'POST'])
def agregar(nombre):
    data_dp = obtener_datos('Deposito')

    if request.method == 'POST':
        nombre = request.args.get('nombre')
        cantidad = int(request.form['cantidad'])
        producto = request.form['producto']
        
        flash(f'{cantidad} unidades de {producto} agregadas a la lista', 'success')

        return redirect(url_for('agregar_pro', nombre=nombre))

    return render_template('agregar.html', nombre=nombre, data_dp=data_dp)

#
@app.route('/Bodega')
def bodega():
    data_dp = obtener_datos('Deposito')
    return render_template('Bodega.html', data_dp=data_dp)

#
@app.route('/agregar_pro/<nombre>')
def agregar_pro(nombre):
    data_dp = obtener_datos('Deposito')
    return render_template('agregar.html', nombre=nombre, data_dp=data_dp)

#
@app.route('/actualizar_cantidad/<int:id>/<nombre>', methods=['POST'])
def actualizar_cantidad(id, nombre):
    if request.method == 'POST':
        nueva_cantidad = int(request.form['cantidad'])
        producto_nombre = request.form['producto_nombre']
        precios_productos = int(request.form['precios'])

        cursor = conn.cursor()
        cursor.execute("SELECT cantidad FROM Deposito WHERE id = ?", (id,))
        cantidad_actual = cursor.fetchone()[0]

        if nueva_cantidad > cantidad_actual:
            flash('La cantidad seleccionada supera la cantidad disponible en el depósito.', 'error')
        else:
            nueva_cantidad_deposito = cantidad_actual - nueva_cantidad
            cursor.execute("UPDATE Deposito SET cantidad = ? WHERE id = ?", (nueva_cantidad_deposito, id))
            cursor.execute(f"INSERT INTO {nombre} (productos, cantidades, precios) VALUES (?, ?, ?)", (producto_nombre, nueva_cantidad, precios_productos))
            conn.commit()

    return redirect(url_for('agregar_pro', nombre=nombre))
#
def listados(nombre):
    data_list = obtener_datos(nombre)
    return render_template('listados.html', nombre_tabla=nombre, data_list=data_list)
#
@app.route('/listados/<nombre>')
def mostrar_listados(nombre):
    return listados(nombre)
#
if __name__ == '__main__':
    app.run(debug=True)