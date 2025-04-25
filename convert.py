import argparse
from modes import mono, poly, drums

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input audio file (WAV preferred)")
    parser.add_argument("output", help="Output MIDI file")
    parser.add_argument("--mode", choices=["mono", "poly", "drums"], required=True, help="Mode of conversion")
    args = parser.parse_args()

    if args.mode == "mono":
        mono.convert_mono(args.input, args.output)
    elif args.mode == "poly":
        poly.convert_poly(args.input, args.output)
    elif args.mode == "drums":
        drums.convert_drums(args.input, args.output)

if __name__ == "__main__":
    main()

