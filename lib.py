def xy(pos1, pos2):
    x1 = pos1 % 8
    x2 = pos2 % 8
    y1 = pos1 // 8
    y2 = pos2 // 8
    return x1, y1, x2, y2

def sign(a):
    return -1 if (a < 0) else (1 if a else 0)

def cellsBetween(pos1, pos2):
    x1, y1, x2, y2 = xy(pos1, pos2)
    dx = sign(x2 - x1)
    dy = sign(y2 - y1)
    if dx * (y2 - y1) != dy * (x2 - x1):
        return []
    n = max(dx * (x2 - x1), dy * (y2 - y1))
    dp = dx + dy * 8
    return [(pos1 + i * dp) for i in range(1, n)]

def between(field, pos1, pos2):
    return [p for p in cellsBetween(pos1, pos2) if field[p] != '20']