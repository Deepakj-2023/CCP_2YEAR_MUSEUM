from database.database import Database
from sqlalchemy import text
from database.models import Museum
def get_museums(db):
    museums = db.query(Museum).all()  # Fetch using ORM
    return [
        {
            "museum_id": m.museum_id,
            "museum_name": m.museum_name,
            "description": m.description,
            "location": m.location,
            "available_time": m.available_time,
            "price": float(m.price),  # Convert Decimal to float
            "total_tickets": m.total_tickets,
            "recommended_pick_time": m.recommended_pick_time,
        }
        for m in museums
    ]

db = Database.get_db()
session = next(db)
print(get_museums(session))
print(session.execute(text("SELECT * FROM museums;")).fetchall())  # Should return [(1,)]
session.close()

