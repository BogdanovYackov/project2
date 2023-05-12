def endMove(gm, pos1, act):
    field = gm['field']
    for a in (0, 1):
        if gm['type'] == 'checkers':
            if not sum([(x[0] == str(a)) for x in field]):
                return f'win{1 - a}'
        if gm['type'] == 'cheskers':
            if not sum([(x == f'{a}l') for x in field]):
                return f'win{1 - a}'
    if gm['act'] != act:
        if act == gm['passant'][1]:
            gm['passant'] = (-1, 2)
        pos1 = -1
        gm['act'] = act
        gm['fix'] = 0
        gm['choice'] = 0
        gm['eat'] = checkNextMoves(gm, field, act)
    gm['move'] = pos1

def checkNextMoves(gm, field, act):
    for pos in range(64):
        if ((field[pos][0] == str(act)) and (field[pos][1] in ("m", "d"))
            and checkNextMove(gm, field, pos, act)):
            return True

def checkNextMove(gm, field, pos, act):
    x2, y2 = pos%8, pos//8
    dirs = ((-1, -1), (1, -1), (-1, 1), (1, 1))
    if not (field[pos][1] == "d" or gm['eatBack'][2]):
        dirs = ((-1, 2*act-1), (1, 2*act-1))
    for dx, dy in dirs:
        dm = dx + 8 * dy
        for i in range(1, min(8 if field[pos][1] else 2,
                              7*(1+dx)//2 - dx*x2, 7*(1+dy)//2 - dy*y2)):
            if ((field[pos + i*dm][0] == str(1 - act))
                and (field[pos + i*dm+dm] == '20')):
                return True