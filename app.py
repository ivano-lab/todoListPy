from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
  return jsonify({"status": "API de Tarefas está online e funcionando!"})

if __name__ == '__main__':
    app.run(debug=True)