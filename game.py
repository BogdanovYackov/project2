from flask import Flask, redirect, url_for, request, Response

from chess import chessMove, castling, checkChessWin
from checkers import checkersMove
from page import gamePage
from move import endMove

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
    resultName = {'':'not finished', 'win0':'white win', 'win1':'black win', 'draw':'draw'}
    
    
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
              'castling':[1, 1, 1, 1], 'eat':0, 'type':tp, 'draw':[0,0],
              'mustEat':[0]*3, 'eatBack':[1]*3, 'highlight':[set(), set()],
              'field' : cheskers[:] if tp == 'cheskers' else (chess[:] if tp == 'chess' else checkers[:])}
        gm[0] = name
        info['games'][gid] = gm
        info['NGId'] += 1
        info['result'][gid] = [name, None, '', tp]
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
        td = '<td align="center">'
        th = '<th align="center">'
        result = [f'''{f'{td}{res[r][3]}</td>' if tp == 'all' else ''}
                    {td}{r}</td><td>{res[r][0]}</td>{td}{res[r][1]}</td>
                    {td}{resultName[res[r][2]]}</td>'''
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

    def endRequest(name, gid, end):
        gm = info['games'][gid]
        if end and ((name == gm[0]) or (name == gm[1])):
            if end == 'draw':
                gm['draw'][name == gm[1]] ^= 1
            if (gm[0] == gm[1]) or (gm['draw'] == [1, 1]):
                info['result'][gid][2] = 'draw'
            elif end == 'give up':
                player = int(name == gm[0])
                info['result'][gid][2] = f'win{player}'
        return endGame(name, gid)

    def endGame(name, gid, result = None):
        if result is not None:
            info['result'][gid][2] = result
        if info['result'][gid][2]:
            tp = info['result'][gid][3]
            if info['result'][gid][1] is None:
                info[tp] = None
                del info['result'][gid]
            del info['games'][gid]
            return redirect(url_for('score', name = name, 
                                    password = '_'+info['users'][name], tp = tp))

    def choose(name, gm, choice):
        if choice:
            gm['field'][gm['move']] = choice
            gm['choice'] = 0
            red = checkChessWin(gm, gm['field'], gm['act'])
            if red:
                return red
            endMove(gm, -1, 1 - gm['act'])

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
            return endGame(name, gm['id'], checkersMove(gm, pos1, pos2))
        else:
            return endGame(name, gm['id'], chessMove(gm, pos1, pos2))

    @app.route('/game/<string:tp>/<int:gid>/<string:name>/<string:password>', methods = ['POST', 'GET'])
    def game(name, password, gid, tp):
        if gid not in info['games']:
            return redirect(url_for('score', name=name, password=password, tp=tp))
        gm = info['games'][gid]
        if request.method == 'GET':
            return checkUser(name, password) or gamePage(name, info['games'][gid])
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
        return red or gamePage(name, info['games'][gid])
    return app