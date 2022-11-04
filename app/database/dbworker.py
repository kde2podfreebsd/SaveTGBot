import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import uuid

app = Flask(__name__)
app.app_context().push()

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer())
    language = db.Column(db.String(64), default="N/A")
    username = db.Column(db.String(64), default ="N/A")
    date_of_join = db.Column(db.String(64), default ="N/A")
    referal_code = db.Column(db.String(64), default ="N/A")

    def __repr__(self):
        return f"<User {self.chat_id}>"

def init_user(chat_id: int, username: str, date_of_join: str, referal_code:str):
    try:
        with app.app_context():
            if Users.query.filter_by(chat_id=chat_id).first():
                return {"message": 'User already added'}
            else:
                user = Users(chat_id=chat_id, username = username, date_of_join = date_of_join, referal_code = referal_code, language='N/A')
                db.session.add(user)
                db.session.commit()

            return {"message": 'User added', "name": user.chat_id}

    except Exception as e:
        return jsonify(message=e, status="DB error")

def set_language(chat_id, language):
    try:
        with app.app_context():
            if Users.query.filter_by(chat_id=chat_id).first():
                user = Users.query.filter_by(chat_id=chat_id).first()
                user.language = language
                db.session.commit()
                return {"message": f'Language set is{user.language}', "status": True}
            else:
                return {"message": 'No user with this chat_id', "status": False}

    except Exception as e:
        return jsonify(message=e, status="DB error")

def get_language(chat_id):
    try:
        with app.app_context():
            if Users.query.filter_by(chat_id=chat_id).first():
                user = Users.query.filter_by(chat_id=chat_id).first()
                return user.language
            else:
                return {"message": 'No user with this chat_id', "status": False}

    except Exception as e:
        return jsonify(message=e, status="DB error")

def get_users():
    try:
        with app.app_context():
            return Users.query.filter(Users.id != None).all()

    except Exception as e:
        return jsonify(message=e, status="DB error")

class Admin(db.Model):
    __tablename__ = 'Admin'

    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer())

    def __repr__(self):
        return f"<User {self.chat_id}>"


def init_admin(chat_id: int):
    try:
        with app.app_context():
            if Admin.query.filter_by(chat_id=chat_id).first():
                return {"message": 'Admin already added'}
            else:
                admin = Admin(chat_id=chat_id)
                db.session.add(admin)
                db.session.commit()

            return {"message": 'User added', "name": admin.chat_id}

    except Exception as e:
        return jsonify(message=e, status="DB error")


def delete_admin(chat_id: int):
    try:
        with app.app_context():
            if Admin.query.filter_by(chat_id=chat_id).first():
                Admin.query.filter(Admin.chat_id == chat_id).delete()
                db.session.commit()

                return {"message": 'Admin deleted', "chat_id": chat_id}

            else:
                return {"message": 'Admin alreday deleted', "chat_id": chat_id}

    except Exception as e:
        return jsonify(message=e, status="DB error")

def is_admin(chat_id:int):
    try:
        with app.app_context():
            if Admin.query.filter_by(chat_id=chat_id).first():
                return True
            else:
                return False

    except Exception as e:
        return jsonify(message=e, status="DB error")

class Downloads(db.Model):
    __tablename__ = 'Downloads'

    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer())
    src_type = db.Column(db.String(64), default="N/A")
    date_of_join = db.Column(db.String(64), default="N/A")
    url = db.Column(db.String(5096), default="N/A")

    def __repr__(self):
        return f"<Download {self.id}>"

def init_download(chat_id: int, src_type:str, date_of_join:str, url: str):
    try:
        with app.app_context():
            download = Downloads(chat_id=chat_id, src_type = src_type, date_of_join=date_of_join, url=url)
            db.session.add(download)
            db.session.commit()

            return {"message": 'download added', "id": download.id}

    except Exception as e:
        return jsonify(message=e, status="DB error")


