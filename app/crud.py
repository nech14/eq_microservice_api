from loguru import logger
from app.models import User, Uploaded_file, Directory
import secrets
from datetime import datetime


def add_user(engine, session, nickname: str, email: str, password: str, token=secrets.token_hex(16)):
    with session(autoflush=False, bind=engine) as db:
        new_user = User(email=email, nickname=nickname,
                        password=password, token=token)
        db.add(new_user)
        db.commit()
        new_user_id = new_user.id
        logger.info(f"[CRUD user] New user: {nickname} was created")
    return new_user_id


def add_directory(engine, session, user_id: int, name_directory: str):
    with session(autoflush=False, bind=engine) as db:
        new_directory = Directory(user_id=user_id, name_directory=name_directory)
        db.add(new_directory)
        db.commit()
        new_directory_id = new_directory.id
        logger.info(f"[CRUD directory] New directory for user with id: {user_id} was created")
    return new_directory_id


def add_file(engine, session, user_id: int, directory_id: int, file: str,
             range_start: datetime, range_end: datetime, date=datetime.now(), description=''):
    with session(autoflush=False, bind=engine) as db:
        new_file = Uploaded_file(user_id=user_id, date=date,
                                 directory_id=directory_id, file=file,
                                 range_start=range_start, range_end=range_end, description=description)
        db.add(new_file)
        db.commit()
        new_file_id = new_file.id
        logger.info(f"[CRUD file] Add new file: {file} to directory with id: {directory_id} by "
                    f"user with id {user_id}")
    return new_file_id


def check_user(engine, session, nickname: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname == nickname).first()
    if user:
        logger.info(f"[CRUD user] User: {nickname} was found")
    else:
        logger.error(f"[CRUD user] User: {nickname} wasn't found")
    return bool(user)


def authorization(engine, session, email: str, password: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email == email).filter(User.password == password).first()
    if user:
        logger.info(f"[CRUD user] {user.nickname} was successfully signed in")
    else:
        logger.error(f"[CRUD user] User wasn't signed in")
    return bool(user)


def search_email_by_token(engine, session, token: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.token == token).first()
    if not bool(user):
        logger.info(f"[Search email] Don't have user by this token")
        return None
    logger.info(f"[Search email] Get user's email for user: {user.nickname} by token")
    return user.email


def search_name_by_token(engine, session, token: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.token == token).first()
    if not bool(user):
        logger.info(f"[Search name] Don't have user by this token")
        return None
    logger.info(f"[Search name] Get user's name for user: {user.nickname} by token")
    return user.nickname


def search_token_by_email(engine, session, email: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.email == email).first()
    if not bool(user):
        logger.info(f"[Search token] Don't have user by this email")
        return None
    logger.info(f"[Search token] Get user's token for user: {user.nickname} by email")
    return user.token


def get_user_id(engine, session, nickname: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname == nickname).first()
    if not bool(user):
        logger.info(f"[CRUD user] Don't have user by this nickname")
        return None
    logger.info(f"[CRUD user] Get user id by nickname: {nickname}")
    return user.id


def get_files(engine, session, user_id: int, directory_id: int, limit=10):
    with session(autoflush=False, bind=engine) as db:
        files = db.query(Uploaded_file).filter(Uploaded_file.user_id == user_id,
                                               Uploaded_file.directory_id == directory_id).order_by(
            Uploaded_file.date.desc()).limit(limit).all()
        logger.info(f"[CRUD file] Get {limit} files from directory "
                    f"with id: {directory_id} for user with id: {user_id}.")
    return files


def get_file(engine, session, file_id):
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id == file_id).first()
    if not bool(file):
        logger.info(f"[CRUD user]  Don't have file by file_id: {file_id}")
        return None
    logger.info(f"[CRUD user] Get file by file_id: {file_id}")
    return file


def get_directories(engine, session, user_id: int):
    with session(autoflush=False, bind=engine) as db:
        directories = db.query(Directory).filter(Directory.user_id == user_id).all()
        logger.info(f"[CRUD directory] User with id: {user_id} get directories")
    return directories


def get_directory_id_by_name(engine, session, user_id: int, name_directory: str):
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.user_id == user_id,
                                               Directory.name_directory == name_directory).first()
    if not bool(directory):
        logger.info(f"[CRUD directory] User with id: {user_id} don't have directory id by name {name_directory}")
        return None
    logger.info(f"[CRUD directory] User with id: {user_id} get directory id by name {name_directory}")
    return directory.id


def get_directory_by_id(engine, session, directory_id: int):
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.id == directory_id).first()
        logger.info(f"[CRUD directory] Get directory id by id {directory_id}")
    if not bool(directory):
        return None
    return directory


def get_dates(engine, session, user_id: int, first_date, second_date, limit=10):
    with session(autoflush=False, bind=engine) as db:
        files = db.query(Uploaded_file).filter(Uploaded_file.user_id == user_id,
                                               Uploaded_file.range_start >= first_date,
                                               Uploaded_file.range_end <= second_date).limit(limit).all()
        logger.info(f"[CRUD file] Get files for user with id: {user_id} by date between {first_date} and "
                    f"{second_date}")
    return files


def del_user(engine, session, nickname: str):
    with session(autoflush=False, bind=engine) as db:
        user = db.query(User).filter(User.nickname == nickname).first()
        db.delete(user)
        db.commit()
        logger.info(f"[CRUD user] Delete user: {nickname}")


def del_file(engine, session, file_id: int):
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id == file_id).first()
        db.delete(file)
        db.commit()
        logger.info(f"[CRUD file] Delete file with id: {file_id}")


def del_directory(engine, session, directory_id: int):
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.id == directory_id).first()
        db.delete(directory)
        db.commit()
        logger.info(f"[CRUD directory] Delete directory by id {directory_id}")


def update_file(engine, session, file_id: int, new_name: str, date=datetime.now()):
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id == file_id).first()
        old_name = file.file
        file.file = new_name
        file.date = date
        db.commit()
        logger.info(f"[CRUD file] Rename file with id {file_id} from {old_name} to {new_name}")



def update_description_file(engine, session, file_id: int, new_description: str, date=datetime.now()):
    with session(autoflush=False, bind=engine) as db:
        file = db.query(Uploaded_file).filter(Uploaded_file.id == file_id).first()
        old_description = file.description
        file.description = new_description
        file.date = date
        db.commit()
        logger.info(f"[CRUD file] Update description file with id {file_id} from {old_description} to {new_description}")


def update_name_directory(engine, session, directory_id: int, new_name: str):
    with session(autoflush=False, bind=engine) as db:
        directory = db.query(Directory).filter(Directory.id == directory_id).first()
        old_name = directory.name_directory
        directory.name_directory = new_name
        db.commit()
        logger.info(f"[CRUD directory] Rename directory with id: {directory_id} from {old_name} to {new_name}")
