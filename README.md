Основная проблема запуска игры - отсутствие сервера.
Игру можно запустить по сети при наличии ngrok, запустив ngrok.py ,
но она будет работать только пока включена она и клиент ngrok.
Игру можно запустить локально, запустив localhost.py .

Их дополнительные пунктов реализована только графика.

Игра содержит костыльную авторизацию - при вводе нового пользователя
игра сохраняет введённый пароль, иначе проверяет его.

Кнопка "Random opponent" начинает новую партию и ждёт следующего игрока,
который начнёт такую же игру, если есть партия без оппонента,
иначе присоединяет к последней начатой игре.

Кнопка "Play with youself" начинает новую партию для игры на одном компьютере.

Кнопка "Famous opponent" начинает новую партию, к которой можно
присоединиться при помощи id, или присоединяет к такой игре при помощи id.

Кнопка "Join with id" присоединяет к игре при помощи id.

При помощи id также можно присоединится к игре, в которой уже есть
два участника, но без возможности участвовать.

Игра позволяет менять правила связанные с шашками во время игры.

Для изменения правил и ничьи необходимо подтверждение обоих участников.

Содержится три игры - шашки, шашматы, шахматы.