from supabase import create_client, Client

SUPABASE_URL = "url"
SUPABASE_KEY = "api key"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


data = {
    
    "852741": {
        "name": "Brad Pitt",
        "course": "B.Tech_CSE",
        "total_attendance": 6,
        "batch": "61,62",
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    "963852": {
        "name": "Dwayne Johnson",
        "course": "B.Tech_CSE",
        "total_attendance": 6,
        "batch": "61,62",
        "last_attendance_time": "2022-12-11 00:54:34"
    }
}


students_to_insert = []

for student_id, info in data.items():
    student_entry = {
        "id": student_id,
    }
    students_to_insert.append(student_entry)


response = supabase.table("students").insert(students_to_insert).execute()

print("Insert response:", response)
