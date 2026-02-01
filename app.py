from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood_tracker.db'
db = SQLAlchemy(app)
app.json.ensure_ascii = False 

# Модель данных
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id события
    date = db.Column(db.DateTime, default=lambda: datetime.now()) # дата 
    mood_score = db.Column(db.Integer, nullable=False) # оценка настроения
    tags = db.Column(db.String(200)) # тэги 
    note = db.Column(db.Text) # заметка

with app.app_context():
    db.create_all()

# опубликование записи о настроении
@app.route('/api/mood', methods=['POST'])
def add_mood():
    data = request.json
    
    new_entry = Entry(
        mood_score=data['mood_score'],
        tags=",".join(data.get('tags', [])),
        note=data.get('note', '')
    )
    
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "success"}), 201

# получение статистики за 30 дней (запрос api)
@app.route('/api/stats', methods=['GET'])
def get_stats():
    entries = Entry.query.order_by(Entry.date.desc()).limit(30).all()
    if not entries:
        return jsonify({"message": "Записей еще не было"}), 200

    scores = [e.mood_score for e in entries]
    avg_mood = sum(scores) / len(scores)
    best_days = [e.date.isoformat() for e in entries if e.mood_score >= 8]
    
    return jsonify({
        "average_30_days": round(avg_mood, 2),
        "best_days_dates": best_days,
        "total_entries": len(entries)
    })

# рендер простенькой страницы с отображением функционала
@app.route('/')
def index():
    entries = Entry.query.order_by(Entry.date.desc()).all()
    return render_template('index.html', entries=entries)

# точка входа в приложение
if __name__ == '__main__':
    app.run(debug=True)
