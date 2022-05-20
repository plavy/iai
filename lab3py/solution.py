import os
import sys


def main(argv):
    if not len(argv) == 2:
        print("solution.py TRAIN_DATASET TEST_DATASET")
        sys.exit(2)
    train_file = argv[0]
    test_file = argv[1]
    label, label_values = read_train_file(train_file)
    print(label, label_values)


def read_train_file(file):
    with open(file) as f:
        lines = f.readlines()
    label = ""
    label_values = set()
    for line in lines:
        line = line.strip()
        elements = line.split(",")
        if not label:
            label = elements[-1]
        else:
            label_values.add(elements[-1])
    return label, label_values


if __name__ == "__main__":
    main(sys.argv[1:])
