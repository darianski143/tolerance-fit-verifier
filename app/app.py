from flask import Flask, render_template, request
from logic import calculate_fit_details

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    
    if request.method == 'POST':
        try:
            nominal = float(request.form.get('nominal'))
            hole = request.form.get('hole')
            shaft = request.form.get('shaft')

            if not (20 <= nominal <= 50):
                error = "Diameter must be between 20 and 50 mm."
            else:
                result = calculate_fit_details(nominal, hole, shaft)
                if "error" in result:
                    error = result["error"]
                    result = None
        except ValueError:
            error = "Please enter valid numeric values."

    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
