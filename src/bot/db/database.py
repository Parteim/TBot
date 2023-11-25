from models import User, engin

from sqlalchemy.orm import Session

with Session(bind=engin) as session:
    user = User(user_id=123, username='Admin', is_admin=True)
    session.add(user)
    session.commit()

    user = session.query(User).filter_by(id=1).first()
    print(user)
