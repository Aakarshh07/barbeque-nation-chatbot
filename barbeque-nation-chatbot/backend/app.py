from flask import Flask
from routes.knowledge_base import kb_blueprint
from routes.chatbot import chatbot_blueprint
from routes.postcall import postcall_blueprint

app = Flask(__name__)
app.register_blueprint(kb_blueprint)
app.register_blueprint(chatbot_blueprint)
app.register_blueprint(postcall_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
