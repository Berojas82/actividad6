from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, send, join_room, leave_room

db = SQLAlchemy()
DB_NAME = "database.db"
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    socketio.init_app(app)

    # Registro de blueprints y otras configuraciones
    from .inicio import inicio
    from .auth import auth
    from .chats import chats
    from .popcorns import popcorns

    app.register_blueprint(inicio, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(chats, url_prefix='/')
    app.register_blueprint(popcorns, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
