# app.py
from flask import Flask, render_template, request, send_file, url_for, redirect
import random
import io
import traceback # For more detailed error logging

from midi_generator import UKHitFactory

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Serves the main page with the input form."""
    # We could pass default values here if needed, but HTML form handles them for now
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate_hit():
    """Handles the MIDI generation request."""
    if request.method == 'GET':
        return redirect(url_for('index'))

    # If request.method == 'POST' (from form submission):
    try:
        # --- Read all form inputs ---
        seed_input = request.form.get('seed')
        if seed_input and seed_input.isdigit():
            current_seed = int(seed_input)
        else:
            current_seed = random.randint(0, 1000000)
        
        # Gather new control values, providing defaults if not present
        generation_params = {
            'seed': current_seed,
            'primary_genre': request.form.get('primary_genre', 'ModernPop'),
            'mood': request.form.get('mood', 'UpliftingEnergetic'),
            'energy_level': int(request.form.get('energy_level', 3)), # Scale 1-5
            'tempo_preference': request.form.get('tempo_preference', 'Medium'),
            'song_length': request.form.get('song_length', 'Radio'),
            'structural_complexity': request.form.get('structural_complexity', 'Standard'),
            'melodic_complexity': int(request.form.get('melodic_complexity', 3)), # Scale 1-5
            'harmonic_richness': request.form.get('harmonic_richness', 'Some7ths'),
            'instrumentation_focus': request.form.get('instrumentation_focus', 'Balanced')
        }
        
        print(f"Received generation parameters: {generation_params}") # Log received params

        # Instantiate and use your MIDI generator, passing all params
        hit_generator = UKHitFactory(user_params=generation_params) # Pass as a dictionary
        hit_generator.compose()

        midi_buffer = io.BytesIO()
        hit_generator.midi_obj.writeFile(midi_buffer)
        midi_buffer.seek(0)

        song_title_for_file = hit_generator.song_title.replace(" ", "_").replace(":", "-") + ".mid"

        return send_file(
            midi_buffer,
            as_attachment=True,
            download_name=song_title_for_file,
            mimetype='audio/midi'
        )

    except Exception as e:
        print(f"Error during MIDI generation (app.py): {e}")
        traceback.print_exc() # Print full stack trace to console
        return f"An error occurred during MIDI generation: {str(e)} <br><a href='{url_for('index')}'>Try again</a>", 500


if __name__ == '__main__':
    app.run(debug=True)