import numpy as np
import librosa
import pretty_midi
import soundfile as sf
import os

def convert_drums(input_audio, output_midi):
    """
    Convert drum audio to MIDI by detecting onsets in different frequency bands.
    Supports WAV and MP3 formats.
    
    Args:
        input_audio (str): Path to input audio file (WAV or MP3)
        output_midi (str): Path to output MIDI file
    """
    # Load the audio file using librosa which supports multiple formats
    audio, sr = librosa.load(input_audio, sr=None)
    
    # Convert to mono if needed
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Extract percussive content
    _, percussive = librosa.effects.hpss(audio)
    
    # Define frequency bands for different drum elements
    # These ranges are approximate and may need adjustment
    bands = {
        "kick": (20, 200),       # MIDI note 36
        "snare": (200, 1200),    # MIDI note 38
        "hi-hat": (1200, 8000),  # MIDI note 42 (closed hi-hat)
    }
    
    # Create a MIDI object
    midi = pretty_midi.PrettyMIDI()
    drum_track = pretty_midi.Instrument(program=0, is_drum=True)
    
    # Process each band separately
    for drum_name, (low_freq, high_freq) in bands.items():
        # Filter the audio to the specific frequency band
        y_band = librosa.effects.preemphasis(percussive)
        
        # Low-pass filter for kick
        if drum_name == "kick":
            y_band = librosa.effects.low_pass(y_band, sr, high_freq)
        # Band-pass filter for snare
        elif drum_name == "snare":
            y_band = librosa.effects.high_pass(y_band, sr, low_freq)
            y_band = librosa.effects.low_pass(y_band, sr, high_freq)
        # High-pass filter for hi-hat
        elif drum_name == "hi-hat":
            y_band = librosa.effects.high_pass(y_band, sr, low_freq)
        
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=y_band, sr=sr)
        
        # Detect onsets with different thresholds per instrument
        threshold = {
            "kick": 0.5,
            "snare": 0.4,
            "hi-hat": 0.3
        }
        
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env, 
            sr=sr, 
            threshold=threshold[drum_name]
        )
        
        # Convert frames to time
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        
        # Map drum names to MIDI notes
        drum_midi_map = {
            "kick": 36,    # Bass Drum
            "snare": 38,   # Acoustic Snare
            "hi-hat": 42,  # Closed Hi-Hat
        }
        
        # Create notes for each onset
        for onset_time in onset_times:
            # Get the intensity at this time for velocity
            frame_index = librosa.time_to_frames(onset_time, sr=sr)
            if frame_index < len(onset_env):
                velocity = int(min(127, 60 + 67 * (onset_env[frame_index] / np.max(onset_env))))
            else:
                velocity = 100
                
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=drum_midi_map[drum_name],
                start=onset_time,
                end=onset_time + 0.1  # Short duration for drums
            )
            drum_track.notes.append(note)
    
    # Add the drum track to the MIDI object
    midi.instruments.append(drum_track)
    
    # Write the MIDI file
    midi.write(output_midi)