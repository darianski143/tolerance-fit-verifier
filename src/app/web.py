from pathlib import Path
import sys

from flask import Flask, render_template, request

# Prefer package-relative import for bundled/packaged runs; fallback for plain script.
try:
    from .logic import calculate_fit_details  # type: ignore
except ImportError:  # pragma: no cover - fallback when run as a script
    from logic import calculate_fit_details  # type: ignore


def resource_path(relative: str) -> Path:
    """
    Resolve resource paths for both dev and PyInstaller builds.
    In frozen mode, data lives under _MEIPASS/app/<relative>; otherwise under src/app/<relative>.
    """
    if hasattr(sys, "_MEIPASS"):  # type: ignore[attr-defined]
        return Path(sys._MEIPASS) / "app" / relative  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent / relative


app = Flask(
    __name__,
    template_folder=str(resource_path("templates")),
    static_folder=str(resource_path("static")),
)

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
