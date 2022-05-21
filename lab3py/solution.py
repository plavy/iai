import os
import sys
import math


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
    m = max(values, key=values.get)
    for el in values:
        if values[el] == values[m] and el < m:
            m = el
    return m


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


def max_ig(dataset, features, label):
    initial_e = 0
    for el in values_of(dataset, label):
        prob = len(dataset_filter(dataset, label, el)) / len(dataset)
        if not prob == 0:
            initial_e -= prob * math.log2(prob)
    igs = dict()
    for feature in features:
        igs[feature] = initial_e
        for feature_value in values_of(dataset, feature):
            share = len(dataset_filter(dataset, feature, feature_value)) / len(dataset)
            sub_dataset = dataset_filter(dataset, feature, feature_value)
            for label_value in values_of(sub_dataset, label):
                prob = len(dataset_filter(sub_dataset, label, label_value)) / len(sub_dataset)
                if not prob == 0:
                    igs[feature] += share * prob * math.log2(prob)
    m = max(igs, key=igs.get)
    for el in igs:
        if igs[el] == igs[m] and el < m:
            m = el
    return m


class ID3:
    root_node: Node = None
    print_lines = list()

    def create_tree(self, dataset, parent_dataset, features, label):
        if len(dataset) == 0:
            v = most_frequent_value(parent_dataset, label)
            return Node(label_value=v)
        v = most_frequent_value(dataset, label)
        if len(features) == 0 or not dataset_has_other_than(dataset, label, v):
            return Node(label_value=v)
        x = max_ig(dataset, features, label)
        new_features = features.copy()
        new_features.remove(x)
        subtrees = list()
        for v in values_of(dataset, x):
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

    def fit(self, dataset, parent_dataset, features, label):
        self.root_node = self.create_tree(dataset, parent_dataset, features, label)
        print('[BRANCHES]:')
        self.generate_tree(self.root_node, 1, "")
        for el in self.print_lines:
            print(el)

    def predict_single(self, node, example):
        if node.label_value:
            return node.label_value
        for el in node.subtrees:
            if example[node.feature] == el[0]:
                return self.predict_single(el[1], example)

    def predict(self, dataset, features, label):
        correct = 0
        matrix = [[0 for i in range(len(values_of(dataset, label)))] for j in range(len(values_of(dataset, label)))]
        print("[PREDICTIONS]:", end=' ')
        for el in dataset:
            actual = el[label]
            prediction = self.predict_single(self.root_node, el)
            matrix[sorted(values_of(dataset, label)).index(actual)][sorted(values_of(dataset, label)).index(prediction)] += 1
            print(prediction, end=' ')
            if actual == prediction:
                correct += 1
        print()
        print('[ACCURACY]: %.5f' % round(correct / len(dataset), 5))
        print("[CONFUSION_MATRIX]:")
        for i in matrix:
            for j in i:
                print(j, end=' ')
            print()


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


def main(argv):
    if not len(argv) == 2:
        print("solution.py TRAIN_DATASET_FILE TEST_DATASET_FILE")
        sys.exit(2)
    train_file = argv[0]
    test_file = argv[1]
    dataset, features, label = read_dataset_file(train_file)
    model = ID3()
    model.fit(dataset, dataset, features, label)
    dataset, features, label = read_dataset_file(test_file)
    model.predict(dataset, features, label)


if __name__ == "__main__":
    main(sys.argv[1:])
