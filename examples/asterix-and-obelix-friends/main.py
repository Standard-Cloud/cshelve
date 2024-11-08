"""
This example demonstrates the flexibility of the database by dealing with types and entries around the theme of Asterix and Obelix.
Here is the initial structure of the database:
{
    'gaule': ['Adrénaline', 'Amérix', ...],
    'rome': ['Anglaigus', 'Caius Obtus', ...],
    'new_friends': {}
}
And here is the structure of the database after adding 'Cléopâtre' and 'Numérobis' from 'Egypte' and 'Chipolata' from 'Corse':
{
    'gaule': ['Adrénaline', 'Amérix', ...],
    'rome': ['Anglaigus', 'Caius Obtus', ...],
    'new_friends': {
        'cléopâtre': 'egypte',
        'numérobis': 'egypte',
        'chipolata': 'corse'
    },
    'egypte': ['cléopâtre', 'numérobis'],
    'corse': ['chipolata']
}

How to use it:
1. Install the necessary package: pip install -r requirements.txt
2. Run the program: python3 main.py mydb
"""
import cshelve
import sys

# Some Gaulois and Romans are added at the startup.
GAULOIS_KEY = "gaule"
ROMANS_KEY = "rome"
# This key will contain new friends added to simplify dictionary operations.
NEW_FRIENDS_KEY = "new_friends"

# Open the database based on the program parameter.
db = cshelve.open(sys.argv[1], "n")

# Load the Gaulois.
if GAULOIS_KEY not in db:
    with open("./gaulois.txt", "r") as fd:
        # Lowercase the names to simplify the comparison.
        # Remove empty strings.
        db[GAULOIS_KEY] = [p.lower() for p in fd.read().split("\n") if p]

# Load the Romans.
if ROMANS_KEY not in db:
    with open("./romans.txt", "r") as fd:
        # Lowercase the names to simplify the comparison.
        # Remove empty strings.
        db[ROMANS_KEY] = [p.lower() for p in fd.read().split("\n") if p]

# Add the default key to simplify dictionary parsing.
if NEW_FRIENDS_KEY not in db:
    db[NEW_FRIENDS_KEY] = {}

print("Enter 'end' to finish our adventure.")

while True:
    # Remove potential '\n' and unnecessary spaces.
    personnage = input("Enter the name of the character: ").strip().lower()

    if not personnage:
        continue

    # If the character is a Gaulois, print a custom message.
    if personnage in db[GAULOIS_KEY]:
        print("A true Gaulois par Toutatis!")
    # If the character is a Roman, print a custom message.
    elif personnage in db[ROMANS_KEY]:
        print("A Roman!")
    # End of the loop.
    elif personnage == "end":
        break
    # This character was added by the user.
    # Let's retrieve where he/she is from and display it.
    elif _from := db[NEW_FRIENDS_KEY].get(personnage):
        print(f"{personnage} is a true {_from}")
    # Unknown character, let's add it to the DB.
    else:
        _from = (
            input(f"I don't know {personnage}, where is he/she from? ").strip().lower()
        )
        # Unknown location.
        if _from not in db:
            db[_from] = [personnage]
        # Some characters are already from this location, we want to keep them too.
        else:
            db[_from] += [personnage]
        print("Thanks for this new friend!")
        # Add the new friend to the nested dict to simplify the parsing.
        db[NEW_FRIENDS_KEY] = {**db[NEW_FRIENDS_KEY], personnage: _from}

# Display friends and where they are from.
for _from, personages in db.items():
    if NEW_FRIENDS_KEY == _from:
        continue
    print(f"Here are friend(s) from {_from.capitalize()}:")
    for p in personages:
        print(f"- {p.capitalize()}")

db.close()
