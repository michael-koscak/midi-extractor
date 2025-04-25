import argparse
from modes import mono, poly, drums

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input audio file (WAV or MP3)")
    parser.add_argument("output", help="Output MIDI file")
    parser.add_argument("--mode", choices=["mono", "poly", "drums"], required=True, help="Mode of conversion")
    parser.add_argument("--bpm", type=float, help="Set specific BPM (beats per minute) for the MIDI file")
    args = parser.parse_args()

    if args.mode == "mono":
        mono.convert_mono(args.input, args.output, bpm=args.bpm)
    elif args.mode == "poly":
        poly.convert_poly(args.input, args.output, bpm=args.bpm)
    elif args.mode == "drums":
        drums.convert_drums(args.input, args.output, bpm=args.bpm)

if __name__ == "__main__":
    main()