import crepe
import soundfile as sf
import pretty_midi
import librosa
import os

def convert_mono(input_audio, output_midi, bpm=None):
    """
    Convert monophonic audio to MIDI by tracking pitch using CREPE.
    Supports WAV and MP3 formats.
    
    Args:
        input_audio (str): Path to input audio file (WAV or MP3)
        output_midi (str): Path to output MIDI file
        bpm (float, optional): Beats per minute for the MIDI file. If None, no tempo is set.
    """
    # Use librosa to load the audio file regardless of format
    audio, sr = librosa.load(input_audio, sr=None)
    
    # CREPE pitch tracking
    time, frequency, confidence, _ = crepe.predict(audio, sr, viterbi=True)

    # Create MIDI object with optional BPM
    if bpm is not None:
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    else:
        midi = pretty_midi.PrettyMIDI()  # No tempo specified
        
    instrument = pretty_midi.Instrument(program=0)  # Piano by default

    # Convert detected pitches to MIDI notes
    notes = []
    current_note = None
    
    # Only consider frequencies with reasonable confidence
    confidence_threshold = 0.7
    
    for i, (t, f, c) in enumerate(zip(time, frequency, confidence)):
        if f > 0 and c >= confidence_threshold:
            pitch = int(round(pretty_midi.hz_to_midi(f)))
            
            # Start a new note or continue current note
            if current_note is None:
                current_note = {"pitch": pitch, "start": t, "end": t + 0.1}
            elif current_note["pitch"] == pitch:
                # Extend the current note
                current_note["end"] = t + 0.1
            else:
                # Finish current note and start a new one
                notes.append(current_note)
                current_note = {"pitch": pitch, "start": t, "end": t + 0.1}
        elif current_note is not None:
            # End current note on silence or low confidence
            notes.append(current_note)
            current_note = None
    
    # Add the last note if it exists
    if current_note is not None:
        notes.append(current_note)
    
    # Create MIDI notes
    for note_data in notes:
        # Only add notes of reasonable duration
        if note_data["end"] - note_data["start"] >= 0.05:
            note = pretty_midi.Note(
                velocity=100,
                pitch=note_data["pitch"],
                start=note_data["start"],
                end=note_data["end"]
            )
            instrument.notes.append(note)

    midi.instruments.append(instrument)
    midi.write(output_midi)