def get_stat():
    try:
        with app.app_context():
            downloads = Downloads.query.filter(Downloads.id != None).all()
            users = Users.query.filter(Users.id != None).all()
            users_today = 0
            today_downloads = 0
            youtube_iter = 0
            tiktok_iter = 0
            instagram_iter = 0
            shorts_iter = 0

            for i in range(len(users)):
                if users[i].date_of_join == date_today():
                    users_today += 1

            for i in range(len(downloads)):
                if downloads[i].date_of_join == date_today():
                    today_downloads += 1
                if downloads[i].src_type == 'youtube':
                    youtube_iter += 1
                if downloads[i].src_type == 'tiktok':
                    tiktok_iter += 1
                if downloads[i].src_type == 'instagram':
                    instagram_iter += 1
                if downloads[i].src_type == 'youtube_shorts':
                    shorts_iter += 1

            return {
                'number_of_users': len(users),
                'users_today': users_today,
                'all_downloads': len(downloads),
                'today_downloads': today_downloads,
                'youtube': youtube_iter,
                'tiktok': tiktok_iter,
                'instagram': instagram_iter,
                'youtube_shorts': shorts_iter
            }

    except Exception as e:
        return jsonify(message=e, status="DB error")

def date_today():
    with app.app_context():
        today = date.today()
        return str(today.strftime("%d/%m/%Y"))

class Referal(db.Model):
    __tablename__ = 'Referal'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64))
    uuid = db.Column(db.String(64))


def init_referal(name: str):
    try:
        with app.app_context():
            uid = uuid.uuid4()
            referal = Referal(name=name, uuid = str(uid))
            db.session.add(referal)
            db.session.commit()

            return referal.uuid

    except Exception as e:
        return jsonify(message=e, status="DB error")

def get_name_by_uuid(uuid:str):
    try:
        with app.app_context():
            referal = Referal.query.filter_by(uuid=uuid).first()
            return referal.name

    except Exception as e:
        return jsonify(message=e, status="DB error")

def get_referal_stat():
    try:
        with app.app_context():
            referals = Referal.query.filter(Referal.id != None).all()
            unique = []
            output = dict()

            for i in range(len(referals)):
                if referals[i].uuid in unique and referals[i].uuid != 'N/A':
                    continue
                else:
                    unique.append(referals[i].uuid)
                    output[referals[i].uuid] = 0

            users = Users.query.filter(Users.id != None).all()

            for i in range(len(users)):
                if users[i].referal_code in unique and users[i].referal_code != 'N/A':
                    output[users[i].referal_code] += 1

            return output

    except Exception as e:
        return jsonify(message=e, status="DB error")

class Ads(db.Model):
    __tablename__ = 'Ads'

    id = db.Column(db.Integer(), primary_key=True)
    shortname = db.Column(db.String(64))
    text = db.Column(db.String(10192))
    file_path = db.Column(db.String(1024), default="N/A")
    media_type = db.Column(db.String(8), default="N/A")
    btn_text =db.Column(db.String(64), default="N/A")
    btn_url = db.Column(db.String(10192), default="N/A")

    def __repr__(self):
        return f"<Ad {self.id}>"

def new_ad(shortname: str, text: str, file_path: str, media_type: str, btn_text: str, btn_url: str):
    try:
        with app.app_context():
            if Ads.query.filter_by(shortname=shortname).first():
                return {"message": 'Ad already added', "shortname": shortname}
            else:
                ad =  Ads(shortname=shortname, text = text, file_path = file_path, media_type = media_type, btn_text = btn_text, btn_url= btn_url)
                db.session.add(ad)
                db.session.commit()

                return {"message": 'Ad added', "id": ad.id}

    except Exception as e:
        return jsonify(message=e, status="DB error")

def get_ads():
    try:
        with app.app_context():
            return Ads.query.filter(Ads.id != None).all()

    except Exception as e:
        return jsonify(message=e, status="DB error")

def get_ad(shortname: str):
    with app.app_context():
        return Ads.query.filter_by(shortname=shortname).first()

def delete_ad(shortname: str):
    try:
        with app.app_context():
            if Ads.query.filter_by(shortname=shortname).first():
                Ads.query.filter(Ads.shortname == shortname).delete()
                db.session.commit()

                return {"message": 'Ad deleted', "shortname": shortname}

            else:
                return {"message": 'Ad alreday deleted', "chat_id": shortname}

    except Exception as e:
        return jsonify(message=e, status="DB error")
