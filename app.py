from flask import Flask, render_template, request, redirect, url_for, flash
import json
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración para subir archivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Definir las secciones con sus respectivas imágenes
sections = [
    {'name': 'Brown', 'streets': ['cartas monopoly español_page-0004.jpg', 'cartas monopoly español_page-0005.jpg']},
    {'name': 'Light Blue', 'streets': ['cartas monopoly español_page-0001.jpg', 'cartas monopoly español_page-0002.jpg', 'cartas monopoly español_page-0003.jpg']},
    {'name': 'Pink', 'streets': ['cartas monopoly español_page-0020.jpg', 'cartas monopoly español_page-0021.jpg', 'cartas monopoly español_page-0022.jpg']},
    {'name': 'Orange', 'streets': ['cartas monopoly español_page-0017.jpg', 'cartas monopoly español_page-0018.jpg', 'cartas monopoly español_page-0019.jpg']},
    {'name': 'Red', 'streets': ['cartas monopoly español_page-0014.jpg', 'cartas monopoly español_page-0015.jpg', 'cartas monopoly español_page-0016.jpg']},
    {'name': 'Yellow', 'streets': ['cartas monopoly español_page-0011.jpg', 'cartas monopoly español_page-0012.jpg', 'cartas monopoly español_page-0013.jpg']},
    {'name': 'Green', 'streets': ['cartas monopoly español_page-0008.jpg', 'cartas monopoly español_page-0009.jpg', 'cartas monopoly español_page-0010.jpg']},
    {'name': 'Blue', 'streets': ['cartas monopoly español_page-0006.jpg', 'cartas monopoly español_page-0007.jpg']}
]

extras = [
    {'name' : 'Stations', 'carts': ['cartas monopoly español_page-0023.jpg', 'cartas monopoly español_page-0024.jpg', 'cartas monopoly español_page-0025.jpg', 'cartas monopoly español_page-0026.jpg']},
    {'name' : 'Companies', 'carts': ['cartas monopoly español_page-0027.jpg', 'cartas monopoly español_page-0020.jpg']},
    {'name' : 'Extra', 'carts': ['cartas monopoly español_page-0028.jpg', 'cartas monopoly español_page-0029.jpg']},
    ]

# Función para verificar la extensión de archivo permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para la página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para ingresar el nombre del tablero
@app.route('/board-name', methods=['GET', 'POST'])
def board_name():
    if request.method == 'POST':
        board_name = request.form.get('board_name', '')
        return redirect(url_for('customize', board_name=board_name))
    return render_template('board_name.html')

# Ruta para la personalización de calles
@app.route('/customize', methods=['GET', 'POST'])
def customize():
    board_name = request.args.get('board_name', '')
    if request.method == 'POST':
        streets = {}
        for section in sections:
            section_name = section['name']
            streets[section_name] = {}
            for i, street_image in enumerate(section['streets']):
                street_key = f'streets[{section_name}][{i}]'
                street_value = request.form.get(street_key, '').strip()
                streets[section_name][i + 1] = street_value
        
        return redirect(url_for('summary', board_name=board_name, streets=json.dumps(streets)))
    
    return render_template('customize.html', sections=sections, board_name=board_name)

