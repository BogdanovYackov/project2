from lib import cellsBetween, between, xy
from move import endMove

def checkMove(gm, field, pos1, pos2, act):
    t = field[pos1][1]
    x1, y1, x2, y2 = xy(pos1, pos2)
    dx = x2 - x1
    dy = y2 - y1
    if (t == "h"):
        return (abs(dx), abs(dy)) in ((1, 2), (2, 1))
    if (t == "c"):
        return (abs(dx), abs(dy)) in ((1, 3), (3, 1))
    if between(field, pos1, pos2):
        return False
    if (t in "rq") and not (dx and dy):
        return True
    if (t in "bq") and (abs(dx) == abs(dy)):
        return True
    if (t == "l"):
        return (abs(dx) == 1) and (abs(dy) == 1)
    if (t == "k"):
        return (1 >= abs(dx)) and (1 >= abs(dy)) and not chessAttack(gm, pos2, 1 - act)
    if (t == "p") and (1 >= abs(dx)) and ((field[pos2] == '20' and gm['passant'][0] != pos2) == (dx == 0)):
        d = 2 * act - 1
        return (dy == d) or ((y1 in (1,6)) and (dx == 0) and (dy == 2 * d) and (field[pos1 + 8 * d] == '20'))

def castlingRecheck(gm, pos):
    for i in (0, 1):
        if pos - i * 56 in (0, 4):
            gm['castling'][2 * i] = 0
        if pos - i * 56 in (7, 4):
            gm['castling'][2 * i + 1] = 0

def recheckShah(gm, field, pos1, pos2, act):
    if gm['type'] == 'chess':
        var = field[pos2]
        field[pos2] = field[pos1]
        field[pos1] = '20'
        shah = chessAttack(gm, findKing(gm, act), 1 - act)
        field[pos1] = field[pos2]
        field[pos2] = var
        return shah

def checkAllMoves(gm, field, act):
    for pos1 in range(64):
        if field[pos1][0] == str(act):
            for pos2 in range(64):
                if ((field[pos2][0] != str(act)) and checkMove(gm, field, pos1, pos2, act)
                    and not recheckShah(gm, field, pos1, pos2, act)):
                    return True

def checkChessWin(gm, field, act):
    if gm['type'] == 'chess':
        checkShah(gm, 1 - act)
        if not checkAllMoves(gm, field, 1 - act):
            return f'win{int(act)}' if gm['highlight'][0] else 'draw'

def chessMove(gm, pos1, pos2):
    field = gm['field']
    act = gm['act']
    if checkMove(gm, field, pos1, pos2, act):
        if recheckShah(gm, field, pos1, pos2, act):
            return
        var = field[pos2]
        field[pos2] = field[pos1]
        field[pos1] = '20'
        if gm['type'] == 'chess':
            castlingRecheck(gm, pos1)
            castlingRecheck(gm, pos2)
            if gm['passant'][0] == pos2:
                field[pos2 - 8 + 16 * (pos2//8 == 2)] = '20'
        gm['choice'] = (field[pos2][1] == "p") and (pos2 // 8 == 7 * act)
        if (field[pos2][1] == "p") and (abs(pos2 - pos1) == 16):
            gm['passant'] = ((pos1 + pos2) // 2, act)
        if gm['choice']:
            return endMove(gm, pos2, act)
        return checkChessWin(gm, field, act) or endMove(gm, -1, 1 - act)

def chessAttack(gm, pos2, act):
    field = gm['field']
    var = field[pos2]
    field[pos2] = str(1 - act) + '0'
    res = [pos1 for pos1 in range(64) if ((field[pos1][0] == str(act))
                                          and checkMove(gm, field, pos1, pos2, act))]
    field[pos2] = var
    return res

def findKing(gm, act):
    for pos in range(64):
        if gm['field'][pos] == str(act) + "k":
            return pos

def checkShah(gm, act):
    if gm['type'] == 'chess':
        pos2 = findKing(gm, act)
        gm['highlight'][0] = set(chessAttack(gm, pos2, 1 - act))
        gm['highlight'][1] = set()
        for pos1 in gm['highlight'][0]:
            gm['highlight'][1] |= set(cellsBetween(pos1, pos2))
        if 'debug' not in gm:
            gm['debug'] = []
        gm['debug'] += gm['highlight']

def castling(gm, pos1, pos2, act):
    s = pos2 & 1
    check = not sum([bool(chessAttack(gm, p, 1 - act)) for p in cellsBetween(pos1, pos2)])
    if ((pos1 == 4 + 56 * (1 - act)) and (pos2 == 7 * s + 56 * (1 - act)) and check
        and gm['castling'][2 * act + s] and (not between(gm['field'], pos1, pos2))):
        gm['castling'][2 * act : 2 * act + 1] = [0, 0]
        gm['field'][pos2 + 1 - 2 * s] = gm['field'][pos1]
        gm['field'][pos2 + 2 - 4 * s] = gm['field'][pos2]
        gm['field'][pos1] = '20'
        gm['field'][pos2] = '20'
        endMove(gm, -1, 1 - act)
        return True