# melody_generators/contour_generator.py
import random

# --- Contour Shape Definitions ---
# Values represent relative height/target (0 = low/start, 1 = high/peak of contour range)
# The length of the list determines the number of "steps" in the contour.
CONTOUR_SHAPES = {
    "ARCH_SIMPLE":    [0.0, 0.5, 1.0, 0.5, 0.0],         # 5 steps
    "ARCH_BROAD":     [0.0, 0.2, 0.5, 0.8, 1.0, 0.8, 0.5, 0.2, 0.0], # 9 steps
    "VALLEY_SIMPLE":  [1.0, 0.5, 0.0, 0.5, 1.0],         # 5 steps
    "VALLEY_BROAD":   [1.0, 0.8, 0.5, 0.2, 0.0, 0.2, 0.5, 0.8, 1.0], # 9 steps
    "ASCENDING_GENTLE": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], # Gradual
    "DESCENDING_GENTLE": [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
    "WAVE_SIMPLE":    [0.0, 0.7, 1.0, 0.3, 0.0, 0.5, 0.8, 0.2], # 8 steps
    "PLATEAU_HIGH":   [0.2, 0.8, 1.0, 1.0, 1.0, 0.8, 0.2],
    "PLATEAU_LOW":    [0.8, 0.2, 0.0, 0.0, 0.0, 0.2, 0.8],
    "RANDOM_WALK_ISH":[random.uniform(0.2, 0.8) for _ in range(random.randint(5,9))] # More erratic
}

# Helper: Simplified internal scale/chord functions (ideally from a shared utility or factory_params)
def get_scale_notes_simple(root, major, style):
    pentatonic_maj = [0, 2, 4, 7, 9]; pentatonic_min = [0, 3, 5, 7, 10]
    diatonic_maj = [0, 2, 4, 5, 7, 9, 11]; diatonic_min = [0, 2, 3, 5, 7, 8, 10]
    if style == 'bridge_distinct' or random.random() < 0.3: return [(root + i) % 12 for i in (diatonic_maj if major else diatonic_min)]
    else: return [(root + i) % 12 for i in (pentatonic_maj if major else pentatonic_min)]

def get_chord_tones_simple(root, type_str, factory_params): # Pass factory_params for _build_chord_voicings
    # Use the factory's more robust voicing builder if possible
    if hasattr(factory_params, '_build_chord_voicings_instance_method'): # Check if method is bound
        voicings = factory_params._build_chord_voicings_instance_method(root, type_str, octave_center=0, num_notes_pref=4)
        return [n % 12 for n in voicings]
    else: # Fallback to very simple
        root_pc = root % 12; tones = [root_pc]
        if "major" in type_str or "maj" in type_str : tones.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        elif "minor" in type_str or "min" in type_str: tones.extend([(root_pc + 3) % 12, (root_pc + 7) % 12])
        else: tones.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        return sorted(list(set(tones)))


