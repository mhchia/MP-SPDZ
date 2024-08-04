# Mean Age Example
## Installation
Clone the repo

```bash
cd ..
git clone https://github.com/mhchia/MP-SPDZ
cd MP-SPDZ
git checkout coscup-example
```

Build the MPC vm for `semi` protocol.

```bash
make setup
# Compile the VM for the `semi` protocol
make -j8 semi-party.x
# Make sure `semi-party.x` exists
ls semi-party.x
```

If you're on macOS and see the following linker warning, you can safely ignore it:

```bash
ld: warning: search path '/usr/local/opt/openssl/lib' not found
```

## Running the Example
Under the `MP-SPDZ` directory and make sure `Programs/Source/mean_age.mpc` exists.

```bash
ls Programs/Source/mean_age.mpc
```

Prepare input files for parties
```bash
# Create input file for party 0
echo 30 > Player-Data/Input-P0-0
# Create input file for party 1
echo 40 > Player-Data/Input-P1-0
# Create input file for party 2
echo 50 > Player-Data/Input-P2-0
```

Run all 3 parties in local machines
```bash
PLAYERS=3 ./Scripts/compile-run.py semi mean_age
```
