from sqlalchemy import or_
from flask import Flask, request, jsonify, make_response, Blueprint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import markdown
from datetime import datetime
from weasyprint import HTML

app = Flask(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///noteforces.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    token = db.Column(db.String(200), unique=True, nullable=True)
    role = db.Column(db.String(20), default='user')
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def generate_token(self):
        self.token = str(uuid.uuid4())
        db.session.commit()
        return self.token

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))
    shareToken = db.Column(db.String(200), unique=True, nullable=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def json_response(code=0, msg='ok', data=None, status=200):
    return jsonify({'code': code, 'msg': msg, 'data': data or {}}), status

def get_json_body():
    return request.get_json(silent=True) or {}

def get_token():
    auth = request.headers.get('Authorization')
    if auth and auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]
    return None

def login_required(func):
    def wrapper(*args, **kwargs):
        token = get_token()
        if not token:
            return json_response(4001, 'Not logged in', status=401)
        user = User.query.filter_by(token=token).first()
        if not user:
            return json_response(4001, 'Invalid token', status=401)
        return func(user, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def admin_required(func):
    def wrapper(user, *args, **kwargs):
        if user.role != 'admin':
            return json_response(4002, 'Permission denied', status=403)
        return func(user, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@api_bp.route('/user/register', methods=['POST'])
def user_register():
    data = get_json_body()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return json_response(4003, 'Username and password required', status=400)
    if User.query.filter_by(username=username).first():
        return json_response(4003, 'User already exists', status=400)
    is_first_user = User.query.count() == 0
    user = User(username=username)
    user.set_password(password)
    if is_first_user:
        user.role = 'admin'
    db.session.add(user)
    db.session.commit()
    return json_response(0, 'User registered successfully', status=201)

@api_bp.route('/user/login', methods=['POST'])
def user_login():
    data = get_json_body()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return json_response(4003, 'Invalid username or password', status=401)
    token = user.generate_token()
    return json_response(0, 'Login successful', {'token': token})

@api_bp.route('/user/logout', methods=['POST'])
@login_required
def user_logout(current_user):
    current_user.token = None
    db.session.commit()
    return json_response(0, 'Logout successful')

@api_bp.route('/user/me', methods=['GET'])
@login_required
def user_me(current_user):
    return json_response(0, 'ok', {'id': current_user.id, 'username': current_user.username, 'role': current_user.role})

@api_bp.route('/note/create', methods=['POST'])
@login_required
def note_create(current_user):
    data = get_json_body()
    note = Note(userId=current_user.id)
    note.title = data.get('title')
    note.content = data.get('content')
    note.category = data.get('category')
    note.tags = ','.join(data.get('tags') or [])
    db.session.add(note)
    db.session.commit()
    return json_response(0, 'ok', {'noteId': note.id})

@api_bp.route('/note/update', methods=['POST'])
@login_required
def note_update(current_user):
    data = get_json_body()
    noteId = data.get('noteId')
    if current_user.role == 'admin':
        note = db.session.get(Note, noteId)
    else:
        note = Note.query.filter_by(id=noteId, userId=current_user.id).first()
    if not note:
        return json_response(4003, 'Note not found', status=404)
    note.title = data.get('title')
    note.content = data.get('content')
    note.category = data.get('category')
    note.tags = ','.join(data.get('tags') or [])
    db.session.commit()
    return json_response(0, 'ok')

@api_bp.route('/note/delete', methods=['POST'])
@login_required
def note_delete(current_user):
    data = get_json_body()
    noteId = data.get('noteId')
    if current_user.role == 'admin':
        note = db.session.get(Note, noteId)
    else:
        note = Note.query.filter_by(id=noteId, userId=current_user.id).first()
    if not note:
        return json_response(4003, 'Note not found', status=404)
    db.session.delete(note)
    db.session.commit()
    return json_response(0, 'ok')

@api_bp.route('/note/detail', methods=['GET'])
@login_required
def note_detail(current_user):
    noteId = request.args.get('noteId')
    if current_user.role == 'admin':
        note = db.session.get(Note, noteId)
    else:
        note = Note.query.filter_by(id=noteId, userId=current_user.id).first()
    if not note:
        return json_response(4003, 'Note not found', status=404)
    return json_response(0, 'ok', {
        'noteId': note.id,
        'title': note.title,
        'content': note.content,
        'category': note.category,
        'tags': note.tags.split(',') if note.tags else [],
        'createdAt': note.createdAt,
        'updatedAt': note.updatedAt,
        'shareToken': note.shareToken
    })

@api_bp.route('/note/list', methods=['GET'])
@login_required
def note_list(current_user):
    keyword = request.args.get('keyword') or ''
    category = request.args.get('category') or ''
    tags = request.args.getlist('tags')
    query = Note.query.filter_by(userId=current_user.id)
    if keyword:
        query = query.filter(or_(Note.title.contains(keyword), Note.content.contains(keyword)))
    if category:
        query = query.filter_by(category=category)
    notes = []
    for n in query.all():
        note_tags = n.tags.split(',') if n.tags else []
        if all(tag in note_tags for tag in tags):
            notes.append({'noteId': n.id, 'title': n.title, 'category': n.category, 'tags': note_tags})
    return json_response(0, 'ok', {'notes': notes})

@api_bp.route('/note/tags', methods=['GET'])
@login_required
def note_tags(current_user):
    notes = Note.query.filter_by(userId=current_user.id).all()
    tags = set(tag for n in notes for tag in (n.tags.split(',') if n.tags else []))
    return json_response(0, 'ok', {'tags': list(tags)})

@api_bp.route('/note/categories', methods=['GET'])
@login_required
def note_categories(current_user):
    notes = Note.query.filter_by(userId=current_user.id).all()
    categories = set(n.category for n in notes if n.category)
    return json_response(0, 'ok', {'categories': list(categories)})

@api_bp.route('/share/enable', methods=['POST'])
@login_required
def share_enable(current_user):
    data = get_json_body()
    noteId = data.get('noteId')
    if current_user.role == 'admin':
        note = db.session.get(Note, noteId)
    else:
        note = Note.query.filter_by(id=noteId, userId=current_user.id).first()
    if not note:
        return json_response(4003, 'Note not found', status=404)
    if not note.shareToken:
        note.shareToken = str(uuid.uuid4())
        db.session.commit()
    return json_response(0, 'ok', {'shareToken': note.shareToken})

@api_bp.route('/share/disable', methods=['POST'])
@login_required
def share_disable(current_user):
    data = get_json_body()
    noteId = data.get('noteId')
    if current_user.role == 'admin':
        note = db.session.get(Note, noteId)
    else:
        note = Note.query.filter_by(id=noteId, userId=current_user.id).first()
    if not note:
        return json_response(4003, 'Note not found', status=404)
    note.shareToken = None
    db.session.commit()
    return json_response(0, 'ok')

@api_bp.route('/share/view', methods=['GET'])
def share_view():
    token = request.args.get('token')
    note = Note.query.filter_by(shareToken=token).first()
    if not note:
        return json_response(4003, 'Note not found', status=404)
    user = db.session.get(User, note.userId)
    return json_response(0, 'ok', {'noteId': note.id, 'title': note.title, 'content': note.content, 'owner': user.username if user else ''})

@api_bp.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def admin_users(current_user):
    keyword = request.args.get('keyword') or ''
    query = User.query
    if keyword:
        query = query.filter(User.username.contains(keyword))
    users = [{'id': u.id, 'username': u.username, 'role': u.role} for u in query.all()]
    return json_response(0, 'ok', {'users': users})

@api_bp.route('/admin/user/delete', methods=['POST'])
@login_required
@admin_required
def admin_user_delete(current_user):
    data = get_json_body()
    user = db.session.get(User, data.get('userId'))
    if not user:
        return json_response(4003, 'User not found', status=404)
    if user.role == 'admin':
        other_users = User.query.filter(User.id != user.id).count()
        if other_users > 0:
            return json_response(4004, 'Cannot delete admin while other users exist', status=403)
    db.session.delete(user)
    db.session.commit()
    return json_response(0, 'ok')

@api_bp.route('/admin/notes', methods=['GET'])
@login_required
@admin_required
def admin_notes(current_user):
    keyword = request.args.get('keyword') or ''
    userId = request.args.get('userId')
    query = Note.query
    if keyword:
        query = query.filter(Note.title.contains(keyword))
    if userId:
        query = query.filter_by(userId=userId)
    notes = []
    for n in query.all():
        user = db.session.get(User, n.userId)
        notes.append({
            'noteId': n.id,
            'title': n.title,
            'category': n.category,
            'tags': n.tags.split(',') if n.tags else [],
            'owner': user.username if user else ''
        })
    return json_response(0, 'ok', {'notes': notes})

@api_bp.route('/admin/note/delete', methods=['POST'])
@login_required
@admin_required
def admin_note_delete(current_user):
    data = get_json_body()
    note = db.session.get(Note, data.get('noteId'))
    if not note:
        return json_response(4003, 'Note not found', status=404)
    db.session.delete(note)
    db.session.commit()
    return json_response(0, 'ok')

@api_bp.route('/admin/logs', methods=['GET'])
@login_required
@admin_required
def admin_logs(current_user):
    return json_response(0, 'ok', {'logs': []})

@api_bp.route('/health', methods=['GET'])
def health():
    return json_response(0, 'ok', {'status': 'ok'})

# ==================== 导出路由，只支持 PDF ====================
@api_bp.route('/note/export', methods=['GET'])
@login_required
def note_export(current_user):
    note_id = request.args.get('noteId')
    note = Note.query.filter_by(id=note_id, userId=current_user.id).first()
    if not note:
        return json_response(4003, 'Note not found', status=404)

    # 将 Markdown 内容转换为 HTML
    html_body = markdown.markdown(note.content, extensions=['extra', 'codehilite', 'toc'])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{note.title}</title>
        <style>
            body {{
                font-family: 'DejaVu Sans', 'Noto Sans CJK SC', '宋体', SimHei, sans-serif;
                margin: 1.5cm;
                line-height: 1.6;
                color: #333;
            }}
            h1, h2, h3, h4, h5, h6 {{
                margin-top: 1.2em;
                margin-bottom: 0.6em;
                font-weight: bold;
            }}
            h1 {{ font-size: 24pt; }}
            h2 {{ font-size: 20pt; }}
            h3 {{ font-size: 18pt; }}
            p {{ margin: 0 0 0.8em 0; text-align: justify; }}
            ul, ol {{ margin: 0 0 1em 1.5em; padding: 0; }}
            li {{ margin-bottom: 0.3em; }}
            pre {{
                background: #f5f5f5;
                padding: 0.5em;
                border-radius: 4px;
                overflow-x: auto;
                font-family: monospace;
                font-size: 10pt;
                border: 1px solid #ddd;
                margin: 1em 0;
            }}
            code {{
                background: #f5f5f5;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: monospace;
                font-size: 0.9em;
            }}
            blockquote {{
                border-left: 4px solid #ccc;
                margin: 0.5em 0;
                padding-left: 1em;
                color: #666;
                font-style: italic;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 0.4em 0.6em;
                text-align: left;
            }}
            th {{ background: #f0f0f0; }}
            img {{ max-width: 100%; height: auto; }}
            .page-break {{ page-break-before: always; }}
        </style>
    </head>
    <body>
        <h1>{note.title}</h1>
        <div>{html_body}</div>
    </body>
    </html>
    """
    pdf = HTML(string=html_content).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=note_{note.id}.pdf'
    return response

# ==================== 导入外部模块，注册蓝图，创建数据库 ====================
from password_change import setup_password_change
setup_password_change(api_bp, db, User, login_required, json_response)

app.register_blueprint(api_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)