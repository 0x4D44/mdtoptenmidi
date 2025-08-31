# midi_generator.py
import random
from midiutil import MIDIFile

# Import the new melody generator modules
from melody_generators import standard_generator 
from melody_generators import contour_generator 
# from melody_generators import markov_generator

# --- Version ---
GENERATOR_VERSION = "0.8.6" # Phase 7 - Drum Break Indentation Fix

class UKHitFactory:
    def __init__(self, user_params):
        self.user_params = user_params
        self.seed = user_params.get('seed', random.randint(0,1000000))
        random.seed(self.seed)
        
        self.song_title = f"UKHitFactory_v{GENERATOR_VERSION}_Seed_{self.seed}"
        self.num_instrument_tracks = 5
        self.midi_obj = MIDIFile(numTracks=self.num_instrument_tracks, removeDuplicates=True, deinterleave=False)
        self.track_map = {"Drums": 0, "Bass": 1, "Chords": 2, "Melody": 3, "Pad": 4}

        self.params = {} 
        self._initialize_and_process_parameters()

    def _initialize_and_process_parameters(self):
        self.params['seed'] = self.seed
        primary_genre = self.user_params.get('primary_genre', 'ModernPop')
        mood = self.user_params.get('mood', 'UpliftingEnergetic')
        self.params['primary_genre'] = primary_genre
        self.params['mood'] = mood

        tempo_preference = self.user_params.get('tempo_preference', 'Medium')
        if tempo_preference == "VerySlow": self.params['bpm'] = random.randint(60, 80)
        elif tempo_preference == "Slow": self.params['bpm'] = random.randint(80, 100)
        elif tempo_preference == "Medium": self.params['bpm'] = random.randint(100, 120)
        elif tempo_preference == "Fast": self.params['bpm'] = random.randint(120, 140)
        elif tempo_preference == "VeryFast": self.params['bpm'] = random.randint(140, 165)
        else: 
            if primary_genre == "Ballad": self.params['bpm'] = random.randint(65, 90)
            elif primary_genre == "HipHopGroove": self.params['bpm'] = random.randint(80, 105)
            elif primary_genre == "EDMPulse": self.params['bpm'] = random.randint(120, 135)
            elif primary_genre == "RetroSynthwave": self.params['bpm'] = random.randint(90, 120)
            else: self.params['bpm'] = random.randint(100, 130)
        if tempo_preference == "Any":
            energy_level = self.user_params.get('energy_level', 3)
            if energy_level == 1: self.params['bpm'] = max(60, self.params['bpm'] - 20)
            elif energy_level == 2: self.params['bpm'] = max(60, self.params['bpm'] - 10)
            elif energy_level == 4: self.params['bpm'] = min(180, self.params['bpm'] + 10)
            elif energy_level == 5: self.params['bpm'] = min(180, self.params['bpm'] + 20)
        for track_num in range(self.midi_obj.numTracks):
            self.midi_obj.addTempo(track_num, 0, self.params['bpm'])
        print(f"Selected BPM: {self.params['bpm']}")

        song_length_pref = self.user_params.get('song_length', 'Radio')
        if song_length_pref == "Short": self.params['target_duration_seconds'] = random.randint(120, 150)
        elif song_length_pref == "Radio": self.params['target_duration_seconds'] = random.randint(150, 195)
        elif song_length_pref == "Standard": self.params['target_duration_seconds'] = random.randint(195, 240)
        elif song_length_pref == "Extended": self.params['target_duration_seconds'] = random.randint(240, 285)
        else: self.params['target_duration_seconds'] = random.randint(150, 195)

        keys_info_major = [(0, "C Major"), (2, "D Major"), (5, "F Major"), (7, "G Major")]
        keys_info_minor = [(9, "A Minor"), (4, "E Minor"), (2, "D Minor"), (7, "G Minor")]
        is_major_key = True
        if mood == "MelancholySentimental": is_major_key = random.random() < 0.1
        elif mood == "DarkIntense": is_major_key = random.random() < 0.2
        elif mood == "NeutralReflective": is_major_key = random.random() < 0.5
        elif mood == "HappyBright": is_major_key = random.random() < 0.9
        elif mood == "UpliftingEnergetic": is_major_key = random.random() < 0.85
        if is_major_key: chosen_key_root, chosen_key_name = random.choice(keys_info_major)
        else: chosen_key_root, chosen_key_name = random.choice(keys_info_minor)
        self.params['key_root_original'] = chosen_key_root
        self.params['is_major_original'] = is_major_key
        self.params['key_name_original'] = chosen_key_name
        self.params['active_key_root'] = self.params['key_root_original']
        self.params['active_is_major'] = self.params['is_major_original']
        print(f"Original Key: {self.params['key_name_original']}")

        structural_complexity_pref = self.user_params.get('structural_complexity', 'Standard')
        if structural_complexity_pref == "Simple":
            form_templates = [["Intro", "Verse", "Chorus", "Verse", "Chorus", "Outro"], ["Verse", "Chorus", "Verse", "Chorus", "Chorus", "Outro"]]
        elif structural_complexity_pref == "Developed":
            form_templates = [["Intro", "Verse", "PreChorus", "Chorus", "Verse", "PreChorus", "Chorus", "Bridge", "InstrumentalHook", "Chorus", "Outro"], ["Intro", "Verse", "PreChorus", "Chorus", "Verse", "PreChorus", "Chorus", "Bridge", "Chorus", "Chorus", "Outro"]]
        else: # Standard
            form_templates = [["Intro", "Verse", "PreChorus", "Chorus", "Verse", "PreChorus", "Chorus", "Bridge", "Chorus", "Outro"], ["Intro", "Verse", "Chorus", "Verse", "Chorus", "InstrumentalHook", "Chorus", "Outro"]]
        self.params['song_form'] = random.choice(form_templates)

        schemas = {"I-V-vi-IV": ([0, 7, 9, 5], "Classic Pop/Rock"), "vi-IV-I-V": ([9, 5, 0, 7], "Singer/Songwriter/Ballad"), "I-vi-IV-V": ([0, 9, 5, 7], "Doo-wop/Oldies"), "IV-V-vi-I": ([5, 7, 9, 0], "Modern Pop/Hopscotch")}
        schema_choice = "I-V-vi-IV"
        if mood == "MelancholySentimental" and random.random() < 0.7: schema_choice = "vi-IV-I-V"
        elif mood == "UpliftingEnergetic" and random.random() < 0.6: schema_choice = "IV-V-vi-I"
        elif primary_genre == "Ballad": schema_choice = "vi-IV-I-V"
        elif primary_genre == "RetroSynthwave" and random.random() < 0.5: schema_choice = random.choice(["I-V-vi-IV", "vi-IV-I-V"])
        else: schema_choice = random.choice(list(schemas.keys()))
        self.params['harmonic_schema_name'] = schema_choice
        self.params['harmonic_schema_progression_degrees'], self.params['harmonic_schema_feel'] = schemas[self.params['harmonic_schema_name']]
        print(f"Harmonic Schema: {self.params['harmonic_schema_name']}")

        harmonic_richness_pref = self.user_params.get('harmonic_richness', 'Some7ths')
        if harmonic_richness_pref == "TriadsOnly": self.params['use_7th_chords_probability'] = 0.0
        elif harmonic_richness_pref == "Some7ths": self.params['use_7th_chords_probability'] = 0.4
        elif harmonic_richness_pref == "Mostly7ths": self.params['use_7th_chords_probability'] = 0.8
        else: self.params['use_7th_chords_probability'] = 0.4

        if primary_genre == "HipHopGroove": self.params['rhythm_personality'] = "HipHopGroove"
        elif primary_genre == "EDMPulse": self.params['rhythm_personality'] = "EDMPulse"
        elif primary_genre == "RetroSynthwave": self.params['rhythm_personality'] = "EDMPulse"
        elif primary_genre == "Ballad": self.params['rhythm_personality'] = "PopRock"
        else: self.params['rhythm_personality'] = "PopRock"
        print(f"Rhythm Personality: {self.params['rhythm_personality']}")
        
        instrumentation_focus = self.user_params.get('instrumentation_focus', 'Balanced')
        self.params['instrumentation_focus'] = instrumentation_focus

        self.params['instruments'] = { "Drums": None }
        bass_instr = random.choice([33, 34, 38]); chords_instr = random.choice([0, 4, 88]); melody_instr = random.choice([80, 25, 52]); pad_instr = random.choice([89, 90, 92])
        if self.params['rhythm_personality'] in ["HipHopGroove", "EDMPulse", "RetroSynthwave"]: bass_instr = random.choice([38, 39])
        if primary_genre == "Ballad": chords_instr = 0; melody_instr = random.choice([25, 40, 52]); pad_instr = random.choice([48, 89])
        elif primary_genre == "RetroSynthwave": chords_instr = random.choice([80,81,88,89]); melody_instr = random.choice([80,81,84]); pad_instr = random.choice([88,89,90,91,92])
        if instrumentation_focus == "PianoLed": chords_instr = 0
        elif instrumentation_focus == "SynthHeavy": chords_instr = random.choice([80,81,88,89]); melody_instr = random.choice([80,81,84]); pad_instr = random.choice([88,89,90,91,92])
        elif instrumentation_focus == "GuitarFocused": chords_instr = random.choice([24, 25]); melody_instr = random.choice([26, 27, 28, 29, 30])
        self.params['instruments']['Bass'] = bass_instr; self.params['instruments']['Chords'] = chords_instr; self.params['instruments']['Melody'] = melody_instr; self.params['instruments']['Pad'] = pad_instr
        if instrumentation_focus == "Minimalist": 
            self.params['instruments']['Pad'] = None
            if random.random() < 0.5: self.params['instruments']['Chords'] = None
        
        energy_level = self.user_params.get('energy_level', 3)
        if energy_level == 1: self.params['overall_dynamic_level'] = random.randint(55, 65)
        elif energy_level == 2: self.params['overall_dynamic_level'] = random.randint(65, 75)
        elif energy_level == 3: self.params['overall_dynamic_level'] = random.randint(75, 85)
        elif energy_level == 4: self.params['overall_dynamic_level'] = random.randint(85, 95)
        elif energy_level == 5: self.params['overall_dynamic_level'] = random.randint(95, 105)
        else: self.params['overall_dynamic_level'] = random.randint(75, 85)

        melodic_complexity_ui = self.user_params.get('melodic_complexity', 3)
        if melodic_complexity_ui <= 2: self.params['melodic_complexity_level'] = "Simple"
        elif melodic_complexity_ui >= 4: self.params['melodic_complexity_level'] = "Complex"
        else: self.params['melodic_complexity_level'] = "Moderate"
        print(f"Internal Melodic Complexity: {self.params['melodic_complexity_level']}")

        self.params['melody_generation_method'] = self.user_params.get('melody_generation_style', 'Standard')
        print(f"Melody Generation Method: {self.params['melody_generation_method']}")

        self.params['hook_on_downbeat_strong'] = True
        
        self.params['_get_scale_notes_func'] = self._get_scale_notes
        self.params['_build_chord_voicings_func'] = self._build_chord_voicings

    def _get_section_profile(self, section_type, base_dynamic_level):
        # ... (This method remains the same as v0.8.5)
        profile = {
            'velocity_base': base_dynamic_level, 'rhythmic_density_modifier': 1.0,
            'instrument_layers': ["Chords"], 'fills_enabled': False,
            'build_tension': False, 'is_peak_section': False, 'modulate_key': False,
            'allow_rhythmic_break': False, 'melody_style': 'standard'
        }
        primary_genre = self.params.get('primary_genre', 'ModernPop')
        instrumentation_focus = self.params.get('instrumentation_focus', 'Balanced')

        if primary_genre == "Ballad":
            profile['rhythmic_density_modifier'] *= 0.7
            base_dynamic_level = max(50, base_dynamic_level - 10)

        if section_type == "Intro":
            profile['velocity_base'] = max(40, base_dynamic_level - 35)
            profile['instrument_layers'] = random.choice([["Chords", "Pad"], ["Melody_Sparse", "Pad"], ["Chords"]])
            if instrumentation_focus == "Minimalist": profile['instrument_layers'] = [random.choice(["Chords", "Pad", "Melody_Sparse"])]
            profile['rhythmic_density_modifier'] *= 0.5
        elif section_type == "Verse":
            profile['velocity_base'] = max(50, base_dynamic_level - 25)
            profile['instrument_layers'] = ["Drums_Light", "Bass", "Chords", "Melody"]
            if random.random() < 0.4 and instrumentation_focus != "Minimalist": profile['instrument_layers'].append("Pad_Light")
            if instrumentation_focus == "Minimalist": profile['instrument_layers'] = ["Bass", "Melody"]
            profile['rhythmic_density_modifier'] *= 0.8; profile['fills_enabled'] = True
        elif section_type == "PreChorus":
            profile['velocity_base'] = max(55, base_dynamic_level - 20)
            profile['instrument_layers'] = ["Drums_Build", "Bass_Active", "Chords_Sustained_Cresc", "Melody_Rising", "Pad_Swell_Cresc"]
            if instrumentation_focus == "Minimalist": profile['instrument_layers'] = ["Drums_Build", "Bass_Active", "Melody_Rising"]
            profile['rhythmic_density_modifier'] *= 1.2; profile['build_tension'] = True; profile['fills_enabled'] = True
        elif section_type == "Chorus":
            profile['velocity_base'] = min(115, base_dynamic_level + 10)
            profile['instrument_layers'] = ["Drums_Full", "Bass_Driving", "Chords_Full", "Melody_Hook", "Pad_Full"]
            if random.random() < 0.5 and instrumentation_focus != "Minimalist": profile['instrument_layers'].append("CounterMelody_Simple")
            if instrumentation_focus == "Minimalist": profile['instrument_layers'] = ["Drums_Full", "Bass_Driving", "Melody_Hook"]
            profile['fills_enabled'] = True; profile['is_peak_section'] = True
        elif section_type == "InstrumentalHook":
            profile['velocity_base'] = min(110, base_dynamic_level + 5)
            profile['instrument_layers'] = ["Drums_Full", "Bass_Driving", "Chords_Full", "Melody_Hook", "Pad_Full"]
            if instrumentation_focus == "Minimalist": profile['instrument_layers'] = ["Drums_Full", "Bass_Driving", "Melody_Hook"]
            profile['fills_enabled'] = True; profile['is_peak_section'] = True; profile['allow_rhythmic_break'] = random.random() < 0.3
        elif section_type == "Bridge":
            profile['velocity_base'] = max(45, base_dynamic_level - 30)
            profile['modulate_key'] = random.random() < 0.5; profile['melody_style'] = 'bridge_distinct'
            if profile['modulate_key']:
                profile['instrument_layers'] = ["Drums_Light", "Bass", "Chords_Sustained", "Melody_Modulating", "Pad_Swell"]
            elif random.random() < 0.6:
                profile['instrument_layers'] = random.choice([["Chords_Sparse", "Pad"], ["Bass_Melodic", "Pad_Light"], ["Melody_Reflective"]])
            else:
                profile['instrument_layers'] = ["Drums_Light", "Bass", "Chords_Sustained", "Melody", "Pad_Swell"]
            if instrumentation_focus == "Minimalist" and not profile['modulate_key']:
                 profile['instrument_layers'] = [random.choice(["Melody_Reflective", "Chords_Sparse"])]
            profile['rhythmic_density_modifier'] *= (0.7 if profile['modulate_key'] else 0.6)
            profile['allow_rhythmic_break'] = random.random() < 0.2; profile['fills_enabled'] = True
        elif section_type == "Outro":
            profile['velocity_base'] = max(35, base_dynamic_level - 40)
            profile['rhythmic_density_modifier'] *= 0.5
            profile['instrument_layers'] = random.choice([["Chords_Fade", "Pad_Fade"], ["Melody_Sparse_Fade"], ["Chords_Fade"]])
            if instrumentation_focus == "Minimalist":  profile['instrument_layers'] = [random.choice(["Melody_Sparse_Fade", "Chords_Fade"])]
        if instrumentation_focus == "Minimalist":
            has_harmonic_or_melodic = any(s.startswith("Chords") or s.startswith("Melody") for s in profile['instrument_layers'])
            if not has_harmonic_or_melodic:
                if self.params['instruments'].get("Melody"): profile['instrument_layers'].append("Melody")
                elif self.params['instruments'].get("Chords"): profile['instrument_layers'].append("Chords")
        return profile

    def _get_scale_notes(self, root_note, is_major, scale_type="diatonic"):
        major_intervals = [0, 2, 4, 5, 7, 9, 11]; minor_intervals = [0, 2, 3, 5, 7, 8, 10]
        major_pentatonic_intervals = [0, 2, 4, 7, 9]; minor_pentatonic_intervals = [0, 3, 5, 7, 10]
        intervals = []
        if scale_type == "diatonic": intervals = major_intervals if is_major else minor_intervals
        elif scale_type == "major_pentatonic": intervals = major_pentatonic_intervals
        elif scale_type == "minor_pentatonic": intervals = minor_pentatonic_intervals
        else: intervals = major_intervals if is_major else minor_intervals
        return sorted([(root_note + i) % 12 for i in intervals])

    def _get_chord_notes_from_roman(self, roman_numeral_degree, key_root, is_major):
        scale_intervals = [0, 2, 4, 5, 7, 9, 11] if is_major else [0, 2, 3, 5, 7, 8, 10]
        chord_root_offset = scale_intervals[roman_numeral_degree % 7]
        actual_chord_root_note = key_root + chord_root_offset; triad_type = "major"
        if is_major:
            if roman_numeral_degree in [1, 2, 5]: triad_type = "minor"
            elif roman_numeral_degree == 6: triad_type = "diminished"
        else:
            if roman_numeral_degree in [0, 3, 4]: triad_type = "minor"
            elif roman_numeral_degree in [2, 5, 6]: triad_type = "major"
            elif roman_numeral_degree == 1: triad_type = "diminished"
        final_chord_type = triad_type
        if self.params.get('use_7th_chords_probability', 0.0) > random.random():
            if is_major:
                if roman_numeral_degree in [0, 3]: final_chord_type = "maj7"
                elif roman_numeral_degree in [1, 2, 5]: final_chord_type = "min7"
                elif roman_numeral_degree == 4: final_chord_type = "dom7"
                elif roman_numeral_degree == 6: final_chord_type = "min7b5"
            else:
                if roman_numeral_degree in [0,3,4]: final_chord_type = "min7"
                elif roman_numeral_degree in [2,5]: final_chord_type = "maj7"
                elif roman_numeral_degree == 1: final_chord_type = "min7b5"
                elif roman_numeral_degree == 6: final_chord_type = "dom7"
        return actual_chord_root_note, final_chord_type

    def _get_chord_progression_for_section(self, section_type, num_bars):
        key_root = self.params['active_key_root']; is_major = self.params['active_is_major']
        schema_degrees = self.params['harmonic_schema_progression_degrees']
        progression_tuples = []; beats_per_chord = 4
        if section_type == "Bridge" and self.params.get('bridge_is_modulating', False) and random.random() < 0.8:
            bridge_degrees = random.choice([[1, 4, 0], [3,4,0]])
            for bar in range(num_bars):
                degree = bridge_degrees[bar % len(bridge_degrees)]
                root_note, chord_type = self._get_chord_notes_from_roman(degree, key_root, is_major)
                progression_tuples.append((root_note, chord_type, beats_per_chord))
        else:
            for bar in range(num_bars):
                degree = schema_degrees[bar % len(schema_degrees)]
                root_note, chord_type = self._get_chord_notes_from_roman(degree, key_root, is_major)
                progression_tuples.append((root_note, chord_type, beats_per_chord))
        return progression_tuples

    def _build_chord_voicings(self, root_midi_note, chord_type, octave_center=4, num_notes_pref=3):
        root_pc = root_midi_note % 12; notes_pc = [root_pc]
        if "major" in chord_type or "maj" in chord_type or "dom" in chord_type : notes_pc.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        elif "minor" in chord_type or "min" in chord_type: notes_pc.extend([(root_pc + 3) % 12, (root_pc + 7) % 12])
        elif "dim" in chord_type: notes_pc.extend([(root_pc + 3) % 12, (root_pc + 6) % 12])
        else: notes_pc.extend([(root_pc + 4) % 12, (root_pc + 7) % 12])
        if "maj7" in chord_type: notes_pc.append((root_pc + 11) % 12)
        elif "min7" in chord_type and "b5" not in chord_type : notes_pc.append((root_pc + 10) % 12)
        elif "dom7" in chord_type: notes_pc.append((root_pc + 10) % 12)
        elif "min7b5" in chord_type or ("dim" in chord_type and "7" in chord_type): notes_pc = [root_pc, (root_pc + 3) % 12, (root_pc + 6) % 12, (root_pc + 10) % 12]
        notes_pc = sorted(list(set(notes_pc)))
        base_octave_root = root_midi_note
        if base_octave_root < 36: base_octave_root = (octave_center * 12) + root_pc
        voiced_notes = [base_octave_root]
        for interval_note_pc in notes_pc[1:]: voiced_notes.append(base_octave_root + ((interval_note_pc - (base_octave_root % 12) + 12) % 12))
        if len(voiced_notes) > num_notes_pref and ("7" in chord_type or "b5" in chord_type):
            if num_notes_pref == 3 and len(voiced_notes) >=3:
                third_approx = base_octave_root + 3 if "min" in chord_type or "dim" in chord_type else base_octave_root + 4
                seventh_approx = base_octave_root + 10 if "min7" in chord_type or "dom7" in chord_type or "min7b5" in chord_type else base_octave_root + 11
                selected_voicing = [base_octave_root]
                for n in voiced_notes:
                    if n % 12 == third_approx % 12 and n not in selected_voicing: selected_voicing.append(n); break
                for n in voiced_notes:
                    if n % 12 == seventh_approx % 12 and n not in selected_voicing: selected_voicing.append(n); break
                if len(selected_voicing) < num_notes_pref: voiced_notes = sorted(list(set(voiced_notes)))[:num_notes_pref]
                else: voiced_notes = sorted(list(set(selected_voicing)))[:num_notes_pref]
            else: voiced_notes = sorted(list(set(voiced_notes)))[:num_notes_pref]
        else: voiced_notes = sorted(list(set(voiced_notes)))[:num_notes_pref]
        return voiced_notes

    def _get_drum_fill_pattern(self, fill_type="standard_snare_roll", rhythm_personality="PopRock"):
        if fill_type == "standard_snare_roll":
            return [(38, 1.0, 0.25), (38, 0.75, 0.25), (38, 0.5, 0.25), (38, 0.25, 0.25)]
        elif fill_type == "tom_roll_simple":
             return [(48, 1.0, 0.33), (45, 0.66, 0.33), (41, 0.33, 0.33)]
        elif fill_type == "hiphop_stutter_snare" and rhythm_personality == "HipHopGroove":
            return [(40, 1.0, 0.125), (22, 0.875, 0.125), (40, 0.75, 0.125), (22, 0.625, 0.125),
                    (40, 0.5, 0.125), (22, 0.375, 0.125), (40, 0.25, 0.125)]
        elif fill_type == "edm_noise_sweep" and rhythm_personality == "EDMPulse":
            return [(46, 1.0, 0.25), (46, 0.75, 0.25), (46, 0.5, 0.25), (46, 0.25, 0.25)]
        elif fill_type == "kick_and_cymbal_transition":
            return [(36, 1.0, 0.5), (49, 0.5, 0.5)]
        elif fill_type == "sparse_tom_accent":
            return [(45, 0.5, 0.25), (41, 0.25, 0.25)]
        elif fill_type == "syncopated_snare_pop":
            return [(38, 1.0, 0.25), (38, 0.5, 0.25)]
        return [(38, 1.0, 0.25), (38, 0.75, 0.25)]

    def _add_drum_pattern(self, track_num, start_time_beats, num_bars, section_type, section_profile):
        base_velocity = section_profile['velocity_base']
        is_build = section_profile['build_tension']; is_peak = section_profile['is_peak_section']
        fills_enabled = section_profile['fills_enabled']; rhythm_personality = self.params['rhythm_personality']
        allow_rhythmic_break = section_profile.get('allow_rhythmic_break', False)

        if rhythm_personality == "HipHopGroove": kick, snare, closed_hh, open_hh = 35, 40, 22, 26
        elif rhythm_personality == "EDMPulse": kick, snare, closed_hh, open_hh = 36, 38, 42, 46
        else: kick, snare, closed_hh, open_hh = 36, 38, 42, 46
        crash, ride = 49, 51
        
        if self.params['primary_genre'] == "Ballad":
            if random.random() < 0.4: return

        for bar_idx in range(num_bars):
            bar_start = start_time_beats + bar_idx * 4
            current_bar_overall_velocity = base_velocity
            if is_build:
                progression_in_prechorus = bar_idx / num_bars if num_bars > 0 else 0
                current_bar_overall_velocity = int(base_velocity + (15 * progression_in_prechorus))
                current_bar_overall_velocity = min(115, current_bar_overall_velocity)
            
            if allow_rhythmic_break and bar_idx == num_bars // 2 and num_bars > 2:
                if random.random() < 0.5: 
                    print(f"    Drum break in {section_type} at bar {bar_idx+1}")
                    if random.random() < 0.7: 
                        self.midi_obj.addNote(track_num, 9, crash, bar_start, 2, current_bar_overall_velocity -10)
                    continue # Correctly indented to skip the rest of the bar

            kick_vel = min(127, current_bar_overall_velocity + 5)
            snare_vel = min(127, current_bar_overall_velocity + 10)
            hat_vel = max(30, current_bar_overall_velocity - (25 if self.params['primary_genre'] == "Ballad" else 20) )

            if rhythm_personality == "EDMPulse":
                for i in range(4): self.midi_obj.addNote(track_num, 9, kick, bar_start + i, 0.5, kick_vel)
                self.midi_obj.addNote(track_num, 9, snare, bar_start + 1, 0.5, snare_vel)
                self.midi_obj.addNote(track_num, 9, snare, bar_start + 3, 0.5, snare_vel)
                for i in range(8):
                    if i % 2 == 1: self.midi_obj.addNote(track_num, 9, closed_hh, bar_start + i * 0.5, 0.25, hat_vel)
            elif rhythm_personality == "HipHopGroove":
                self.midi_obj.addNote(track_num, 9, kick, bar_start + 0, 0.5, kick_vel)
                if random.random() < 0.6: self.midi_obj.addNote(track_num, 9, kick, bar_start + random.choice([0.75, 1.5, 1.75]), 0.25, current_bar_overall_velocity)
                self.midi_obj.addNote(track_num, 9, snare, bar_start + 1, 0.5, snare_vel)
                self.midi_obj.addNote(track_num, 9, kick, bar_start + 2, 0.5, kick_vel if random.random() < 0.7 else current_bar_overall_velocity)
                if random.random() < 0.4: self.midi_obj.addNote(track_num, 9, kick, bar_start + random.choice([2.5, 2.75, 3.5]), 0.25, current_bar_overall_velocity)
                self.midi_obj.addNote(track_num, 9, snare, bar_start + 3, 0.5, snare_vel)
                for i in range(16):
                    if random.random() < (0.5 if is_build else 0.3):
                         self.midi_obj.addNote(track_num, 9, closed_hh if random.random() < 0.8 else open_hh, bar_start + i * 0.25, 0.125, hat_vel - random.randint(0,5))
            else: 
                self.midi_obj.addNote(track_num, 9, kick, bar_start + 0, 1, kick_vel)
                self.midi_obj.addNote(track_num, 9, snare, bar_start + 1, 1, snare_vel)
                self.midi_obj.addNote(track_num, 9, kick, bar_start + 2, 1, kick_vel)
                self.midi_obj.addNote(track_num, 9, snare, bar_start + 3, 1, snare_vel)
                hat_subdivision = 0.5
                if self.params['primary_genre'] == "Ballad": hat_subdivision = 1.0 
                elif is_build and (bar_idx >= num_bars / 2 if num_bars > 0 else False): hat_subdivision = 0.25
                elif is_peak or section_profile['rhythmic_density_modifier'] > 1.0 : hat_subdivision = 0.25
                if hat_subdivision > 0:
                    for i in range(int(4 / hat_subdivision)):
                        if self.params['primary_genre'] == "Ballad" and random.random() < 0.6 and section_type == "Verse": continue
                        hat_note = closed_hh if self.params['primary_genre'] != "Ballad" else random.choice([ride, closed_hh])
                        if is_build and i % (int(1/hat_subdivision) * 2) == (int(1/hat_subdivision) * 2 -1) and random.random() < 0.3: hat_note = open_hh
                        self.midi_obj.addNote(track_num, 9, hat_note, bar_start + i * hat_subdivision, hat_subdivision, hat_vel)
            if is_peak and bar_idx % 4 == 0 : self.midi_obj.addNote(track_num, 9, crash, bar_start, 2, min(127, current_bar_overall_velocity + 15))
            if fills_enabled and bar_idx == num_bars - 1 and random.random() < 0.85:
                fill_options = ["standard_snare_roll", "tom_roll_simple", "kick_and_cymbal_transition", "syncopated_snare_pop"]
                if rhythm_personality == "HipHopGroove": fill_options.append("hiphop_stutter_snare")
                elif rhythm_personality == "EDMPulse": fill_options.append("edm_noise_sweep")
                elif self.params['primary_genre'] == "Ballad": fill_options = ["sparse_tom_accent", "kick_and_cymbal_transition"]
                fill_pattern_name = random.choice(fill_options); fill_notes = self._get_drum_fill_pattern(fill_pattern_name, rhythm_personality)
                fill_bar_end_time = bar_start + 4; fill_vel = min(127, current_bar_overall_velocity + 10)
                for note_val, offset_from_end, duration in fill_notes: self.midi_obj.addNote(track_num, 9, note_val, fill_bar_end_time - offset_from_end, duration, fill_vel)
                if fill_notes: self.midi_obj.addNote(track_num, 9, crash, fill_bar_end_time - 0.01, 0.5, fill_vel + 5)
            elif fills_enabled and (bar_idx + 1) % 4 == 0 and bar_idx < num_bars -1 and random.random() < (0.15 if self.params['primary_genre'] == "Ballad" else 0.35) :
                fill_options = ["sparse_tom_accent", "syncopated_snare_pop"]
                if rhythm_personality != "EDMPulse": fill_options.append("standard_snare_roll")
                fill_notes = self._get_drum_fill_pattern(random.choice(fill_options), rhythm_personality)
                fill_bar_end_time = bar_start + 4; fill_vel = current_bar_overall_velocity
                for note_val, offset_from_end, duration in fill_notes:
                    if offset_from_end <= 2.0 : self.midi_obj.addNote(track_num, 9, note_val, fill_bar_end_time - offset_from_end, duration, fill_vel)

    def _add_bass_line(self, track_num, chord_prog, start_time_beats, section_type, section_profile):
        base_velocity = section_profile['velocity_base']
        is_build = section_profile['build_tension']; is_peak = section_profile['is_peak_section']
        key_root, is_major = self.params['active_key_root'], self.params['active_is_major']
        scale_notes_pc = self._get_scale_notes(key_root, is_major, "diatonic")
        rhythm_personality = self.params['rhythm_personality']; primary_genre = self.params['primary_genre']
        current_beat = start_time_beats; total_section_duration_beats = sum(d for _,_,d in chord_prog) if chord_prog else 1
        for i, (root_midi, chord_type, duration_beats) in enumerate(chord_prog):
            current_note_overall_velocity = base_velocity
            if is_build: progression_in_build = (current_beat - start_time_beats) / total_section_duration_beats if total_section_duration_beats > 0 else 0; current_note_overall_velocity = int(base_velocity + (15 * progression_in_build)); current_note_overall_velocity = min(110, current_note_overall_velocity)
            bass_octave_root = root_midi - 12
            if bass_octave_root < 24: bass_octave_root += 12
            chord_tones_for_bass = self._build_chord_voicings(root_midi, chord_type, octave_center=2, num_notes_pref=3)
            if is_peak and section_type == "Chorus" and primary_genre not in ["Ballad", "RetroSynthwave"]:
                step_duration = 0.5; num_steps = int(duration_beats / step_duration) if step_duration > 0 else 1
                for step_idx in range(num_steps):
                    note_to_play = bass_octave_root
                    if step_idx % 2 == 1 and len(chord_tones_for_bass) > 1 and random.random() < 0.4: note_to_play = chord_tones_for_bass[1] if chord_tones_for_bass[1] < 60 else bass_octave_root
                    note_velocity = min(127, current_note_overall_velocity + (5 if step_idx % (int(1/step_duration)*2 if step_duration > 0 else 1) == 0 else 0))
                    self.midi_obj.addNote(track_num, track_num, note_to_play, current_beat + step_idx * step_duration, step_duration - 0.02, note_velocity)
            elif primary_genre == "Ballad": self.midi_obj.addNote(track_num, track_num, bass_octave_root, current_beat, duration_beats - 0.1, current_note_overall_velocity)
            else:
                step_duration = 0.5
                if rhythm_personality == "EDMPulse" and is_peak: step_duration = 0.25
                elif rhythm_personality == "HipHopGroove": step_duration = random.choice([0.5, 1.0])
                num_steps = int(duration_beats / step_duration) if step_duration > 0 else 1
                if num_steps == 0: num_steps = 1
                last_bass_note_val = None
                for step_idx in range(num_steps):
                    beat_in_chord = current_beat + step_idx * step_duration; actual_step_duration = step_duration
                    if beat_in_chord + actual_step_duration > current_beat + duration_beats: actual_step_duration = (current_beat + duration_beats) - beat_in_chord
                    if actual_step_duration <= 0.05: continue
                    note_to_play = bass_octave_root; note_velocity = current_note_overall_velocity
                    if step_idx == 0: note_velocity = min(127, current_note_overall_velocity + 5)
                    if rhythm_personality == "HipHopGroove" and random.random() < 0.4 and step_idx == 0:
                        note_to_play = bass_octave_root - 12 if bass_octave_root >=36 else bass_octave_root
                        self.midi_obj.addNote(track_num, track_num, note_to_play, beat_in_chord, duration_beats - 0.1, note_velocity); break
                    elif step_idx == 0: note_to_play = bass_octave_root
                    elif random.random() < 0.6:
                        options = [ct for ct in chord_tones_for_bass if ct >= 24 and ct < 60]
                        if not options: options = [bass_octave_root]
                        if last_bass_note_val is not None and random.random() < 0.4:
                            target_chord_tone = random.choice(options); diff = target_chord_tone - last_bass_note_val
                            if abs(diff) > 1 and abs(diff) <=4 :
                                step_dir = 1 if diff > 0 else -1; passing_note_pc = (last_bass_note_val + step_dir) % 12
                                if passing_note_pc in scale_notes_pc:
                                    possible_passing_notes = [n for n in range(last_bass_note_val + step_dir, target_chord_tone, step_dir) if n%12 == passing_note_pc]
                                    if possible_passing_notes: note_to_play = random.choice(possible_passing_notes)
                        else: note_to_play = random.choice(options)
                    if note_to_play < 24: note_to_play += 12
                    if note_to_play > 60 : note_to_play -=12
                    self.midi_obj.addNote(track_num, track_num, note_to_play, beat_in_chord, actual_step_duration - 0.02, note_velocity)
                    last_bass_note_val = note_to_play
            current_beat += duration_beats

    def _add_chord_instrument(self, track_num, chord_prog, start_time_beats, num_bars_in_section, section_type, section_profile, is_pad_role=False):
        base_velocity = section_profile['velocity_base'] - (10 if is_pad_role else 0)
        is_build = section_profile['build_tension']; octave_center = 5 if is_pad_role else 4
        sustain_factor = 0.98 if is_pad_role else 0.95
        if is_pad_role and section_type == "Outro": sustain_factor = 2.5
        current_beat = start_time_beats; total_duration_of_section_beats = num_bars_in_section * 4
        for i, (root_midi, chord_type, duration_beats) in enumerate(chord_prog):
            current_note_overall_velocity = base_velocity
            progress_within_section = (current_beat - start_time_beats) / total_duration_of_section_beats if total_duration_of_section_beats > 0 else 0
            if is_build: current_note_overall_velocity = int(base_velocity + (20 * progress_within_section)); current_note_overall_velocity = min(100 if is_pad_role else 110, current_note_overall_velocity)
            elif section_type == "Outro": current_note_overall_velocity = int(base_velocity * (1 - progress_within_section * 0.8))
            num_notes_for_voicing = 3
            if self.params.get('use_7th_chords_probability', 0.0) > random.random() and ("7" in chord_type or "b5" in chord_type): num_notes_for_voicing = random.choice([3,4])
            if is_pad_role: num_notes_for_voicing = random.choice([2,3,4])
            chord_pitches = self._build_chord_voicings(root_midi, chord_type, octave_center=octave_center, num_notes_pref=num_notes_for_voicing)
            note_velocity_for_this_chord = current_note_overall_velocity
            if not is_build and not section_type == "Outro": note_velocity_for_this_chord = min(127, current_note_overall_velocity + (3 if is_pad_role else 5) )
            actual_sustain = duration_beats * sustain_factor
            if is_pad_role and random.random() < 0.5: actual_sustain = duration_beats + 0.1
            if is_build and not is_pad_role and random.random() < 0.6:
                num_pulses = int(duration_beats / 0.5) if duration_beats > 0 else 0
                for pulse in range(num_pulses):
                    for pitch in chord_pitches: self.midi_obj.addNote(track_num, track_num, pitch, current_beat + pulse * 0.5, 0.5 * sustain_factor, note_velocity_for_this_chord)
            else:
                for pitch in chord_pitches: self.midi_obj.addNote(track_num, track_num, pitch, current_beat, actual_sustain, note_velocity_for_this_chord)
            current_beat += duration_beats
            
    def _add_melody_line(self, track_num, chord_prog, start_time_beats, section_type, section_profile):
        method = self.params.get('melody_generation_method', 'Standard')
        print(f"    Using melody generation method: {method} for {section_type}")

        factory_params_for_melody = self.params.copy()
        factory_params_for_melody['_get_scale_notes_instance_method'] = self._get_scale_notes
        factory_params_for_melody['_build_chord_voicings_instance_method'] = self._build_chord_voicings
        # This provides access to UKHitFactory's instance methods for theory if needed by external generators.
        # External generators can call: factory_params_for_melody['_get_scale_notes_instance_method'](root, major, style)

        if method == "MarkovChain":
            print(f"    Markov Chain melody for {section_type} (Not Fully Implemented Yet, using Standard)")
            standard_generator.generate(self.midi_obj, track_num, chord_prog, start_time_beats, section_type, section_profile, factory_params_for_melody)
        elif method == "ContourDriven":
            contour_generator.generate(self.midi_obj, track_num, chord_prog, start_time_beats, section_type, section_profile, factory_params_for_melody)
        else: # Standard (Rule-Based & Motif)
            standard_generator.generate(self.midi_obj, track_num, chord_prog, start_time_beats, section_type, section_profile, factory_params_for_melody)

    def _generate_section_midi(self, section_type, current_time_beats, section_bars):
        print(f"  Generating MIDI for {section_type} ({section_bars} bars)")
        section_profile = self._get_section_profile(section_type, self.params['overall_dynamic_level'])
        self.params['bridge_is_modulating'] = False
        if section_type == "Bridge" and section_profile.get('modulate_key', False):
            self.params['bridge_is_modulating'] = True; modulation_target = random.choice([7, 5])
            self.params['active_key_root'] = (self.params['key_root_original'] + modulation_target) % 12
            self.params['active_is_major'] = self.params['is_major_original']
            print(f"    Modulating Bridge to key root {self.params['active_key_root']} ({'Major' if self.params['active_is_major'] else 'Minor'})")
        chord_prog = self._get_chord_progression_for_section(section_type, section_bars)
        if any(s.startswith("Drums") for s in section_profile['instrument_layers']): self._add_drum_pattern(self.track_map["Drums"], current_time_beats, section_bars, section_type, section_profile)
        if any(s.startswith("Bass") for s in section_profile['instrument_layers']): self._add_bass_line(self.track_map["Bass"], chord_prog, current_time_beats, section_type, section_profile)
        if any(s.startswith("Chords") for s in section_profile['instrument_layers']): self._add_chord_instrument(self.track_map["Chords"], chord_prog, current_time_beats, section_bars, section_type, section_profile, is_pad_role=False)
        if any(s.startswith("Melody") or s.startswith("CounterMelody") for s in section_profile['instrument_layers']): self._add_melody_line(self.track_map["Melody"], chord_prog, current_time_beats, section_type, section_profile)
        if any(s.startswith("Pad") for s in section_profile['instrument_layers']): self._add_chord_instrument(self.track_map["Pad"], chord_prog, current_time_beats, section_bars, section_type, section_profile, is_pad_role=True)
        extra_pause_beats = 0
        if section_type == "PreChorus" and random.random() < 0.7:
            extra_pause_beats = random.choice([1, 2])
            if extra_pause_beats > 0: print(f"    Adding {extra_pause_beats} beats of silence after PreChorus.")
        if self.params.get('bridge_is_modulating', False):
            self.params['active_key_root'] = self.params['key_root_original']
            self.params['active_is_major'] = self.params['is_major_original']
            self.params['bridge_is_modulating'] = False
            print(f"    Reverted key to original {self.params['key_name_original']} after Bridge.")
        return section_bars * 4 + extra_pause_beats

    def compose(self):
        print(f"Composing '{self.song_title}'...")
        self.params['active_key_root'] = self.params['key_root_original']
        self.params['active_is_major'] = self.params['is_major_original']
        for key in list(self.params.keys()): 
            if key.endswith("_motif") or key.endswith("_used_once"): del self.params[key]
        for track_name, track_num in self.track_map.items():
            self.midi_obj.addTrackName(track_num, 0, track_name)
            if track_name != "Drums" and track_name in self.params['instruments'] and self.params['instruments'].get(track_name) is not None:
                self.midi_obj.addProgramChange(track_num, track_num, 0, self.params['instruments'][track_name])
        current_total_time_beats = 0
        max_beats = (self.params['target_duration_seconds'] / 60) * self.params['bpm']
        section_bar_lengths = {}
        structural_complexity_pref = self.user_params.get('structural_complexity', 'Standard')
        for section_name_in_form in set(self.params['song_form']):
            if section_name_in_form in ["Intro", "Outro"]: section_bar_lengths[section_name_in_form] = random.choice([2,4] if structural_complexity_pref == "Simple" else [4, 8])
            elif section_name_in_form == "Bridge" or section_name_in_form == "InstrumentalHook": section_bar_lengths[section_name_in_form] = random.choice([4,8])
            else:
                if structural_complexity_pref == "Simple": section_bar_lengths[section_name_in_form] = random.choice([8,12])
                elif structural_complexity_pref == "Developed": section_bar_lengths[section_name_in_form] = random.choice([12,16,20])
                else: section_bar_lengths[section_name_in_form] = random.choice([8, 12, 16])
        for i, section_type in enumerate(self.params['song_form']):
            if current_total_time_beats >= max_beats: print("Max duration reached."); break
            section_bars = section_bar_lengths[section_type]
            duration_beats_of_section = self._generate_section_midi(section_type, current_total_time_beats, section_bars)
            current_total_time_beats += duration_beats_of_section
        print(f"Composition complete. Total beats: {current_total_time_beats}, Approx duration: {current_total_time_beats / self.params['bpm'] * 60:.2f}s")

    def save_midi(self, filename=None):
        if filename is None: filename = f"{self.song_title.replace(' ', '_')}.mid"
        with open(filename, "wb") as output_file:
            self.midi_obj.writeFile(output_file)
        print(f"MIDI file saved as {filename}")

if __name__ == "__main__":
    test_user_params = {
        'seed': random.randint(0,1000000), 
        'primary_genre': 'ModernPop', 
        'mood': 'UpliftingEnergetic', 
        'energy_level': 4,
        'tempo_preference': 'Medium', 
        'song_length': 'Radio', 
        'structural_complexity': 'Standard',
        'melodic_complexity': 3, 
        'harmonic_richness': 'Some7ths', 
        'instrumentation_focus': 'Balanced',
        'melody_generation_style': 'ContourDriven'
    }
    print(f"Using test_user_params for local test: {test_user_params}")
    hit_generator = UKHitFactory(user_params=test_user_params)
    hit_generator.compose()
    hit_generator.save_midi()