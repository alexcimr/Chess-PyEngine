
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

for dr, dc in directions:
    for i in range(4):
        dr += 1
    print(dr)