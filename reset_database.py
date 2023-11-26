# THIS FILE SHOULD ONLY BE RUN BY HAND

if __name__ == "__main__":
    from webserver.app import *
    with app.app_context():
        db.drop_all()
        db.create_all()