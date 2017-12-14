import pyrebase

config = {
    "apiKey": "AIzaSyCN6JZDMEVwVmZWslTb6msHlvkW1i52-Ss",
    "authDomain": "musi-11554.firebaseapp.com",
    "databaseURL": "https://musi-11554.firebaseio.com",
    "projectId": "musi-11554",
    "storageBucket": "musi-11554.appspot.com",
    "messagingSenderId": "632070266146"
}

def get_firebase_ref():
    firebase = pyrebase.initialize_app(config)
    return firebase.database()