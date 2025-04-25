# Audio-to-MIDI Converter

This utility converts audio files (WAV and MP3) to MIDI using different extraction techniques for monophonic melodies, polyphonic content, and drum patterns.

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install numpy librosa soundfile pretty_midi crepe pydub
```

## Usage

The utility provides three modes of operation:

```bash
python convert.py input_audio.[wav|mp3] output.mid --mode [mono|poly|drums]
```

### Modes

- **mono**: Extracts a single melody line from the audio (best for vocal melodies, solo instruments)
- **poly**: Extracts polyphonic content like chords and multiple simultaneous notes
- **drums**: Extracts drum patterns by analyzing different frequency bands

### Examples

Convert a vocal recording to a MIDI melody:
```bash
python convert.py vocals.wav vocals.mid --mode mono
```

Extract chords from a piano recording (MP3 format):
```bash
python convert.py piano.mp3 piano.mid --mode poly
```

Extract a drum pattern:
```bash
python convert.py drums.wav drums.mid --mode drums
```

## How It Works

- **Monophonic Mode**: Uses CREPE (Convolutional Representation for Pitch Estimation) for accurate pitch tracking of a single melodic line.
- **Polyphonic Mode**: Uses Constant-Q Transform and onset detection to identify multiple simultaneous notes.
- **Drums Mode**: Analyzes different frequency bands to detect kick drum, snare, and hi-hat patterns.

## Limitations

- The converter works best with clean audio recordings
- Results may vary depending on the complexity and quality of the input audio
- The system currently uses fixed thresholds that might need adjustment for different recordings

## Future Improvements

- Add more drum detection categories (toms, cymbals, etc.)
- Improve polyphonic extraction accuracy
- Add a graphical user interface
- Add output MIDI customization options (instrument selection, quantization)