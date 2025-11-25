#!/usr/bin/env python3
import sys
from .molecule_to_usdz_script import convert_molecule_to_usdz

def main():
    if len(sys.argv) < 2:
        print("Usage: convert_molecule_to_usdz input.pdb|input.xyz")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = convert_molecule_to_usdz(input_file)
    print(f"✅ Conversion complete: {output_file}")

if __name__ == "__main__":
    main()

