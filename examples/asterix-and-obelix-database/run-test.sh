#!/bin/bash

echo "Note: This test is not cross-platform. It is intended to be run on Unix-like systems."
echo "But the application is cross-platform so you play with it even on Windows :)"
echo "Running Asterix and Obelix database test..."

run_test() {
    DB=$1

    echo "Running test for $DB..."

    echo "Insert Gaulois."
    cat ./datasets/gaulois.input.txt | python3 main.py $DB save

    echo "Ensure Gaulois are correctly saved."
    python3 main.py $DB dump > /tmp/gaulois.txt
    diff --strip-trailing-cr ./datasets/gaulois.output.txt /tmp/gaulois.txt

    addGauloisStatus=$?
    if [ $addGauloisStatus -ne 0 ]; then
        echo "Gaulois test failed."
        python3 main.py $DB clear
        exit 1
    fi
    echo "Gaulois correctly inserted."


    echo "Insert Romain."
    cat ./datasets/romains.input.txt | python3 main.py $DB save

    echo "Ensure Romains are correctly saved with Gaulois."
    python3 main.py $DB dump > /tmp/gaulois-and-romains.txt
    diff --strip-trailing-cr ./datasets/gaulois-and-romains.output.txt /tmp/gaulois-and-romains.txt

    addRomainStatus=$?
    if [ $addRomainStatus -ne 0 ]; then
        echo "Gaulois & Romain test failed."
        python3 main.py $DB clear
        exit 1
    fi
    echo "Gaulois and Romains are correctly inserted."


    echo "Insert Others."
    cat ./datasets/others.input.txt | python3 main.py $DB save

    echo "Ensure Others are correctly saved with Gaulois and Romains."
    python3 main.py $DB dump > /tmp/gaulois-and-romains-and-others.txt
    diff --strip-trailing-cr ./datasets/gaulois-and-romains-and-others.output.txt /tmp/gaulois-and-romains-and-others.txt

    addOthersStatus=$?
    if [ $addOthersStatus -ne 0 ]; then
        echo "Gaulois & Romain & Others test failed."
        python3 main.py $DB clear
        exit 1
    fi

    echo "Gaulois, Romains and Others are correctly inserted."

    python3 main.py $DB clear

    echo "Test for $DB passed."
}

DB=/tmp/asterix-and-obelix.db
run_test $DB

DB=./azure-passwordless.ini
run_test $DB

DB=./azure-compression.ini
run_test $DB

echo "All tests passed."
exit 0
