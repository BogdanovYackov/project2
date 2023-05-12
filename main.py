#local = True -- запуск на локальном хосте
#local = False -- запуск на хосте ngrok
local = True

from game import createApp
app = createApp()

if local:
    app.run("localhost", 5000)
else:
    #!pip install pyngrok
    from flask_ngrok import run_with_ngrok
    run_with_ngrok(app)
    app.run()