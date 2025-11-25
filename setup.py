from setuptools import setup, find_packages

setup(
    name="molecule-to-usdz",          # Unique PyPI name
    version="0.1.0",
    author="Alexei A. Kananenka",
    author_email="akanane@udel.edu",
    description="Convert PDB/XYZ molecules to USDZ via Blender",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kananenka-group/MoleculeToUSDZ",  # Optional
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "ase>=3.24.0",
        "numpy>=1.25.2",
    ],
    entry_points={
        "console_scripts": [
            "convert-molecule-to-usdz = molecule_to_usdz.convert:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
    ],
)

