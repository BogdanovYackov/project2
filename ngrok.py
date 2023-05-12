#!pip install pyngrok
from flask_ngrok import run_with_ngrok
from game import createApp
app = createApp()
run_with_ngrok(app)
app.run()
