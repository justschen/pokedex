# Pokedex App

A simple Pokédex application built with Python and Tkinter that allows users to search for Pokémon by their number and view their images.

## Features

- Search for Pokémon by number (1-1025).
- Navigate through Pokémon images using Previous and Next buttons.
- Copy Pokémon images to your local machine.

## Requirements

- Python 3.x
- `requests`
- `Pillow`

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd pokedex-app
   ```

2. Install the required packages:

   ```bash
   pip install -r src/requirements.txt
   ```

## Running the Application

To run the application, execute the following command:

```bash
python src/app.py
```

## Packaging

To package the application as a standalone executable, you can use tools like `PyInstaller`. 

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Create the executable:

   ```bash
   pyinstaller --onefile src/app.py
   ```

The executable will be created in the `dist` folder.

## License

This project is licensed under the MIT License.