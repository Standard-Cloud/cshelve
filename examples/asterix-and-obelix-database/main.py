""""
This application is a simple database for the Asterix and Obelix comic series. It allows you to add new users to the database and dump the current users in the database.

How to use:
    python main.py <database-configuration> dump|save|clear
"""
import sys

import cshelve


# Open the database configuration.
with cshelve.open(sys.argv[1], writeback=True) as db:
    # Create the 'users' key if it doesn't exist.
    if "users" not in db:
        db["users"] = []

    # Check the command.
    if sys.argv[2] == "dump":
        # Print all the users in the database.
        for user in db["users"]:
            print(f"{user['name']} {user['insertion-number']}")
    elif sys.argv[2] == "save":
        # Add new users to the database.
        try:
            while user := input():
                user = user.strip()
                db["users"].append(
                    {"name": user, "insertion-number": len(db["users"]) + 1}
                )
            db.sync()
        except EOFError:
            # Catch the EOFError exception when the user presses Ctrl+D.
            ...
    elif sys.argv[2] == "clear":
        # Clear the database.
        db["users"] = []
    else:
        print("Par toutatis, I don't know that command!")
