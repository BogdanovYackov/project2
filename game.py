from flask import Flask, redirect, url_for, request, Response
def createApp():
    app = Flask(__name__)
    
    #Данные игры
    info = {'users':{'':''}, 'games':{}, 'result':{}, 'NGId':1, 'chess':None, 'cheskers':None, 'checkers':None}
    
    #стартовые позиции
    chess = (['1r','1h','1b','1q','1k','1b','1h','1r'] + ['1p']*8 +
             ['20']*32 + ['0p']*8 + ['0r','0h','0b','0q','0k','0b','0h','0r'])
    cheskers = (['20','1c','20','1l','20','1l','20','1b'] + ['1m','20']*4 + ['20','1m']*4 + ['20']*16 
                + ['0m','20']*4 + ['20','0m']*4 + ['0b','20','0l','20','0l','20','0c','20'])
    checkers = (['20','1m']*4 + ['1m','20']*4 + ['20','1m']*4 +
                ['20']*16 + ['0m','20']*4 + ['20','0m']*4 + ['0m','20']*4)
    
    #Магические константы
    const = {'imgSize':64, 'size':70, 'FPosX':650, 'FPosY':0, 'IPosX':-4, 'IPosY':+1, 'TPosX':360, 'TPosY':0,
             'results':('not finished', 'white win', 'black win', 'draw'),
             'applyColors':("white", "blue", "yellow", "green")}
    
    
    #Соответствие констант и фигур
    #0 - первый игрок
    #1 - второй игрок
    #p - пешка - pawn
    #t - ладья - rook
    #h - конь - knight
    #b - слон - bishop
    #q - ферзь - queen
    #k - король - king (chess)
    #l - король - king (checkers)
    #c - верблюд - camel
    #m - шашка - man
    #d - дамка - king (checkers)
    #20 - пустая клетка
    colorName = {'0':'White ', '1':'Black ', '2':''}
    figName = {'m':'man',  'd':'king',   'l':'king',   'c':'camel', 'p':'pawn',  
               'r':'rook', 'h':'knight', 'b':'bishop', 'q':'queen', 'k':'king', '0':''}

    @app.route('/')
    def root():
        return redirect(url_for('login'))

    @app.route('/login', defaults={'error':''}, methods = ['POST', 'GET'])
    @app.route('/login/<string:error>', methods = ['POST', 'GET'])
    def login(error):
        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            if name not in info['users']:
                info['users'][name] = password
            if name and (info['users'][name] == password):
                return redirect(url_for('menu', name = name, password = "_"+password, tp = 'cheskers'))
        return f'''<html><body><div align="center"><form method = "post">
                <big><big><br><br><br>
                <p>{"User isn't registered" if error == 'name' else ''}
                {'Wrong password' if error == 'password' else ''}</p>
                <p>Name:</p>
                <p><input type = "text" name = "name" /></p>
                <p>Password:</p>
                <p><input type = "text" name = "password" /></p>
                <p><input type = "submit" value = "submit" /></p>
                </big></big></form></div></body></html>'''

    def checkUser(name, password):
        if name not in info['users']:
            return redirect(url_for('login', error = 'name'))
        if "_"+info['users'][name] != password:
            return redirect(url_for('login', error = 'password'))

    def menuPage(tp, error):
        return f'''<html><body><div align="center"><form method = "post">
                    <big><big><br><br><br>
                    <p><button type="submit" style="background-color:{'green' if tp == 'checkers' else 'white'}"
                        value="checkers" name="type"/><big><big>checkers</big></big></button>
                    <button type="submit" style="background-color:{'green' if tp == 'cheskers' else 'white'}"
                        value="cheskers" name="type"/><big><big>cheskers</big></big></button>
                    <button type="submit" style="background-color:{'green' if tp == 'chess' else 'white'}"
                        value="chess" name="type"/><big><big>chess</big></big></button></p>
                    <p><button type="submit" value="random" name="start"/>
                    <big><big>Random opponent</big></big></button></p>
                    <p><button type="submit" value="youself" name="start"/>
                    <big><big>Play with youself</big></big></button></p>
                    <p><button type="submit" value="wait" name="start"/>
                    <big><big>Famous opponent</big></big></button></p>
                    <p></p><p>Game id:</p>
                    <p><input type = "int" style="width:160px;" name = "game" /></p>
                    <p><button type="submit" value="join" name="start"/>
                    <big><big>Join with id</big></big></button></p>
                    {"<p>Game isn't started</p>" if error else ''}
                    </big></big></form></div></body></html>'''

    def newGame(name, tp, start):
        gid = info['NGId']
        gm = {0:None, 1:None, 'id':gid, 'move':-1, 'act':0, 'fix':0, 'choice':0, 'passant':(-1, 2),
              'castling':[1, 1, 1, 1], 'eat':0, 'type':tp, 'draw':0,
              'mustEat':[0]*3, 'eatBack':[1]*3, 'highlight':[set(), set()],
              'field' : cheskers[:] if tp == 'cheskers' else (chess[:] if tp == 'chess' else checkers[:])}
        gm[0] = name
        info['games'][gid] = gm
        info['NGId'] += 1
        info['result'][gid] = [name, None, 0, tp]
        if start == 'random':
            info[tp] = gid
        return gid

    def startGame(name, password, tp, gid, start):
        if (start == 'youself'):
            gid = newGame(name, tp, start)
            info['games'][gid][1] = name
            info['result'][gid][1] = name
        elif ((info[tp] is None) and (start == 'random')) or (not gid and (start == 'wait')):
            gid = newGame(name, tp, start)
            if start == 'random':
                info[tp] = gid
        elif start == 'random':
            gid = info[tp]
            info[tp] = None
            info['games'][gid][1] = name
            info['result'][gid][1] = name
        elif gid not in info['games']:
            return redirect(url_for('menu', name = name, password = password, tp = tp, error = 'error'))
        elif info['games'][gid][1] is None:
            info['games'][gid][1] = name
            info['result'][gid][1] = name
            if info[info['games'][gid]['type']] == gid:
                info[info['games'][gid]['type']] = None
        return redirect(url_for('game', name = name, password = password, gid = gid, tp = tp))

    @app.route('/menu/<string:name>/<string:password>/<string:tp>', defaults={'error':''}, methods = ['POST', 'GET'])
    @app.route('/menu/<string:name>/<string:password>/<string:tp>/<string:error>', methods = ['POST', 'GET'])
    def menu(name, password, tp, error):
        red = checkUser(name, password)
        if red or request.method == 'GET':
            return red or menuPage(tp, error)
        if request.form.get('type'):
            tp = request.form.get('type')
            return redirect(url_for('menu', name = name, password = password, tp = tp))
        return startGame(name, password, tp, int(request.form['game'] or 0), request.form.get('start'))

    def scorePage(tp, name):
        res = info['result']
        td = '<td align="right">'
        th = '<th align="center">'
        result = [f'''{f'{td}{res[r][3]}</td>' if tp == 'all' else ''}
                    {td}{r}</td><td>{res[r][0]}</td>{td}{res[r][1]}</td>
                    {td}{const["results"][res[r][2]]}</td>'''
                    for r in res if (tp == 'all' or tp == res[r][3])]
        return f'''<html><body><div align="center">
                <big><big><br><br><br><form method = "post">
                <p><button type="submit" style="background-color:
                    {'green' if tp == 'checkers' else 'white'}"
                    value="checkers" name="type"/><big><big>checkers</big></big></button>
                <button type="submit" style="background-color:
                    {'green' if tp == 'cheskers' else 'white'}"
                    value="cheskers" name="type"/><big><big>cheskers</big></big></button>
                <button type="submit" style="background-color:
                    {'green' if tp == 'chess' else 'white'}"
                    value="chess" name="type"/><big><big>chess</big></big></button>
                <button type="submit" style="background-color:{'green' if tp == 'all' else 'white'}"
                    value="all" name="type"/><big><big>all</big></big></button></p>
                {'<p><button type="submit" value="menu" name="link"/>To menu</button></p>' if name else ''}
                </form><p>Score Table: {tp}</p><table border="1" cellspacing="1">
                <tr>{th+'type</th>' if tp == 'all' else ''}{th}id</th>
                {th}white player</th>{th}black player</th>{th}result</th></tr>
                <tr>{'</tr><tr>'.join(result)}</tr></table>
                </big></big></div></body></html>'''

    @app.route('/score/', defaults={'tp':'all', 'name':'', 'password':''}, methods = ['POST', 'GET'])
    @app.route('/score/<string:tp>/', defaults={'name':'', 'password':''}, methods = ['POST', 'GET'])
    @app.route('/score/<string:tp>/<string:name>/<string:password>', methods = ['POST', 'GET'])
    def score(name, password, tp):
        if request.method == 'POST':
            tp = request.form.get('type') or ('checkers' if tp == 'all' else tp)
            if request.form.get('link'):
                return redirect(url_for('menu', name = name, password = password, tp = tp))
            elif request.form.get('type'):
                return redirect(url_for('score', name = name, password = password, tp = tp))
        return scorePage(tp, name)

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
                info['result'][gm['id']][2] = 1 + act if gm['highlight'][0] else 3
                return endGame(gm[act], gm['id'])
    def chessMove(gm, pos1, pos2):
        field = gm['field']
        act = gm['act']
        if checkMove(gm, field, pos1, pos2, act):
            if field[pos2][1] == "k":
                info['result'][gm['id']][2] = 1 + act
                return endGame(gm[act], gm['id'])
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
            checkChessWin(gm, field, act)
            return endMove(gm, -1, 1 - act)

    def chessAttack(gm, pos2, act):
        field = gm['field']
        var = field[pos2]
        field[pos2] = str(1 - act) + '0'
        res = [pos1 for pos1 in range(64) if ((field[pos1][0] == str(act))
                                              and checkMove(gm, field, pos1, pos2, act))]
        field[pos2] = var
        return res

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

    def xy(pos1, pos2):
        x1 = pos1 % 8
        x2 = pos2 % 8
        y1 = pos1 // 8
        y2 = pos2 // 8
        return x1, y1, x2, y2

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
        gid = gm['id']
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

    def endMove(gm, pos1, act):
        field = gm['field']
        for a in (0, 1):
            if gm['type'] == 'checkers':
                if not sum([(x[0] == str(a)) for x in field]):
                    info['result'][gm['id']][2] = 2 - a
            if gm['type'] == 'cheskers':
                if not sum([(x == f'{a}l') for x in field]):
                    info['result'][gm['id']][2] = 2 - a
        red = endGame(gm[gm['act']], gm['id'])
        if red:
            return red
        if gm['act'] != act:
            if act == gm['passant'][1]:
                gm['passant'] = (-1, 2)
            pos1 = -1
            gm['act'] = act
            gm['fix'] = 0
            gm['choice'] = 0
            gm['eat'] = checkNextMoves(gm, field, act)
        gm['move'] = pos1

    def endRequest(name, gid, end):
        gm = info['games'][gid]
        if end and ((name == gm[0]) or (name == gm[1])):
            if end == 'draw':
                gm['draw'] ^= 1 + (name == gm[1])
            if (gm[0] == gm[1]) or (gm['draw'] == 3):
                info['result'][gid][2] = 3
            elif end == 'give up':
                info['result'][gid][2] = 1 + (name == gm[0])
        return endGame(name, gid)

    def endGame(name, gid):
        if info['result'][gid][2]:
            tp = info['result'][gid][3]
            if info['result'][gid][1] is None:
                info[tp] = None
                del info['result'][gid]
            del info['games'][gid]
            return redirect(url_for('score', name = name, 
                                    password = '_'+info['users'][name], tp = tp))

    def roolButton(rool, gm, player, val, body):
        col = 2 if (val == gm[rool][player]) else (val == gm[rool][1 - player])
        if val == gm[rool][2]:
            col = 3
        return f'''<button type="submit" style="background-color:
            {const['applyColors'][col]}" value="{val}" name="{rool}"/>{body}</button>'''
    def changeRool(name, rool, gm, val):
        if gm[0] == gm[1]:
            gm[rool] = [val, val, val]
        else:
            act = name == gm[1]
            gm[rool][act] = val
            if val == gm[rool][1 - act]:
                gm[rool][2] = val

    def button(value, name, body, pos, color):
        img = ''
        if body != '20':
            img = f'''<div style="position:relative; left:{const['IPosX']}px; top:{const['IPosY']}px">
                    <img src="/static/{body}.png" alt="{colorName[body[0]]+figName[body[1]]}"
                    width="{const['imgSize']}" height="{const['imgSize']}"></div>'''
        return f'''<div style="position:absolute; 
                left:{const['FPosX']+const['size']*(pos%8)}px;
                top:{const['FPosY']+const['size']*(pos//8)}px">
                    <button type="submit" style="height:{const['size']}px; width:{const['size']}px;
                    background-color:{color}" value="{value}" name="{name}"/>
                    {img}
                </button></div>'''

    def roolButtons(name, gm):
        player = name == gm[1]
        s = ''
        if gm['type'] != 'chess':
            s = f'''<p>Must eat:
                    {roolButton('mustEat', gm, player, 0, "off")}
                    {roolButton('mustEat', gm, player, 1, "on")}</p>
                    <p>Can eat back:
                    {roolButton('eatBack', gm, player, 0, "off")}
                    {roolButton('eatBack', gm, player, 1, "on")}</p>'''
        if name == gm[gm['act']] and gm['fix'] and not gm['mustEat'][2]:
            s += '<p><button type="submit" value="true" name="endTurn"/>End move</button></p>' 
        return s
    def choiceButtons(name, gm):
        if name == gm[gm['act']] and gm['choice']:
            if gm['type'] == 'chess':
                return ''.join([button(f"{gm['act']}{'rhbq'[i]}", "choice",
                                     f"{gm['act']}{'rhbq'[i]}", 74 + i, "grey") for i in range(4)])
            else:
                return ''.join([button(f"{gm['act']}{'cbl'[i]}", "choice",
                                     f"{gm['act']}{'cbl'[i]}", 74.5 + i, "grey") for i in range(3)])
        return ''

    def fieldColors(gm):
        col = ["" for i in range(64)]
        for i in range(64):
            if (i == gm['move']):
                col[i] = "green"
            elif i in gm['highlight'][0]:
                col[i] = "red"
            elif i in gm['highlight'][1]:
                col[i] = "orange"
            else:
                col[i] = "black" if ((i+i//8)%2) else "white"
        return col
    def gamePage(name, gid):
        gm = info['games'][gid]
        colors = fieldColors(gm)
        but = ''.join([button(i, "act", gm['field'][i], 
                              i if gm[0] == name else 63-i, colors[i]) for i in range(64)])
        act = gm['act']
        return f'''<html><body><form method = "post">
                <div style="position:absolute; left:{const['TPosX']}px; top:{const['TPosY']}px">
                <p>Game id: {gid}</p>
                <p>White player: {gm[0]}</p>
                <p>Black player: {gm[1]}</p>
                <p>{'Black' if act else 'White'} player's move</p>
                <p><button type="submit" value="draw" name="endGame"/>Draw</button>
                <button type="submit" value="give up" name="endGame"/>To give up</button></p>
                <p>{'opponent offers a draw' if gm['draw'] else ''}</p>
                <p>{roolButtons(name, gm)}</p></div>
                {choiceButtons(name, gm)}{but}
                </form></body></html>'''

    def choose(name, gm, choice):
        if choice:
            gm['field'][gm['move']] = choice
            gm['choice'] = 0
            red = checkChessWin(gm, gm['field'], gm['act'])
            if red:
                return red
            endMove(gm, -1, 1 - gm['act'])

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

    def startMove(name, gm):
        act = gm['act']
        pos1 = gm['move']
        pos2 = int(request.form.get('act') or -1)
        if request.form.get('endTurn'):
            if (gm['fix'] == 1) and (name == gm[act]):
                endMove(gm, pos1, 1 - act)
        elif (name != gm[act]) or (pos2 == -1):
            pass
        elif (gm['field'][pos2][0] == str(act)) and (gm['fix'] == 0):
            if not castling(gm, pos1, pos2, act):
                gm['move'] = pos2
        elif (pos1 == -1):
            pass
        elif gm['field'][pos1][1] in "md":
            return checkersMove(gm, pos1, pos2)
        else:
            return chessMove(gm, pos1, pos2)

    @app.route('/game/<string:tp>/<int:gid>/<string:name>/<string:password>', methods = ['POST', 'GET'])
    def game(name, password, gid, tp):
        if gid not in info['games']:
            return redirect(url_for('score', name=name, password=password, tp=tp))
        gm = info['games'][gid]
        if request.method == 'GET':
            return checkUser(name, password) or gamePage(name, gid)
        if request.form.get('mustEat'):
            changeRool(name, 'mustEat', gm, int(request.form.get('mustEat')))
        if request.form.get('eatBack'):
            changeRool(name, 'eatBack', gm, int(request.form.get('eatBack')))
        red = checkUser(name, password)
        red = red or endRequest(name, gid, request.form.get('endGame'))
        if red:
            return red
        red = choose(name, gm, request.form.get('choice'))
        red = red or startMove(name, gm)
        return red or gamePage(name, gid)
    return app
