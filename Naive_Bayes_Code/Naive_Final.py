import pretty_midi
import numpy as np
import random
import os
from tabulate import tabulate



def extract_lefthand_notes(filename):

    midi_data = pretty_midi.PrettyMIDI(filename)

    left_hand_notes = []
    for instrument in midi_data.instruments:
        # print(instrument)
        # if instrument.is_drum or not instrument.name.startswith('Piano'):
        #     continue    
        for note in instrument.notes:
            if note.pitch < 60:                     # Assuming left-hand notes are lower than C4
                left_hand_notes.append(note.pitch)


    # Create the chord dictionary
    chord_dict = {}
    for i in range(len(left_hand_notes) - 2):
        chord = tuple(left_hand_notes[i:i+3])
        if chord not in chord_dict:
            chord_dict[chord] = len(chord_dict)

    # Print the chord dictionary
    return chord_dict


def notes_played_by_right_hand(chord_dict,unique_keys_in_piano):

    foldername = os.path.join(os.getcwd(),"tschai")
    midi_files = [f for f in os.listdir(foldername) if f.endswith(".mid")]

    # Initialize the note count matrix
    num_chords = len(chord_dict)
    num_notes = unique_keys_in_piano
    note_count = np.zeros((num_chords, num_notes))



    # Extract the right-hand notes and chords

    for midi_file in midi_files:
        midi_data = pretty_midi.PrettyMIDI(os.path.join(foldername,midi_file))
        left_hand_notes = []
        right_hand_notes = []

        for instrument in midi_data.instruments:
            # if instrument.is_drum or not instrument.name.startswith('Piano'):
            #     continue
            for note in instrument.notes:
                if note.pitch < 60:
                    left_hand_notes.append(note.pitch)

                else:
                    right_hand_notes.append(note.pitch)    
        
        
        for i in range(len(left_hand_notes) - 2):
            chord = tuple(left_hand_notes[i:i+3])
            if chord in chord_dict:
                chord_label = chord_dict[chord]
                for note in right_hand_notes:
                    
                    note_count[chord_label, note - 21] += 1  # Assuming A0 is the 21st n
                    
    # Normalize the note count matrix to obtain the probability matrix
    note_prob = note_count / np.sum(note_count, axis=1, keepdims=True)

    # Print the note probability matrix
    return note_prob



def generate_music(chord_dict, note_prob, no_of_char):
    # new_midi_data = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)

    chords = list(chord_dict.keys())
    # print(len(chords))

    current_chord = random.choice(chords)
    right_hand_notes = []
    # print(current_chord)

    for i in range(no_of_char):
        note_dist = note_prob[chord_dict[current_chord]]
        
        note_dist /= np.sum(note_dist)
        
        note = np.random.choice(range(88), p=note_dist)
        
        right_hand_notes.append(note)
        
        current_chord = random.choice(chords)



    midi_data = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)

    # Add the right-hand notes to the piano instrument

    for i, note in enumerate(right_hand_notes):
        start_time = i * 0.5  # assuming 120 BPM and 16th notes
        end_time = start_time + 0.5
        velocity = 100  # assuming a constant velocity
        midi_note = pretty_midi.Note(velocity=velocity, pitch=note + 21, start=start_time, end=end_time)
        piano.notes.append(midi_note)


        midi_data.instruments.append(piano)
        midi_data.write('generated_music.mid') 

    print("Music generated successfully.")       


def print_matrix(matrix):
    headers = [f"Column {i+1}" for i in range(matrix.shape[1])]
    table = tabulate(matrix, headers=range(88), tablefmt="fancy_grid")
    # print(table)


midi_files = [f for f in os.listdir(os.path.join(".", "tschai")) if f.endswith(".mid")]
ind = random.randint(0, len(midi_files)-1)
# chord_dict = extract_lefthand_notes("./tschai/ty_dezember.mid")
chord_dict = extract_lefthand_notes(os.path.join(".", "tschai", midi_files[ind]))
note_prob = notes_played_by_right_hand(chord_dict,88)

# print_matrix(note_prob)
# print(note_prob)

generate_music(chord_dict, note_prob, no_of_char = 100)