# Asterix and Obelix Friends Database

This example demonstrates the flexibility of the database by dealing with types and entries around the theme of Asterix and Obelix.

## Database Structure

Here is the initial structure of the database:
```json
{
    "gaule": ["Adrénaline", "Amérix", ...],
    "rome": ["Anglaigus", "Caius Obtus", ...],
    "new_friends": {}
}
```

After adding 'Cléopâtre' and 'Numérobis' from 'Egypte' and 'Chipolata' from 'Corse', the structure becomes:
```json
{
    "gaule": ["Adrénaline", "Amérix", ...],
    "rome": ["Anglaigus", "Caius Obtus", ...],
    "new_friends": {
        "cléopâtre": "egypte",
        "numérobis": "egypte",
        "chipolata": "corse"
    },
    "egypte": ["cléopâtre", "numérobis"],
    "corse": ["chipolata"]
}
```

## Installation

1. Install the necessary package:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the program, use the following command:
```bash
python3 main.py <database-file>
```
- `<database-file>`: The path to the database file.

### Example

```bash
python3 main.py mydb
```

## How It Works

1. The script initializes the database with Gaulois and Romans if they are not already present.
2. It then enters a loop where the user can input character names.
3. If the character is a Gaulois or a Roman, a custom message is printed.
4. If the character is unknown, the user is prompted to provide the character's origin, which is then added to the database.

**Note:** This example does not include extensive error handling for clarity.

## Exiting

To exit the program, type `end` when prompted for a character name.
