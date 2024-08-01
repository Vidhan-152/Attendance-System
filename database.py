import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://attendance-system-46645-default-rtdb.firebaseio.com/'
})

ref = db.reference('Students')

data = {
    "179319":
        {
            "name":"Vidhan Sachdeva",
            "major":"Data Science and Engg.",
            "starting_year":2024,
            "total_attendance":6,
            "Standing":"G",
            "last_attendance_time":"2024-07-23 9:34:19"
        },
    "964954":
        {
            "name":"Sundar Pichai",
            "major":"Metallurgy",
            "starting_year":1995,
            "total_attendance":21,
            "Standing":"P",
            "last_attendance_time":"2024-07-23 9:54:48"
        },
    "789217":
        {
            "name":"Elon Musk",
            "major":"Computer Science",
            "starting_year":1990,
            "total_attendance":10,
            "Standing":"G",
            "last_attendance_time":"2024-07-23 9:24:48"
        }
}

for key, values in data.items():
    ref.child(key).set(values)