import os
import secrets
import string
import uvicorn
from datetime import date

from fastapi import FastAPI, UploadFile, File
from pydantic import EmailStr

from modules.db_logic import check_user, add_user, authorization, search_by_token, search_by_email, get_user_id, add_file, \
    get_files, get_dates, update_file, del_file


from modules.responses import generate_success_response, generate_success_regdata, generate_bad_authdata_response, generate_bad_token_response, generate_username_inuse_response, generate_success_wtoken,  generate_success_wdata
from modules.security import generate_token
app = FastAPI()


@app.post("/sign_up")
async def sign_up(user_name: str, user_email: EmailStr, password: str) -> dict:
    token = generate_token()
    if check_user(user_name) > 0:
        return generate_bad_authdata_response()
    add_user(user_name, user_email, password, token)
    os.mkdir(os.path.join(os.getcwd(), 'users_data', user_name))
    return generate_success_regdata(user_name, token)


@app.post('/sign_in')
async def sign_in(user_email: EmailStr, password: str) -> dict:
    if authorization(user_email, password) == 0:
        return generate_bad_authdata_response()
    token = search_by_email(user_email)
    return generate_success_wtoken(token)


@app.post("/upload_data")
async def upload_data(token: str, file: UploadFile = File(...)) -> dict:
    user_name = search_by_token(token)
    if user_name:
        filename = file.filename
        with open(os.path.join(os.getcwd(), 'users_data', user_name, filename), "wb") as f:
            f.write(await file.read())
        user_id = get_user_id(user_name)
        add_file(user_id, filename)
        return generate_success_response()
    return generate_bad_token_response()


@app.get("/get_last_data")
async def get_last_data(token: str, limit: int = 5) -> dict:
    user_name = search_by_token(token)
    if user_name:
        user_id = get_user_id(user_name)
        return generate_success_wdata(get_files(user_id, limit=limit))
    return generate_bad_token_response()


@app.get("/get_data")
async def get_data(token: str, start_date: date, finish_date: date) -> dict:
    user_name = search_by_token(token)
    if user_name:
        user_id = get_user_id(user_name)
        return generate_success_wdata(get_dates(user_id, start_date, finish_date))
    return generate_bad_token_response()



@app.post("/update_data")
async def update_data(token: str, data_id: int, file: UploadFile = File(...)) -> dict:
    user_name = search_by_token(token)
    if user_name:
        filename = file.filename
        with open(os.path.join(os.getcwd(), 'users_data', user_name, filename), "wb") as f:
            f.write(await file.read())
        user_id = get_user_id(user_name)
        update_file(data_id, filename)
        return generate_success_response()
    return generate_bad_token_response()


@app.post("/delete_data")
async def delete_data(token: str, data_id: int) -> dict:
    user_name = search_by_token(token)
    if user_name:
        user_id = get_user_id(user_name)
        del_file(data_id)
        return generate_success_response()
    return generate_bad_token_response()


def main():
    uvicorn.run(f"{os.path.basename(__file__)[:-3]}:app", log_level="info")


if __name__ == '__main__':
    main()
