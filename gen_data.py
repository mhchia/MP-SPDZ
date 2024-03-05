from pathlib import Path


base_path = Path(__file__).parent / "Player-Data"


DATA_LENGTH = 10
NUM_PARTIES = 2

MIN_HEIGHT = 150
MIN_WEIGHT = 40
DELIMITER = " "


def create_data_for_party() -> None:
    identities = range(DATA_LENGTH)

    heights = range(MIN_HEIGHT, MIN_HEIGHT + DATA_LENGTH)
    weights = range(MIN_WEIGHT, MIN_WEIGHT + DATA_LENGTH)

    # data_0: (identity, height)
    # 0 1 2 3
    # 152 160 170 180
    data_path_for_party_0 = base_path / f"Input-P0-0"
    data_path_for_party_0.parent.mkdir(parents=True, exist_ok=True)
    with open(data_path_for_party_0, "w") as f:
        f.write(DELIMITER.join(map(str, identities)) + "\n")
        f.write(DELIMITER.join(map(str, heights)) + "\n")

    # data_1: (identity, weight)
    # 0 1 2 3
    # 50 60 70 80
    data_path_for_party_1 = base_path / f"Input-P1-0"
    data_path_for_party_1.parent.mkdir(parents=True, exist_ok=True)
    with open(data_path_for_party_1, "w") as f:
        f.write(DELIMITER.join(map(str, identities)) + "\n")
        f.write(DELIMITER.join(map(str, weights)) + "\n")



if __name__ == "__main__":
    create_data_for_party()
    print("Data for parties created.")