# MPCStats PoC

## Circuit
[bmi.mpc](./Programs/Source/bmi.mpc): Data Provider 0 provides (identity, height) and Data Provider 1 provides (identity, weight). The User wants to compute the average BMI of the two datasets by joining them on the identity.

## Summary
- Defining mpc computation with python
    - Should be able to support statistics operations easily
        - Fixed-points with arithmetic circuits supported
    - Can support the JOIN operation we want
        - Table (id, height) JOIN table (id, weight) on id
    - Can do 2 data providers + 1 user
- Easily switching between protocols like semi, mascot, etc.
- Rough benchmark
    - Protocol **semi** (semi-honest) is 12 times faster than **mascot** (dishonest)
    - Compile-time and run-time increases fast with the number of rows
        - 10 rows: compile-time 1s, run-time 7s
        - 100 rows: compile-time 42s, run-time 500s
        - 1000 rows: ?

## To-Dos
- [ ] Optimize the bmi example to decrease run-time
- [ ] Run the rest of protocols and see which is more suitable for our use case
- [ ] Confirm the program is correctly written and protocols are correctly used
    - [ ] Correctness: users can be convinced of the correctness of the computation
    - [ ] Privacy: users won't be able to learn the inputs

## How to run?

In the root of MP-SPDZ, compile the VM with the semi-honest settings
```bash
make -j8 semi-party.x
```

Compile the program `bmi` to bytecode
```bash
./compile.py -F 64 bmi
```

Generate testing data for Data Provider 0 and 1
```bash
python gen_data.py
```

In a new terminal, run Data Provider 0
```bash
./semi-party.x -N 3 -p 0 -pn 55781 -OF . bmi
```

In a new terminal, run Data Provider 1
```bash
./semi-party.x -N 3 -p 1 -pn 55781 -OF . bmi
```

In a new terminal, run User (Data Consumer)
```bash
./semi-party.x -N 3 -p 2 -pn 55781 -OF . bmi
```

## Run on different hosts
Have a file containing the IP addresses of the hosts in this format. First line is the IP address of party 0, second line is the IP address of party 1, and so on. For example, we have a file `hosts` with the following content with 2 parties:
```
18.183.238.119:3000
43.207.105.60:3000
```

For the party0, run
```bash
./semi-party.x -N 2 -p 0  -OF . bmi -ip hosts
```

For the party1, run
```bash
./semi-party.x -N 2 -p 1  -OF . bmi -ip hosts
```
