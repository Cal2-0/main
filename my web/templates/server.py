from flask import Flask, render_template, request, session, redirect, url_for,Blueprint
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

chat_bp = Blueprint('home',__name__)
chat_bp.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(chat_bp)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code
@chat_bp.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        password = request.form.get("password")  # Get password from form

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False:
            if not code or not password:
                return render_template("home.html", error="Please enter room code and password.", code=code, name=name)
            if code not in rooms:
                return render_template("home.html", error="Room does not exist.", code=code, name=name)
            if rooms[code]["password"] != password:
                return render_template("home.html", error="Incorrect password.", code=code, name=name)

            room = code  # Join existing room

        elif create != False:
            if not password:
                return render_template("home.html", error="Please enter a password to create room.", code=code, name=name)
            
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": [], "password": password}

        else:
            return render_template("home.html", error="Invalid action.", code=code, name=name)

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")


@chat_bp.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"], password=rooms[room]["password"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].chat_bpend(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(chat_bp, debug=True)