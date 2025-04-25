import numpy as np
import librosa
import pretty_midi
import soundfile as sf
import os

def convert_poly(input_audio, output_midi, bpm=None):
    """
    Convert polyphonic audio to MIDI using librosa for multiple pitch detection.
    Supports WAV and MP3 formats.
    
    Args:
        input_audio (str): Path to input audio file (WAV or MP3)
        output_midi (str): Path to output MIDI file
        bpm (float, optional): Beats per minute for the MIDI file. If None, no tempo is set.
    """
    # Load audio file using librosa which supports multiple formats
    audio, sr = librosa.load(input_audio, sr=None)
    
    # Convert to mono if needed
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Extract harmonic content
    harmonic, _ = librosa.effects.hpss(audio)
    
    # Perform Constant-Q Transform
    hop_length = 512
    C = np.abs(librosa.cqt(harmonic, sr=sr, hop_length=hop_length))
    
    # Frame timing
    times = librosa.times_like(C, sr=sr, hop_length=hop_length)
    
    # Create a MIDI object with optional BPM
    if bpm is not None:
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    else:
        midi = pretty_midi.PrettyMIDI()  # No tempo specified
        
    piano = pretty_midi.Instrument(program=0)  # Piano
    
    # Detect onsets for note segmentation
    onset_env = librosa.onset.onset_strength(y=harmonic, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    
    # Get the duration between consecutive onsets
    durations = np.diff(np.append(onset_times, len(audio) / sr))
    
    # For each onset
    for i, onset_time in enumerate(onset_times):
        # Get the frame index
        frame_idx = np.argmin(np.abs(times - onset_time))
        
        # Get the spectrum at this frame
        magnitudes = C[:, frame_idx]
        
        # Find peaks in the CQT spectrum (potential notes)
        peaks, _ = librosa.util.peak_pick(magnitudes, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
        
        # Convert peak indices to MIDI notes
        for peak in peaks:
            # CQT bins correspond to semitones, with bin 0 = C1 (MIDI note 24)
            midi_note = peak + 24
            
            # Only add reasonably loud notes (relative to the max in this frame)
            if magnitudes[peak] > 0.1 * np.max(magnitudes):
                note = pretty_midi.Note(
                    velocity=int(min(127, 50 + 77 * (magnitudes[peak] / np.max(magnitudes)))),
                    pitch=int(midi_note),
                    start=onset_time,
                    end=onset_time + durations[i]
                )
                piano.notes.append(note)
    
    # Add the instrument to the MIDI object
    midi.instruments.append(piano)
    
    # Write the MIDI file
    midi.write(output_midi)