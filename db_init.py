from app import create_app, db

app = create_app()

# Use the app context to create the database tables
with app.app_context():
    db.create_all()
