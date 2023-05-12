#Магические константы
const = {'imgSize':64, 'size':70, 'FPosX':650, 'FPosY':0, 'IPosX':-4, 'IPosY':+1, 'TPosX':360, 'TPosY':0,
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

def gamePage(name, gm):
    colors = fieldColors(gm)
    but = ''.join([button(i, "act", gm['field'][i], 
                          i if gm[0] == name else 63-i, colors[i]) for i in range(64)])
    act = gm['act']
    return f'''<html><body><form method = "post">
            <div style="position:absolute; left:{const['TPosX']}px; top:{const['TPosY']}px">
            <p>Game id: {gm['id']}</p>
            <p>White player: {gm[0]}</p>
            <p>Black player: {gm[1]}</p>
            <p>{'Black' if act else 'White'} player's move</p>
            <p><button type="submit" value="draw" name="endGame"/>Draw</button>
            <button type="submit" value="give up" name="endGame"/>To give up</button></p>
            <p>{'opponent offers a draw' if gm['draw'] else ''}</p>
            <p>{roolButtons(name, gm)}</p></div>
            {choiceButtons(name, gm)}{but}
            </form></body></html>'''