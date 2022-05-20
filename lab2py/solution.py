import os
import sys


def main(argv):
    keyword = argv[0]
    if keyword == "resolution":
        do_resolution(argv[1])
    elif keyword == "cooking":
        do_cooking(argv[1], argv[2])
    else:
        print("solution.py resolution|cooking clauses_file commands_file")
        sys.exit(2)


def add_to_recipe(file, clause):
    with open(file, "r") as f:
        lines = f.readlines()
    lines.append(f"{clause}\n")
    with open(file, "w") as f:
        f.writelines(lines)


def remove_from_recipe(file, clause):
    with open(file, "r") as f:
        lines = f.readlines()
    lines.remove(f"{clause}\n")
    with open(file, "w") as f:
        f.writelines(lines)


def do_cooking(clauses_file, commands_file):
    temp_file = "clauses.temp"
    with open(clauses_file, "r") as f:
        lines = f.readlines()
    with open(temp_file, "w") as f:
        f.writelines(lines)

    with open(commands_file, "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        clause = line[:-2]
        command = line[-1]
        if command == "?":
            add_to_recipe(temp_file, clause)
            print()
            do_resolution(temp_file)
            remove_from_recipe(temp_file, clause)
        elif command == "+":
            add_to_recipe(temp_file, clause)
        elif command == "-":
            remove_from_recipe(temp_file, clause)
    os.remove(temp_file)


def do_resolution(clauses_file):
    premise_clauses, goal_clauses, original_goal = read_clauses(clauses_file)
    lines = []  # lines to print
    premise_goal_clauses = premise_clauses.union(goal_clauses)
    for clause in premise_clauses:
        lines.append((clause, "/"))  # "/" indicates non derived clause
    for clause in goal_clauses:
        lines.append((clause, "/"))

    premise_clauses = remove_redundant(premise_clauses)

    deductions = {}  # dictionary for logging deductions
    conclusion = refutation_resolution(premise_clauses, goal_clauses, deductions)
    if conclusion:
        # finding path from NIL to non derived clauses
        deduction_path = []
        queue = [""]
        while len(queue) > 0:
            clause = queue.pop(0)
            clausei = deductions[clause][0]
            clausej = deductions[clause][1]
            deduction_path.insert(0, (clause, clausei, clausej))
            if clausei not in premise_goal_clauses:
                queue.append(clausei)
            if clausej not in premise_goal_clauses:
                queue.append(clausej)
        lines += deduction_path
        # printing solution
        divider_printed = False
        i = 0
        for line in lines:
            i += 1
            if line[1] == "/":
                print(f"{str(i)}. {printing_format(line[0])}")
            else:
                if not divider_printed:
                    print("===============")
                    divider_printed = True
                print(f"{str(i)}. {printing_format(line[0])} "
                      f"({find_number(lines, line[2])}, {find_number(lines, line[1])})")
        print("===============")
        print(f"[CONCLUSION]: {printing_format(original_goal)} is true")
    else:
        print(f"[CONCLUSION]: {printing_format(original_goal)} is unknown")


def find_number(lines, clause):
    for i in range(len(lines)):
        if clause == lines[i][0]:
            return i + 1
    return -1


def negate(unit):
    if unit.startswith("~"):
        return unit[1:]
    return "~" + unit


def internal_format(line):
    units = line.strip().lower().split(' v ')
    return ",".join(units)


def printing_format(clause):
    if clause == "":
        return "NIL"
    return " v ".join(clause.split(","))


def is_tautology(clause):
    clause_set = set(clause.split(","))
    for unit in clause_set:
        if negate(unit) in clause_set:
            return True
    return False


def read_clauses(file):
    lines = []
    original_goal = ""
    with open(file, "r") as f:
        for line in f.readlines():
            if not line.startswith("#"):
                lines.append(line)
    premise_clauses = set()
    goal_clauses = set()
    for i in range(len(lines)):
        clause = internal_format(lines[i])
        if i != len(lines) - 1:
            premise_clauses.add(clause)
        else:
            original_goal = clause
            for unit in clause.split(","):
                unit = unit.strip()
                goal_clauses.add(negate(unit))
    return premise_clauses, goal_clauses, original_goal


def remove_redundant(clauses):
    optimized_clauses = set()
    for clausei in clauses:
        optimized_clauses.add(clausei)
        for clausej in clauses:
            if clausej == clausei:
                continue
            if set(clausej.split(",")).issubset(set(clausei.split(","))):
                optimized_clauses.remove(clausei)
                break
    return optimized_clauses


def resolve(clausei, clausej):
    clausei_set = set(clausei.split(","))
    clausej_set = set(clausej.split(","))
    for uniti in clausei_set:
        if negate(uniti) in clausej_set:
            clausei_set.remove(uniti)
            clausej_set.remove(negate(uniti))
            resolved_clause = ",".join(clausei_set.union(clausej_set))  # empty if resolved to NIL
            if is_tautology(resolved_clause):
                break
            else:
                return resolved_clause
    return "/"  # "/" indicates no resolving is done


def refutation_resolution(premises, goals, deductions):
    deduced = set()
    visited = {}  # dict of: clause: [clause1, clause2, ...]
    while True:
        for clausei in goals:
            if clausei not in visited.keys():
                visited[clausei] = []
            for clausej in premises.union(goals):
                if clausei == clausej or clausej in visited[clausei]:
                    continue
                visited[clausei].append(clausej)
                resolved_clause = resolve(clausei, clausej)
                if resolved_clause != "/":
                    deductions[resolved_clause] = (clausei, clausej)
                    if len(resolved_clause) == 0:
                        return True
                    else:
                        deduced.add(resolved_clause)
        if deduced.issubset(premises.union(goals)):
            return False
        goals = goals.union(deduced)


if __name__ == "__main__":
    main(sys.argv[1:])
