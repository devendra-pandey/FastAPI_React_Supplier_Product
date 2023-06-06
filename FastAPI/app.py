from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (supplier_pydantic,supplier_pydanticIn,Supplier,Products,product_pydantic,product_pydanticIn)

##email

from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List


#dotenv
from dotenv import dotenv_values

#credentials
credentials = dotenv_values(".env")

class EmailSchema(BaseModel):
    email: List[EmailStr]

class EmailContent(BaseModel):
    message: str
    subject : str


conf = ConnectionConfig(
    MAIL_USERNAME = credentials['EMAIL'],
    MAIL_PASSWORD = credentials['PASS'],
    MAIL_FROM = "credentials['EMAIL']",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    # MAIL_STARTTLS = True,
    MAIL_TLS = True
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)



app = FastAPI()



@app.get('/')
def index():
    return{"Msg":"Go to the docs for the Documentation"}

@app.post('/supplier')
async def add_Supplier(supplier_info:supplier_pydanticIn):
    supplier_obj = await Supplier.create(**supplier_info.dict(exclude_unset=True))
    response = await supplier_pydantic.from_tortoise_orm(supplier_obj)
    return{"status":"ok","data":response}


@app.get('/supplier')
async def get_all_Supplier():
    response = await supplier_pydantic.from_queryset(Supplier.all())
    return{"status":"ok","data":response}


@app.get('/supplier/{supplier_id}')
async def get_specific_supplier(supplier_id:int):
    # response = await Supplier.get(id=supplier_id)
    response = await supplier_pydantic.from_queryset_single(Supplier.get(id=supplier_id))
    return{"status":"ok","data":response}

@app.put('/supplier/{supplier_id}')
async def update_supplier(supplier_id:int, update_info:supplier_pydanticIn):
    supplier = await Supplier.get(id=supplier_id)
    update_info = update_info.dict(exclude_unset = True)
    supplier.name = update_info['name']
    supplier.company = update_info['company']
    supplier.email = update_info['email']
    supplier.phone = update_info['phone']
    await supplier.save()
    response = await supplier_pydantic.from_tortoise_orm(supplier)
    return{"status":"ok","data":response}


@app.delete('/supplier/{supplier_id}')
async def delete_supplier(supplier_id:int):
    await Supplier.filter(id=supplier_id).delete()
    return{"status":"ok"}



@app.post("email/{product_id}"):
async def send_email(product_id:int, content:EmailContent):

    html = f"""<p>Hi this test mail, thanks for using Fastapi-mail</p> """

    @app.post("/email")
    async def simple_send(email: EmailSchema) -> JSONResponse:
        message = MessageSchema(
            subject="Fastapi-Mail module",
            recipients=email.dict().get("email"),
            body=html,
            subtype=MessageType.html)

        fm = FastMail(conf)
        await fm.send_message(message)
        return JSONResponse(status_code=200, content={"message": "email has been sent"})






register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models":["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)