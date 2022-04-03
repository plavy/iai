import sys


def main(argv):
    keyword = ''
    clauses_file = ''
    commands_file = ''

    if len(argv) > 0:
        keyword = argv[0]
        if keyword == "resolution":
            clauses_file = argv[1]
        elif keyword == "cooking":
            clauses_file = argv[1]
            commands_file = argv[2]
        else:
            print("First argument should be one of the following: [resolution, cooking]")
            sys.exit(2)
    else:
        print("First argument should be one of the following: [resolution, cooking]")
        sys.exit(2)
    premise_clauses, goal_clauses, original_goal = read_clauses(clauses_file)
    lines = []
    premise_goal_clauses = premise_clauses.union(goal_clauses)
    for clause in premise_clauses:
        lines.append((clause, "/"))
    for clause in goal_clauses:
        lines.append((clause, "/"))

    deductions = {}
    conclusion = refutation_resolution(premise_clauses, goal_clauses, deductions)
    if conclusion:
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

        divider_printed = False
        i = 0
        for line in lines:
            i += 1
            if line[1] == "/":
                print(f"{str(i)}. {unformat(line[0])}")
            else:
                if not divider_printed:
                    print("===============")
                    divider_printed = True
                print(f"{str(i)}. {unformat(line[0])} ({unformat(line[1])}, {unformat(line[2])})")
        print("===============")
        print(f"[CONCLUSION]: {unformat(original_goal)} is true")


def negate(unit):
    if unit.startswith("~"):
        return unit[1:]
    return "~" + unit


def unformat(clause):
    if clause == "":
        return "NIL"
    return " v ".join(clause.split(","))


def read_clauses(file):
    lines = []
    original_goal = ""
    with open(file) as f:
        for line in f.readlines():
            if not line.startswith("#"):
                lines.append(line)
    premise_clauses = set()
    goal_clauses = set()
    for i in range(len(lines)):
        clause = ""
        units = lines[i].strip().lower().split('v')
        if i != len(lines) - 1:
            for unit in units:
                unit = unit.strip()
                if len(clause) != 0:
                    clause += ","
                clause += unit
            premise_clauses.add(clause)
        else:
            original_goal = ",".join(units)
            for unit in units:
                unit = unit.strip()
                goal_clauses.add(negate(unit))
    return premise_clauses, goal_clauses, original_goal


def resolve(clausei, clausej):
    clausei_set = set(clausei.split(","))
    clausej_set = set(clausej.split(","))
    for uniti in clausei_set:
        if negate(uniti) in clausej_set:
            clausei_set.remove(uniti)
            clausej_set.remove(negate(uniti))
            return ",".join(clausei_set.union(clausej_set))
    return "/"


def refutation_resolution(premises, goals, deductions):
    deduced = set()
    visited = {}
    while True:
        for clausei in goals:
            if clausei not in visited.keys():
                visited[clausei] = []
            print("Checking for:", clausei)
            for clausej in premises.union(goals):
                if clausei == clausej or clausej in visited[clausei]:
                    continue
                visited[clausei].append(clausej)
                resolved_clause = resolve(clausei, clausej)
                deductions[resolved_clause] = (clausei, clausej)
                if len(resolved_clause) == 0:
                    return True
                if resolved_clause != "/":
                    print("Resolved:", resolved_clause, "from", clausei, clausej)
                    deduced.add(resolved_clause)
        if deduced.issubset(premises.union(goals)):
            return False
        goals = goals.union(deduced)


if __name__ == "__main__":
    main(sys.argv[1:])
