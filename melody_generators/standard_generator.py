# melody_generators/standard_generator.py
import random

# These methods were previously part of UKHitFactory and are now self-contained here.
# They will need access to some parameters from the main UKHitFactory instance,
# so those will be passed in via the `factory_params` argument.

def _create_melodic_motif(num_beats_motif, home_chord_root, home_chord_type, key_root, is_major, complexity_level_str, melody_style, factory_params):
    """ Creates a short, somewhat memorable motif. """
    motif_notes = []; attempts = 0
    
    # Access scale generation from factory_params if needed, or pass scale directly
    # For now, assuming _get_scale_notes and _build_chord_voicings might be utility functions
    # accessible globally or passed in, or we replicate simplified versions here.
    # Let's assume they might be part of factory_params or a utility module later.
    # For now, simplified internal logic for scales/chords.
    
    def get_scale_notes_simple(root, major, style): # Simplified internal version
        pentatonic_maj = [0, 2, 4, 7, 9]
        pentatonic_min = [0, 3, 5, 7, 10]
        diatonic_maj = [0, 2, 4, 5, 7, 9, 11]
        diatonic_min = [0, 2, 3, 5, 7, 8, 10]
        if style == 'bridge_distinct':
            return [(root + i) % 12 for i in (diatonic_maj if major else diatonic_min)]
        else:
            return [(root + i) % 12 for i in (pentatonic_maj if major else pentatonic_min)]

    def get_chord_tones_simple(root, type_str): # Simplified internal version
        root_pc = root % 12
        tones = [root_pc]
        if "major" in type_str or "maj" in type_str : tones.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        elif "minor" in type_str or "min" in type_str: tones.extend([(root_pc + 3) % 12, (root_pc + 7) % 12])
        else: tones.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        return sorted(list(set(tones)))

    scale_notes_pc = get_scale_notes_simple(key_root, is_major, melody_style)
    chord_tones_pc = get_chord_tones_simple(home_chord_root, home_chord_type)
    if not chord_tones_pc: chord_tones_pc = [key_root % 12]
        
    base_octave = 5
    if melody_style == 'bridge_distinct' and random.random() < 0.3: base_octave = random.choice([4,5,6])
    current_motif_beat = 0
    
    start_pitch_pc = random.choice(chord_tones_pc)
    if melody_style == 'bridge_distinct' and len(chord_tones_pc) > 1:
         start_pitch_pc = random.choice(chord_tones_pc[len(chord_tones_pc)//2:])
    
    start_pitch = (base_octave * 12) + start_pitch_pc
    start_duration = random.choice([0.5, 1.0, 0.75])
    if melody_style == 'bridge_distinct': start_duration = random.choice([1.0, 1.5, 2.0, 0.75])

    motif_notes.append((start_pitch, 0, min(start_duration, num_beats_motif)))
    current_motif_beat += min(start_duration, num_beats_motif); last_pitch_val = start_pitch
    
    num_motif_notes = random.randint(2, 4)
    if melody_style == 'bridge_distinct': num_motif_notes = random.randint(1,3)

    for i in range(1, num_motif_notes):
        if current_motif_beat >= num_beats_motif: break
        next_pitch_pc = last_pitch_val % 12; attempts = 0
        if random.random() < (0.4 if melody_style == 'bridge_distinct' else 0.7):
            step_options = [-1, -2, 1, 2]
            if melody_style == 'bridge_distinct': step_options.extend([-3,3,-4,4, -5, 5, -7, 7])
            step = random.choice(step_options)
            next_pitch_pc = (next_pitch_pc + step + 12) % 12
            while next_pitch_pc not in scale_notes_pc and attempts < 5:
                next_pitch_pc = (next_pitch_pc + random.choice([-1,1]) +12) % 12; attempts+=1
        else: next_pitch_pc = random.choice(scale_notes_pc if random.random() <0.5 else chord_tones_pc)
        next_pitch = (base_octave * 12) + next_pitch_pc
        
        max_leap_from_start = (6 if complexity_level_str == "Simple" else (9 if complexity_level_str == "Moderate" else 12))
        if melody_style == 'bridge_distinct': max_leap_from_start = 14
        if abs(next_pitch - start_pitch) > max_leap_from_start :
            diff_octaves = (next_pitch // 12) - (start_pitch // 12)
            if abs(diff_octaves) > 0 : next_pitch -= diff_octaves * 12 * (1 if random.random() < 0.7 else 0)
            if abs(next_pitch - start_pitch) > max_leap_from_start: next_pitch = last_pitch_val + random.choice([-1,1,2,-2,3,-3])
        
        duration = random.choice([0.25, 0.5, 0.5, 0.75, 1.0])
        if melody_style == 'bridge_distinct': duration = random.choice([0.75, 1.0, 1.5, 2.0])
        if current_motif_beat + duration > num_beats_motif: duration = num_beats_motif - current_motif_beat
        if duration < 0.125: continue
        motif_notes.append((next_pitch, current_motif_beat, duration))
        current_motif_beat += duration; last_pitch_val = next_pitch
    return motif_notes

def _apply_motif_variation(motif, variation_type="rhythmic_simple"):
    varied_motif = []
    if not motif: return []
    if variation_type == "rhythmic_simple":
        current_beat_offset = 0
        for p, mb, md in motif:
            new_dur = md
            if random.random() < 0.3:
                if md == 0.5: new_dur = random.choice([0.25, 0.75])
                elif md == 1.0: new_dur = random.choice([0.5, 0.75, 1.25])
                elif md == 0.25: new_dur = 0.5
            new_dur = max(0.125, new_dur)
            varied_motif.append((p, current_beat_offset, new_dur))
            current_beat_offset +=new_dur
        return varied_motif
    elif variation_type == "pitch_ornament":
        current_beat_offset = 0
        if len(motif) > 1:
            idx_to_ornament = random.randrange(len(motif))
            for i, (p, mb, md) in enumerate(motif):
                if i == idx_to_ornament and md > 0.25:
                    neighbor_tone = p + random.choice([-1,-2,1,2])
                    varied_motif.append((p, current_beat_offset, md/2))
                    current_beat_offset += md/2
                    varied_motif.append((neighbor_tone, current_beat_offset, md/2))
                    current_beat_offset += md/2
                else:
                    varied_motif.append((p,current_beat_offset,md))
                    current_beat_offset += md
            return varied_motif
    return list(motif) # Return copy if no variation applied

def _generate_melodic_phrase(num_beats, current_chord_root, current_chord_type, key_root, is_major, complexity_level_str, section_profile, is_hook_on_downbeat_section, factory_params, motif_to_develop=None, is_motif_repetition=False):
    phrase_notes = []
    melody_style = section_profile.get('melody_style', 'standard')
    
    # Access scale/chord tone functions - assuming they might come from factory_params or be utility
    # For now, using simplified internal versions.
    def get_scale_notes_simple(root, major, style):
        pentatonic_maj = [0, 2, 4, 7, 9]; pentatonic_min = [0, 3, 5, 7, 10]
        diatonic_maj = [0, 2, 4, 5, 7, 9, 11]; diatonic_min = [0, 2, 3, 5, 7, 8, 10]
        if style == 'bridge_distinct' or random.random() < 0.3: return [(root + i) % 12 for i in (diatonic_maj if major else diatonic_min)]
        else: return [(root + i) % 12 for i in (pentatonic_maj if major else pentatonic_min)]

    def get_chord_tones_simple(root, type_str):
        root_pc = root % 12; tones = [root_pc]
        if "major" in type_str or "maj" in type_str : tones.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        elif "minor" in type_str or "min" in type_str: tones.extend([(root_pc + 3) % 12, (root_pc + 7) % 12])
        else: tones.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        return sorted(list(set(tones)))

    scale_notes_pc = get_scale_notes_simple(key_root, is_major, melody_style)
    chord_tones_pc = get_chord_tones_simple(current_chord_root, current_chord_type)
    if not chord_tones_pc: chord_tones_pc = [key_root % 12]

    base_octave = 5; current_mel_beat = 0; last_pitch = None; num_notes_in_phrase = 0
    
    current_motif_instance = motif_to_develop
    if motif_to_develop and is_motif_repetition and random.random() < 0.6:
        variation_choice = random.choice(["rhythmic_simple", "pitch_ornament", "none"])
        if variation_choice != "none":
            current_motif_instance = _apply_motif_variation(motif_to_develop, variation_choice)
    
    if current_motif_instance and random.random() < (0.8 if is_hook_on_downbeat_section else (0.3 if melody_style != 'bridge_distinct' else 0.1) ):
        motif_total_duration = sum(md for _,_,md in current_motif_instance)
        if current_mel_beat + motif_total_duration <= num_beats + 0.01:
            for p, mb_in_motif, md in current_motif_instance:
                actual_start_beat = current_mel_beat + mb_in_motif
                if actual_start_beat + md > num_beats + 0.01 : continue
                varied_pitch = p
                is_strong_motif_beat = (mb_in_motif == 0.0 or mb_in_motif % 1.0 == 0.0)
                if is_strong_motif_beat and ( (varied_pitch % 12) not in chord_tones_pc ):
                    if chord_tones_pc : varied_pitch = (varied_pitch // 12)*12 + random.choice(chord_tones_pc)
                phrase_notes.append({'pitch': varied_pitch, 'time': actual_start_beat, 'duration': md})
                last_pitch = varied_pitch
            current_mel_beat += motif_total_duration
            num_notes_in_phrase += len(current_motif_instance)

    rhythmic_density_for_walk = section_profile['rhythmic_density_modifier']
    if melody_style == 'bridge_distinct': rhythmic_density_for_walk *= 0.7

    while current_mel_beat < num_beats - 0.125 and num_notes_in_phrase < (num_beats * 2.0 * rhythmic_density_for_walk):
        note_duration_options = [0.5, 1.0, 0.25]
        if melody_style == 'bridge_distinct': note_duration_options = [1.0, 1.5, 0.75, 2.0]
        if complexity_level_str == "Complex": note_duration_options.extend([0.125, 0.33])
        note_duration = random.choice(note_duration_options)
        if current_mel_beat + note_duration > num_beats: note_duration = num_beats - current_mel_beat
        if note_duration < 0.125: break
        is_strong_beat = ((current_mel_beat - (current_mel_beat % 4)) % 2.0 == 0.0)
        possible_next_pitches_pc = []
        if is_hook_on_downbeat_section and factory_params['hook_on_downbeat_strong'] and is_strong_beat: possible_next_pitches_pc = chord_tones_pc
        elif random.random() < (0.5 if melody_style == 'bridge_distinct' else 0.7): possible_next_pitches_pc.extend(chord_tones_pc)
        if not possible_next_pitches_pc: possible_next_pitches_pc.extend(scale_notes_pc)
        if not possible_next_pitches_pc: possible_next_pitches_pc = [(key_root + i) % 12 for i in [0,2,4,5,7,9,11]]
        chosen_pitch_pc = random.choice(possible_next_pitches_pc)
        next_pitch = (base_octave * 12) + chosen_pitch_pc
        if last_pitch is not None:
            max_interval = 5 if complexity_level_str == "Simple" else (9 if melody_style == 'bridge_distinct' else 7)
            if complexity_level_str == "Complex": max_interval = 10
            interval = abs(next_pitch - last_pitch); attempts = 0;
            while interval > max_interval and attempts < 3:
                chosen_pitch_pc_alt = random.choice(possible_next_pitches_pc)
                next_pitch_alt = (base_octave * 12) + chosen_pitch_pc_alt
                if abs(next_pitch_alt - last_pitch) < interval: next_pitch = next_pitch_alt
                interval = abs(next_pitch - last_pitch); attempts += 1
        phrase_notes.append({'pitch': next_pitch, 'time': current_mel_beat, 'duration': note_duration})
        last_pitch = next_pitch; current_mel_beat += note_duration; num_notes_in_phrase +=1
    return phrase_notes

def generate(midi_obj, track_num, chord_prog, start_time_beats, section_type, section_profile, factory_params):
    """
    Main function for the standard melody generator.
    This replaces the old _add_melody_line's core logic.
    """
    key_root, is_major = factory_params['active_key_root'], factory_params['active_is_major']
    complexity_str = factory_params['melodic_complexity_level']
    is_hook_section = (section_type == "Chorus" or section_type == "InstrumentalHook")
    
    base_melody_velocity = section_profile['velocity_base'] + random.randint(3, 8)
    if section_profile['is_peak_section']: base_melody_velocity = min(120, base_melody_velocity + 10)
    current_abs_beat = start_time_beats
    total_section_duration_beats = sum(d for _,_,d in chord_prog)
    
    hook_motif_key = f"{section_type}_motif"
    if is_hook_section and not factory_params.get(hook_motif_key) and section_profile.get('melody_style') != 'bridge_distinct':
        motif_chord_root, motif_chord_type, _ = chord_prog[0]
        # Pass factory_params to _create_melodic_motif
        factory_params[hook_motif_key] = _create_melodic_motif(
            random.choice([1.0, 2.0]), motif_chord_root, motif_chord_type, 
            key_root, is_major, complexity_str, section_profile.get('melody_style', 'standard'),
            factory_params 
        )
    
    motif_for_current_phrase = None
    if is_hook_section and factory_params.get(hook_motif_key) and section_profile.get('melody_style') != 'bridge_distinct':
        motif_for_current_phrase = factory_params[hook_motif_key]

    for i, (chord_root_midi, chord_type, chord_duration_beats) in enumerate(chord_prog):
        progress_within_section = (current_abs_beat - start_time_beats) / total_section_duration_beats if total_section_duration_beats > 0 else 0
        current_note_overall_velocity = base_melody_velocity
        if section_profile['build_tension']:
            current_note_overall_velocity = int(base_melody_velocity + (20 * progress_within_section))
            current_note_overall_velocity = min(115, current_note_overall_velocity)
        elif section_type == "Outro": 
            current_note_overall_velocity = int(base_melody_velocity * (1 - progress_within_section * 0.9))
        
        is_motif_repetition_in_hook = is_hook_section and (i > 0 or (i==0 and factory_params.get(f"{hook_motif_key}_used_once", False)))
        
        melodic_phrase_notes_data = _generate_melodic_phrase(
            chord_duration_beats, chord_root_midi, chord_type, key_root, is_major,
            complexity_str, section_profile, is_hook_section, factory_params, # Pass factory_params
            motif_to_develop=(motif_for_current_phrase if section_profile.get('melody_style') != 'bridge_distinct' else None),
            is_motif_repetition=is_motif_repetition_in_hook
        )
        if is_hook_section and i == 0 and section_profile.get('melody_style') != 'bridge_distinct':
             factory_params[f"{hook_motif_key}_used_once"] = True

        for note_data in melodic_phrase_notes_data:
            pitch, time_in_phrase, duration = note_data['pitch'], note_data['time'], note_data['duration']
            final_vel = current_note_overall_velocity
            is_strong_beat_in_phrase = (time_in_phrase == 0.0 or time_in_phrase % 1.0 == 0.0)
            if is_hook_section and factory_params['hook_on_downbeat_strong'] and is_strong_beat_in_phrase:
                final_vel = min(127, current_note_overall_velocity + 10)
            elif section_profile['build_tension'] and pitch > (5*12 + 7): # G5
                 final_vel = min(127, current_note_overall_velocity + 5)
            absolute_note_time = current_abs_beat + time_in_phrase
            midi_obj.addNote(track_num, track_num, pitch, absolute_note_time, duration * 0.98, final_vel)
        current_abs_beat += chord_duration_beats