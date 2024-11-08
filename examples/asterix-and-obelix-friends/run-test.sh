echo "Note: This test is not cross-platform. It is intended to be run on Unix-like systems."
echo "But the application is cross-platform so you play with it even on Windows :)"
echo "Running Asterix and Obelix database test..."

python3 main.py azure-passwordless.ini < dataset.txt > /tmp/output.txt

diff --strip-trailing-cr expected-output.txt /tmp/output.txt