# Ruta para personalización adicional de cartas
@app.route('/customize_more', methods=['GET', 'POST'])
def customize_more():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect('monopoly.db')
            c = conn.cursor()

            # Handle stations
            station_names = request.form.getlist('station_names[]')
            station_images = request.files.getlist('station_images[]')
            station_filenames = []

            for image in station_images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    station_filenames.append(filename)

            # Handle companies
            company_names = request.form.getlist('company_names[]')
            company_images = request.files.getlist('company_images[]')
            company_filenames = []

            for image in company_images:
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    company_filenames.append(filename)

            # Handle luck card
            luck_image = request.files['luck_image']
            luck_filename = ''
            if luck_image and allowed_file(luck_image.filename):
                luck_filename = secure_filename(luck_image.filename)
                luck_image.save(os.path.join(app.config['UPLOAD_FOLDER'], luck_filename))

            # Handle treasury card
            treasury_image = request.files['treasury_image']
            treasury_filename = ''
            if treasury_image and allowed_file(treasury_image.filename):
                treasury_filename = secure_filename(treasury_image.filename)
                treasury_image.save(os.path.join(app.config['UPLOAD_FOLDER'], treasury_filename))

            # Handle custom card
            custom_card_image = request.files['custom_card_image']
            custom_card_filename = ''
            if custom_card_image and allowed_file(custom_card_image.filename):
                custom_card_filename = secure_filename(custom_card_image.filename)
                custom_card_image.save(os.path.join(app.config['UPLOAD_FOLDER'], custom_card_filename))
            
            # Retrieve the custom card text
            custom_card_text = request.form.get('custom_card_text', '')

            # Insert into custom_cards table
            c.execute('''
                INSERT INTO custom_cards 
                (station_name, station_image, company_name, company_image, luck_image, treasury_image, custom_card_image, custom_card_text) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (json.dumps(station_names), json.dumps(station_filenames), json.dumps(company_names), json.dumps(company_filenames), luck_filename, treasury_filename, custom_card_filename, custom_card_text))
            
            conn.commit()
            conn.close()

            flash('¡Personalización guardada correctamente!', 'success')
            return redirect(url_for('summary_final', board_name=board_name))

        except Exception as e:
            flash(f'Error al guardar la personalización: {str(e)}', 'danger')
            return redirect(url_for('customize_more'))

    return render_template('customize_more.html', extras=extras)

# Ruta para el resumen inicial
@app.route('/summary', methods=['GET', 'POST'])
def summary():
    board_name = request.args.get('board_name', 'My Monopoly Board')
    streets_json = request.args.get('streets', '{}')
    streets = json.loads(streets_json)

    if request.method == 'POST':
        try:
            # Guardar los datos en la base de datos
            conn = sqlite3.connect('monopoly.db')
            c = conn.cursor()

            # Insertar el tablero
            c.execute('INSERT INTO boards (board_name) VALUES (?)', (board_name,))
            board_id = c.lastrowid

            # Insertar las calles
            for section_name, street_numbers in streets.items():
                for street_number, street_name in street_numbers.items():
                    c.execute('''
                        INSERT INTO streets (board_id, section_name, street_number, street_name)
                        VALUES (?, ?, ?, ?)
                    ''', (board_id, section_name, street_number, street_name))

            conn.commit()
            conn.close()

            # Redirigir a customize_more
            return redirect(url_for('customize_more', board_name=board_name))

        except Exception as e:
            flash(f'Error al guardar los datos: {str(e)}', 'danger')
            return redirect(url_for('customize_more'))

    return render_template('summary.html', board_name=board_name, streets=streets)


# Ruta para el resumen final con todos los datos
@app.route('/summary_final', methods=['GET'])
def summary_final():
    board_name = request.args.get('board_name', 'My Monopoly Board')
    streets_json = request.args.get('streets', '{}')
    streets = json.loads(streets_json)

    # Obtener datos de personalización adicional de cartas desde la base de datos
    conn = sqlite3.connect('monopoly.db')
    c = conn.cursor()
    
    # Obtener la última fila insertada en custom_cards
    c.execute('SELECT * FROM custom_cards ORDER BY id DESC LIMIT 1')
    custom_card_data = c.fetchone()
    
    conn.close()

    return render_template('summary_final.html', board_name=board_name, streets=streets, custom_card_data=custom_card_data, extras=extras)

# Ruta para el dashboard
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('monopoly.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM boards')
    boards = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', boards=boards)

# Ruta para el dashboard2
@app.route('/dashboard2')
def dashboard2():
    conn = sqlite3.connect('monopoly.db')
    c = conn.cursor()

    # Consulta para obtener todas las calles
    c.execute('SELECT * FROM streets')
    streets = c.fetchall()

    conn.close()

    return render_template('dashboard2.html', streets=streets)

# Ruta para los detalles del tablero
@app.route('/board/<int:board_id>')
def board_details(board_id):
    conn = sqlite3.connect('monopoly.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM boards WHERE id = ?', (board_id,))
    board = c.fetchone()
    
    c.execute('SELECT * FROM streets WHERE board_id = ?', (board_id,))
    streets = c.fetchall()
    
    conn.close()
    
    return render_template('board_details.html', board=board, streets=streets)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
