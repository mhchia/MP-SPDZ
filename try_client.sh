make bankers-bonus-client.x

./compile.py bankers_bonus 1
NUM_PARTIES=2
Scripts/setup-ssl.sh $NUM_PARTIES
Scripts/setup-clients.sh $NUM_PARTIES
PLAYERS=$NUM_PARTIES Scripts/semi.sh bankers_bonus-1 &
echo "1"
./bankers-bonus-client.x 0 $NUM_PARTIES 100 0 &
echo "2"
./bankers-bonus-client.x 1 $NUM_PARTIES 200 0 &
echo "3"
./bankers-bonus-client.x 2 $NUM_PARTIES 50 1
