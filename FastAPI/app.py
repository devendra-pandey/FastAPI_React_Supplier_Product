from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (supplier_pydantic,supplier_pydanticIn,Supplier,Products,product_pydantic,product_pydanticIn)

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




@app.post('/product/{supplier_id}')
async def add_Product(supplier_id:int , product_detail:product_pydanticIn):
    supplier = await Supplier.get(id=supplier_id)
    product_detail = product_detail.dict(exclude_unset=True)
    product_detail['revenue'] += product_detail['quantity_sold'] * product_detail['unit_price']
    product_obj = await Products.create(**product_detail, supplied_by=supplier )
    response = await product_pydantic.from_tortoise_orm(product_obj)
    return{"status":"ok","data":response}

@app.get('/product')
async def all_products():
    response = await product_pydantic.from_queryset(Products.all())
    return{"status":"ok","data":response}

@app.get('/product/{product_id}')
async def get_specific_product(product_id:int):
    response = await product_pydantic.from_queryset_single(Products.get(id=product_id))
    return{"status":"ok","data":response}


@app.put('/product/{product_id}')
async def update_specific_product(product_id: int, update_info: product_pydanticIn):
    product = await Products.get(id=product_id)
    update_info = update_info.dict(exclude_unset=True)
    product.name = update_info['name']
    product.quantity_in_stock = update_info['quantity_in_stock']
    product.revenue += update_info['quantity_sold'] * update_info['unit_price'] + update_info['revenue']
    product.quantity_sold += update_info['quantity_sold']
    product.unit_price = update_info['unit_price']
    await product.save()
    response = await product_pydantic.from_tortoise_orm(product)
    return {"status": "ok", "data": response}



@app.delete('product/{product_id}')
async def delete_product(product_id:int):
    await Products.filter(id = product_id).delete()
    return{"status":"ok"}



register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models":["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)