from flask import Blueprint, render_template, request, session, redirect, url_for, Flask
from flask_login import current_user, LoginManager, UserMixin, login_user, login_required, logout_user
from flask_socketio import leave_room, join_room, send, SocketIO
from flask_sqlalchemy import SQLAlchemy
from .models import User
import random
from string import ascii_uppercase
from . import socketio

chats = Blueprint("chats", __name__)

salas = {}

def generate_unique_code(length):
    while True:
        cod = ""
        for _ in range(length):
            cod += random.choice(ascii_uppercase)
        if cod not in salas:
            break
    return cod

@chats.route("/chat", methods=["POST", "GET"])
def chat():
    session.clear()
    if request.method == "POST":
        cod = request.form.get("cod")
        unir = request.form.get("unir", False)
        crear = request.form.get("crear", False)

        if unir != False and not cod:
            return render_template("chat.html", error="Por favor, ingresa un código de sala.", cod=cod, user=current_user)

        sala = cod
        if crear != False:
            sala = generate_unique_code(4)
            salas[sala] = {"miembros": 0, "mensajes": []}
        elif cod not in salas:
            return render_template("chat.html", error="La sala no existe, intenta de nuevo.", cod=cod, user=current_user)

        session["sala"] = sala
        session["user_id"] = current_user.id
        return redirect(url_for("chats.sala"))

    return render_template("chat.html", cod="", user=current_user)


@chats.route("/sala")
def sala():
    sala = session.get("sala")
    user = User.query.get(session.get("user_id"))
    if sala is None or user is None or sala not in salas:
        return redirect(url_for("chats.chat"))

    return render_template("sala.html", cod=sala, mensajes=salas[sala]["mensajes"], first_name=user.first_name)

@socketio.on('connect')
def connect():
    sala = session.get('sala')
    user = User.query.get(session.get('user_id'))
    if not sala or not user:
        return
    join_room(sala)
    send({'first_name': user.first_name, 'mensaje': 'ha entrado a la sala'}, to=sala)
    socketio.emit('usuario_conectado', {'first_name': user.first_name}, to=sala)

@socketio.on('mensaje')
def mensaje(data):
    sala = session.get('sala')
    if sala not in salas:
        return
    user = User.query.get(session.get('user_id'))
    content = {'first_name': user.first_name, 'mensaje': data['data']}
    send(content, to=sala)
    salas[sala]['mensajes'].append(content)
    print(f"Enviando mensaje a la sala {sala}: {content}")


@socketio.on('disconnect')
def disconnect():
    sala = session.get('sala')
    user = User.query.get(session.get('user_id'))
    leave_room(sala)
    if sala in salas:
        salas[sala]['miembros'] -= 1
        if salas[sala]['miembros'] <= 0:
            del salas[sala]
    send({'first_name': user.first_name, 'mensaje': 'ha salido de la sala'}, to=sala)
    socketio.emit('usuario_desconectado', {'first_name': user.first_name}, to=sala)
    print(f"{user.first_name} salió de la sala {sala}")