def generate(midi_obj, track_num, chord_prog, start_time_beats, section_type, section_profile, factory_params):
    """
    Generates melody using a contour-driven approach.
    """
    print(f"    Generating Contour-Driven melody for {section_type}")
    key_root, is_major = factory_params['active_key_root'], factory_params['active_is_major']
    complexity_str = factory_params['melodic_complexity_level']
    melody_style = section_profile.get('melody_style', 'standard')
    is_hook_section = (section_type == "Chorus" or section_type == "InstrumentalHook")

    base_melody_velocity = section_profile['velocity_base'] + random.randint(5, 10) # Contour melodies can be more expressive
    if section_profile['is_peak_section']: base_melody_velocity = min(127, base_melody_velocity + 10)
    
    current_abs_beat = start_time_beats
    total_section_duration_beats = sum(d for _,_,d in chord_prog)
    last_generated_pitch = None

    # For contour-driven, we might apply one contour over a 2-bar or 4-bar phrase
    # For simplicity, let's try to apply a contour over each chord's duration first.
    
    for i, (chord_root_midi, chord_type, chord_duration_beats) in enumerate(chord_prog):
        contour_name_options = list(CONTOUR_SHAPES.keys())
        if melody_style == 'bridge_distinct':
            contour_name = random.choice(["VALLEY_BROAD", "ARCH_BROAD", "DESCENDING_GENTLE", "ASCENDING_GENTLE"])
        elif is_hook_section:
            contour_name = random.choice(["ARCH_SIMPLE", "WAVE_SIMPLE", "PLATEAU_HIGH"])
        else: # Verse
            contour_name = random.choice(contour_name_options)
        
        selected_contour_multipliers = CONTOUR_SHAPES[contour_name]
        
        # Define melodic range for this phrase based on complexity and chord
        phrase_octave = 5
        if melody_style == 'bridge_distinct' and random.random() < 0.4: phrase_octave = random.choice([4,6])
        
        # Use a central note of the chord as the "0" point of the contour for this phrase
        phrase_chord_tones = get_chord_tones_simple(chord_root_midi, chord_type, factory_params)
        phrase_contour_center_pc = random.choice(phrase_chord_tones) if phrase_chord_tones else key_root % 12
        phrase_contour_center_midi = (phrase_octave * 12) + phrase_contour_center_pc

        contour_range_semitones = 7 # Default range (a fifth)
        if complexity_str == "Simple": contour_range_semitones = 5
        elif complexity_str == "Complex": contour_range_semitones = 10
        if melody_style == 'bridge_distinct': contour_range_semitones = random.randint(7,12)


        # Generate notes for this chord's duration along the contour
        num_contour_points = len(selected_contour_multipliers)
        
        # Rhythmic density: how many notes to try and fit
        # More notes for denser rhythms or complex melodies
        num_notes_in_phrase = int(chord_duration_beats * (1.5 + section_profile['rhythmic_density_modifier'] + (0.5 if complexity_str == "Complex" else 0)))
        if melody_style == 'bridge_distinct': num_notes_in_phrase = int(chord_duration_beats * (0.5 + random.random())) # Fewer notes in bridge
        num_notes_in_phrase = max(1, num_notes_in_phrase)

        beat_step = chord_duration_beats / num_notes_in_phrase if num_notes_in_phrase > 0 else chord_duration_beats
        
        scale_for_phrase_pc = get_scale_notes_simple(key_root, is_major, melody_style)


        for note_idx in range(num_notes_in_phrase):
            current_note_time_in_phrase = note_idx * beat_step
            
            # Determine target pitch based on contour progress
            progress_along_contour = (note_idx / (num_notes_in_phrase -1) if num_notes_in_phrase > 1 else 0.5) # Normalized 0-1
            contour_point_float = progress_along_contour * (num_contour_points - 1)
            idx1 = int(contour_point_float)
            idx2 = min(idx1 + 1, num_contour_points - 1)
            interp_factor = contour_point_float - idx1
            
            mult1 = selected_contour_multipliers[idx1]
            mult2 = selected_contour_multipliers[idx2]
            interpolated_mult = mult1 + (mult2 - mult1) * interp_factor # Linear interpolation
            
            # Target pitch relative to center, then add center
            # Multiplier 0 = bottom of range, 1 = top of range
            target_pitch_offset = (interpolated_mult - 0.5) * contour_range_semitones # -0.5 to 0.5 range for multiplier
            target_pitch = phrase_contour_center_midi + target_pitch_offset
            target_pitch = int(round(target_pitch))
            target_pitch = max(48, min(84, target_pitch)) # Clamp to reasonable melodic range (C4-C6)

            # Select actual note: closest scale/chord tone to target_pitch
            # Prioritize notes from the current chord, then current scale
            best_fit_note = target_pitch # Default
            min_dist = float('inf')

            candidate_pool = []
            # Strong preference for chord tones
            for pc_offset in phrase_chord_tones:
                candidate_pool.append( (target_pitch // 12) * 12 + pc_offset ) # Same octave
                candidate_pool.append( (target_pitch // 12 - 1) * 12 + pc_offset ) # Octave below
                candidate_pool.append( (target_pitch // 12 + 1) * 12 + pc_offset ) # Octave above
            
            # Then scale tones
            for pc_offset in scale_for_phrase_pc:
                candidate_pool.append( (target_pitch // 12) * 12 + pc_offset )
                candidate_pool.append( (target_pitch // 12 - 1) * 12 + pc_offset )
                candidate_pool.append( (target_pitch // 12 + 1) * 12 + pc_offset )
            
            for note in candidate_pool:
                if abs(note - target_pitch) < min_dist:
                    min_dist = abs(note - target_pitch)
                    best_fit_note = note
                # If multiple notes are equally close, prefer one that creates a smaller interval from last_generated_pitch
                elif abs(note - target_pitch) == min_dist and last_generated_pitch is not None:
                    if abs(note - last_generated_pitch) < abs(best_fit_note - last_generated_pitch):
                        best_fit_note = note
            
            actual_pitch = max(48, min(84, best_fit_note)) # Ensure it's in melodic range

            # Smoothness constraint for very large leaps, less strict for bridge
            max_leap = 7 if melody_style != 'bridge_distinct' else 10
            if complexity_str == "Complex": max_leap +=3

            if last_generated_pitch is not None and abs(actual_pitch - last_generated_pitch) > max_leap:
                direction = 1 if actual_pitch > last_generated_pitch else -1
                actual_pitch = last_generated_pitch + direction * random.randint(1, min(max_leap, 5))
                actual_pitch = max(48, min(84, actual_pitch))


            note_duration = beat_step
            # Add some rhythmic variation
            if random.random() < 0.3:
                note_duration = random.choice([beat_step * 0.5, beat_step * 1.5, beat_step * 0.75])
                note_duration = max(0.125, min(note_duration, chord_duration_beats - current_note_time_in_phrase))


            if current_abs_beat + current_note_time_in_phrase + note_duration > start_time_beats + total_section_duration_beats + 0.01 : # Ensure not to bleed into next section
                note_duration = (start_time_beats + total_section_duration_beats) - (current_abs_beat + current_note_time_in_phrase)

            if note_duration >= 0.125:
                current_note_velocity = base_melody_velocity
                # Accent for hook's strong beats or downbeats
                absolute_note_time_for_accent = current_abs_beat + current_note_time_in_phrase
                is_bar_downbeat = (absolute_note_time_for_accent % 4.0) < 0.1 
                is_half_bar_beat = (absolute_note_time_for_accent % 2.0) < 0.1

                if is_hook_section and factory_params['hook_on_downbeat_strong'] and (is_bar_downbeat or is_half_bar_beat):
                    current_note_velocity = min(127, base_melody_velocity + 10)
                
                midi_obj.addNote(track_num, track_num, actual_pitch, current_abs_beat + current_note_time_in_phrase, note_duration * 0.98, current_note_velocity)
                last_generated_pitch = actual_pitch
        
        current_abs_beat += chord_duration_beats