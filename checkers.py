from lib import between, sign, xy
from move import endMove, checkNextMove

def checkerJump(gm, pos1, pos2):
    x1, y1, x2, y2 = xy(pos1, pos2)
    dx = sign(x2 - x1)
    dy = sign(y2 - y1)
    if dx * (x2 - x1) != dy * (y2 - y1):
        return (-1, -1)
    if gm['field'][pos2] != '20':
        if not ((0 <= x2+dx < 8) and (0 <= y2+dy < 8)):
            return (-1, -1)
        pos2 += dx + dy * 8
        x2 += dx
    return (pos2, dx * (x2 - x1))

def promotion(gm, pos2, act):
    if pos2 // 8 == 7 * act:
        if gm['type'] == 'checkers':
            gm['field'][pos2] = str(act) + "d"
        else:
            gm['choice'] = 1
            return pos2
    return -1

def checkersMove(gm, pos1, pos2):
    pos2, n = checkerJump(gm, pos1, pos2)
    if pos2 == -1:
        return
    field = gm['field']
    act = gm['act']
    b = between(field, pos1, pos2)
    c = sum([field[p][0] == str(act) for p in b])
    k = [p for p in b if field[p][0] == str(1-act)]
    if c or (field[pos2] != '20'):
        return
    if (((n == 1 and (act == (pos2 > pos1))) or field[pos1][1] == "d")
        and not k and not gm['fix'] and not (gm['eat'] and gm['mustEat'][2])):
        field[pos2] = field[pos1]
        field[pos1] = '20'
        pos = promotion(gm, pos2, act)
        return endMove(gm, pos, 1 - act if pos == -1 else act)
    if ((len(k) == 1) and ((n == 2 and ((act == (pos2 > pos1)) or gm['eatBack'][2]))
                           or field[pos1][1] == "d")):
        return checkersEating(gm, pos1, pos2, act, k[0])

def checkersEating(gm, pos1, pos2, act, pos):
    field = gm['field']
    field[pos2] = field[pos1]
    field[pos] = '20'
    field[pos1] = '20'
    pos = promotion(gm, pos2, act)
    if pos != -1:
        return endMove(gm, pos, act)
    gm['fix'] = checkNextMove(gm, field, pos2, act)
    if gm['fix']:
        pos1 = pos2
    else:
        act = 1 - act
    return endMove(gm, pos1, act)