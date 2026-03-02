from sqlalchemy.orm import Session

# This allows us to access the db, based onn it's session
class BaseRepository:
  def __init__(self, sessioin: Session) -> None:
    self.session = sessioin