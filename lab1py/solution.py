import getopt
import sys


class Node:
    def __init__(self, parent, state, cost):
        self.parent = parent
        self.state = state
        self.cost = cost

    def expand(self, succ):
        children = []
        for i in succ[self.state]:
            children.append(Node(self, i.split(",")[0], self.cost + float(i.split(",")[1])))
        return children


opened = []
closed = []
visited_states = []


def main(argv):
    global opened
    global closed
    global visited_states
    algorithm = ''
    state_descriptor = ''
    heuristic_descriptor = ''
    check_optimistic = False
    check_consistent = False
    try:
        opts, args = getopt.getopt(argv, "h", ["alg=", "ss=", "h=", "check-optimistic", "check-consistent"])
    except getopt.GetoptError:
        print('solution.py')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('solution.py')
            sys.exit()
        elif opt == "--alg":
            algorithm = arg
        elif opt == "--ss":
            state_descriptor = arg
        elif opt == "--h":
            heuristic_descriptor = arg
        elif opt == "--check-optimistic":
            check_optimistic = True
        elif opt == "--check-consistent":
            check_consistent = True

    init, succ, goal = read_state_descriptor(state_descriptor)

    if algorithm != "":
        n = None
        if algorithm == "bfs":
            print("# BFS")
            n = bfs(init, succ, goal)
        elif algorithm == "ucs":
            print("# UCS")
            n = ucs(init, succ, goal)
        elif algorithm == "astar":
            print(f'# A-STAR {heuristic_descriptor}')
            h = read_heuristic_descriptor(heuristic_descriptor)
            n = astar(init, succ, goal, h)
        else:
            print(f"Algorithm {algorithm} not supported.")
            sys.exit(1)
        if n:
            path = [n]
            parent = n.parent
            while parent:
                path.append(parent)
                parent = parent.parent
            path.reverse()
            print("[FOUND_SOLUTION]: yes")
            print(f"[STATES_VISITED]: {len(closed)}")
            print(f"[PATH_LENGTH]: {len(path)}")
            print(f"[TOTAL_COST]: {n.cost:.1f}")
            root = path[0]
            print(f"[PATH]: {root.state}", end="")
            for node in path:
                if node != root:
                    print(f" => {node.state}", end="")
            print()
        else:
            print("[FOUND_SOLUTION]: no")

    elif check_optimistic:
        print(f"# HEURISTIC-OPTIMISTIC {heuristic_descriptor}")
        h = read_heuristic_descriptor(heuristic_descriptor)
        ok = True
        for state in sorted(h):
            opened = []
            closed = []
            visited_states = []
            predicted_cost = float(h[state])
            n = ucs(state, succ, goal)
            if n:
                true_cost = n.cost
                if predicted_cost <= true_cost:
                    print(f"[CONDITION]: [OK] h({state}) <= h*: {predicted_cost:.1f} <= {true_cost:.1f}")
                else:
                    print(f"[CONDITION]: [ERR] h({state}) <= h*: {predicted_cost:.1f} <= {true_cost:.1f}")
                    ok = False
            else:
                raise Exception(f"Can't find a solution from {state}")
        if ok:
            print("[CONCLUSION]: Heuristic is optimistic.")
        else:
            print("[CONCLUSION]: Heuristic is not optimistic.")

    elif check_consistent:
        print(f"# HEURISTIC-CONSISTENT {heuristic_descriptor}")
        h = read_heuristic_descriptor(heuristic_descriptor)
        ok = True
        for current_state in sorted(h):
            current_h = float(h[current_state])
            for next_node in Node(None, current_state, 0).expand(succ):
                next_h = float(h[next_node.state])
                if current_h <= next_h + next_node.cost:
                    print(f"[CONDITION]: [OK] h({current_state}) <= h({next_node.state}) + c: {current_h} <= {next_h} + {next_node.cost}")
                else:
                    print(f"[CONDITION]: [ERR] h({current_state}) <= h({next_node.state}) + c: {current_h} <= {next_h} + {next_node.cost}")
                    ok = False
        if ok:
            print("[CONCLUSION]: Heuristic is consistent.")
        else:
            print("[CONCLUSION]: Heuristic is not consistent.")


def read_state_descriptor(file):
    with open(file) as f:
        init = None
        goal = None
        succ = {}
        for line in f.readlines():
            if line.startswith("#"):
                continue
            line = line.strip()
            if not init:
                init = line
                continue
            if not goal:
                goal = line.split()
                continue
            succ[line.split(":")[0]] = line.split(":")[1].split()
        return init, succ, goal


def read_heuristic_descriptor(file):
    h = {}
    with open(file) as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue
            line = line.strip()
            h[line.split(":")[0]] = line.split(":")[1]
    return h


def bfs(init, succ, goal):
    global opened
    global closed
    global visited_states
    opened.append(Node(None, init, 0))
    while len(opened) > 0:
        n = opened.pop(0)
        closed.append(n)
        visited_states.append(n.state)
        if n.state in goal:
            return n
        children = []
        for child in n.expand(succ):
            if child.state not in visited_states:
                children.append(child)
        opened = opened + sorted(children, key=lambda el: el.state)
    return None


def ucs(init, succ, goal):
    global opened
    global closed
    global visited_states
    opened.append(Node(None, init, 0))
    while len(opened) > 0:
        n = opened.pop(0)
        closed.append(n)
        visited_states.append(n.state)
        if n.state in goal:
            return n
        for child in n.expand(succ):
            if child.state not in visited_states:
                opened.append(child)
        opened.sort(key=lambda el: (el.cost, el.state))
    return None


def astar(init, succ, goal, h):
    global opened
    global closed
    opened.append(Node(None, init, 0))
    while len(opened) > 0:
        n = opened.pop(0)
        closed.append(n)
        if n.state in goal:
            return n
        opened_closed = opened + closed
        for child in n.expand(succ):
            if child.state in [el.state for el in opened_closed]:
                opened_closed_node = [el for el in opened_closed if el.state == child.state][0]
                if child.cost > opened_closed_node.cost:
                    continue
                else:
                    if opened_closed_node in closed:
                        closed.remove(opened_closed_node)
                    elif opened_closed_node in opened:
                        opened.remove(opened_closed_node)
                    else:
                        raise Exception("500 Internal error")
            opened.append(child)
        opened.sort(key=lambda el: (el.cost + float(h[el.state]), el.state))
    return None


if __name__ == "__main__":
    main(sys.argv[1:])
