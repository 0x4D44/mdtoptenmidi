# app.py
from flask import Flask, render_template, request, send_file, url_for, redirect # Added redirect
import random
import io # For handling file data in memory

# Assuming your UKHitFactory class is in midi_generator.py
from midi_generator import UKHitFactory # Make sure this import works

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Serves the main page with the input form."""
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST']) # Allow GET as well now
def generate_hit():
    """Handles the MIDI generation request."""
    if request.method == 'GET':
        # If someone tries to GET this URL directly, just redirect them to the homepage.
        return redirect(url_for('index'))

    # If request.method == 'POST' (from form submission):
    seed_input = request.form.get('seed')

    if seed_input and seed_input.isdigit():
        current_seed = int(seed_input)
    else:
        current_seed = random.randint(0, 1000000)

    try:
        # Instantiate and use your MIDI generator
        hit_generator = UKHitFactory(seed=current_seed)
        hit_generator.compose()

        # Instead of saving to a file directly, write to an in-memory buffer
        midi_buffer = io.BytesIO()
        hit_generator.midi_obj.writeFile(midi_buffer)
        midi_buffer.seek(0) # Reset buffer's position to the beginning

        # Use the song_title from the generator for the filename
        song_title_for_file = hit_generator.song_title.replace(" ", "_").replace(":", "-") + ".mid"

        return send_file(
            midi_buffer,
            as_attachment=True,
            download_name=song_title_for_file,
            mimetype='audio/midi'
        )

    except Exception as e:
        # Basic error handling
        # You might want to log the full error e to the console for debugging
        print(f"Error during MIDI generation: {e}") # Log to console
        # traceback.print_exc() # For more detailed stack trace if you import traceback
        return f"An error occurred during MIDI generation: {str(e)} <br><a href='{url_for('index')}'>Try again</a>", 500


if __name__ == '__main__':
    # For development:
    app.run(debug=True)
    # For production, you'd use a proper WSGI server like Gunicorn or Waitress