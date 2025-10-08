from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)

class Task(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  description = db.Column(db.String(200), nullable=True)
  done = db.Column(db.Boolean, default=False)
  created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

  def __repr__(self):
      return f"<Task {self.id}>"

  def to_dict(self):
      return {
          'id': self.id,
          'title': self.title,
          'description': self.description,
          'done': self.done,
          'created_at': self.created_at.isoformat()
      }
      
with app.app_context():
    db.create_all()

@app.route('/api/tasks', methods=['POST', 'GET'])
def handle_tasks():
    if request.method == 'POST':
        data = request.get_json()

        if not data or 'title' not in data:
            return jsonify({"message": "Título da tarefa é obrigatório."}), 400
        
        new_task = Task(
            title=data['title'],
            description=data.get('description'),
            done=data.get('done', False)
        )

        try: 
            db.session.add(new_task)
            db.session.commit()
            return jsonify(new_task.to_dict()), 201
        except Exception:
            db.session.rollback()
            return jsonify({"message": "Erro interno ao salvar tarefa."}), 500
    
    elif request.method == 'GET':
        tasks = Task.query.all()
        tasks_list = [task.to_dict() for task in tasks]
        return jsonify(tasks_list)
    
@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_task(task_id):
    task = db.get_or_404(Task, task_id)

    if request.method == 'GET':
        return jsonify(task.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return '', 204
    
    if request.method == 'PUT':
        data = request.get_json()

        if not data:
            return jsonify({"message":"Dados de atualização são obrigatórios."}), 400

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)

    if 'done' in data:
        task.done = data['done']

    db.session.commit()
    return jsonify(task.to_dict()
                   )    
if __name__ == '__main__':
    app.run(debug=True)