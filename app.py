# app.py

from flask import Flask, render_template, request, jsonify
from converter import UnitConverter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/categories', methods=['GET'])
def categories():
    categories = UnitConverter.get_categories()
    return jsonify(categories)

@app.route('/units', methods=['GET'])
def units():
    category = request.args.get('category')
    units = UnitConverter.get_units(category)
    return jsonify(units)

@app.route('/convert', methods=['POST'])
def convert():
    try:
        value = float(request.form['value'])
        from_unit = request.form['from_unit']
        to_unit = request.form['to_unit']
        result = UnitConverter.convert(value, from_unit, to_unit)
        return jsonify({"result": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=False)
