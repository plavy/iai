import os
import sys


class Node:
    def __init__(self, feature=None, subtrees=None, label_value=None):
        self.feature = feature
        self.subtrees = subtrees
        self.label_value = label_value


def values_of(dataset, key):
    values = set()
    for el in dataset:
        values.add(el[key])
    return values


def most_frequent_value(dataset, key):
    values = dict()
    for el in dataset:
        values[el[key]] = values.get(el[key]) + 1 if el[key] in values else 0
    return max(values, key=values.get)


def dataset_filter(dataset, key, value):
    new_dataset = list()
    for el in dataset:
        if el[key] == value:
            new_dataset.append(el)
    return new_dataset


def dataset_has_other_than(dataset, key, value):
    for el in dataset:
        if not el[key] == value:
            return True
    return False


class ID3:
    root_node: Node = None
    print_lines = list()

    def create_tree(self, dataset, parent_dataset, features, label):
        if len(dataset) == 0:
            v = most_frequent_value(parent_dataset, label)
            print(f"ended with {v}")
            return Node(label_value=v)
        v = most_frequent_value(dataset, label)
        if len(features) == 0 or not dataset_has_other_than(dataset, label, v):
            print(f"ended here with {v}")
            return Node(label_value=v)
        x = features[0]
        print(x)
        new_features = features.copy()
        new_features.remove(x)
        print(new_features)

        subtrees = list()
        for v in values_of(dataset, x):
            print(f'Going to {x}={v}')
            print(dataset_filter(dataset, x, v))
            t = self.create_tree(dataset_filter(dataset, x, v), dataset, new_features, label)
            subtrees.append((v, t))
        return Node(feature=x, subtrees=subtrees)

    def generate_tree(self, node, depth, path):
        if node.label_value:
            path += node.label_value
            self.print_lines.append(path)
            return
        for el in node.subtrees:
            new_path = path + f'{depth}:{node.feature}={el[0]} '
            self.generate_tree(el[1], depth + 1, new_path)
        return

    def print(self):
        print('[BRANCHES]:')
        self.generate_tree(self.root_node, 1, "")
        for el in self.print_lines:
            print(el)

    def fit(self, dataset, parent_dataset, features, label):
        self.root_node = self.create_tree(dataset, parent_dataset, features, label)


def main(argv):
    if not len(argv) == 2:
        print("solution.py TRAIN_DATASET_FILE TEST_DATASET_FILE")
        sys.exit(2)
    train_file = argv[0]
    test_file = argv[1]
    dataset, features, label = read_dataset_file(train_file)
    model = ID3()
    model.fit(dataset, dataset, features, label)
    model.print()


def read_dataset_file(file):
    with open(file) as f:
        lines = f.readlines()
    label = ""
    features = list()
    dataset = list()
    for line in lines:
        line = line.strip()
        elements = line.split(",")
        if not label:
            for el in elements:
                if not el == elements[-1]:
                    features.append(el)
                else:
                    label = el
        else:
            example = dict()
            for i in range(len(features)):
                example[features[i]] = elements[i]
            example[label] = elements[-1]
            dataset.append(example)
    return dataset, features, label


if __name__ == "__main__":
    main(sys.argv[1:])
