from supabase import create_client, Client
from fastapi import FastAPI,BackgroundTasks, HTTPException
from typing import List,Optional
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel,Field
from datetime import datetime
import json
import pytz
import os
# إعداد الاتصال
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")  
supabase: Client = create_client(url, key)







app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        
    allow_credentials=False,    
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.head("/")
async def read_root_head():
    return {"message": "This is a HEAD request"}
@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI!"}

@app.get("/categories", response_model=List[dict])
def get_categories():
    response = supabase.table("categories").select("*").execute()

    categories=[]

    for row in response.data:
        categorie={
            "id": row['id'],
            "name": row["name"],
            'image':row['image'],

        }
        categories.append(categorie)
    return categories    
  



@app.get("/product/{id}", response_model=dict)
def get_product(id: int):
    response = supabase.table("product").select("*").eq("id", id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_data = response.data[0]

    # Get the category name
    response2 = supabase.table("categories").select("*").eq("id", product_data['categories-id']).execute()
    categorie_name = response2.data[0]['name'] if response2.data else None

    product = {
        "id": product_data['id'],
        "name": product_data["name"],
        "price": product_data['price'],
        "oldprice": product_data['old-price'],
        "main-image": product_data['main-image'],
        "images": product_data['images'],
        "categorie": categorie_name,
        "descreption": product_data['descreption'],
        "colores": product_data['colores'],
        "size": product_data['size'],
        "stock": product_data['stock'],
        "brand": product_data['brand'],
        "created_at": product_data['created_at'],
    }

    return product





@app.get("/products", response_model=List[dict])
def get_():
    response = supabase.table("product").select("*").execute()
    response2 = supabase.table("categories").select("*").execute()
    products=[]

    for row in response.data:
        for row2 in response2.data:
            if row2['id'] == row['categories-id']:
                categorie_name = row2['name']
        
        product={
            "id": row['id'],
            "name": row["name"],
            'price':row['price'],
            'oldprice':row['old-price'],
            'main-image':row['main-image'],
            'images':row['images'],
            'categorie':categorie_name,
            'descreption':row['descreption'],
            'colores':row['colores'],
            'size':row['size'],
            'stock':row['stock'],
            'brand':row['brand'],
            'created_at':row['created_at'],
            
        
        }
        products.append(product)
    return products    



class OrderData(BaseModel):
    firstname: str
    lastname: str
    ordername:str
    wilaya: str
    baladiya: str
    size: str
    color: str
    quantity: int  
    phone: int
    deliveryType: str
    price:float
    deliveryprice:float



    

@app.post("/save-order")
async def save_order(order: OrderData):
    try:
        
        # Insert data into the 'orders' table in Supabase
        response = supabase.table('orders').insert({
            'firstname': order.firstname,
            'lastname': order.lastname,
            'wilaya': order.wilaya,
            'baladiya': order.baladiya,
            'size': order.size,
            'color': order.color,
            'quantity': order.quantity,
            'phone': order.phone,
            'deliveryType': order.deliveryType,
            'ordername': order.ordername,
            'price': order.price,
            'deliveryprice':order.deliveryprice,
        }).execute()
        return response
       
    
    except Exception as e:
        pass


class ProdcutData(BaseModel):
    name: str
    category_id: int = Field(..., alias="categoryId")
    price: float
    old_price: Optional[float] = Field(None, alias="oldPrice")
    main_image: str = Field(..., alias="mainImage")
    images: List[str]
    descreption: Optional[str] = Field(None, alias="description")
    colores: Optional[List[str]] = Field(None, alias="colors")
    size: Optional[List[str]] = Field(None, alias="sizes")
    stock: int
    brand: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
  



@app.post("/save-product")
async def save_product(product: ProdcutData):
    try:
        facebook_link = product.main_image.replace(
            "/c_fill,w_800,h_800,g_auto/",
            "/c_pad,w_1200,h_628,b_white/"
        )
        response = supabase.table('product').insert({
            'name': product.name,
            'categories-id': product.category_id,
            'price': product.price,
            'old-price': product.old_price if product.old_price is not None else None,
            'main-image': product.main_image,
            'images': product.images, 
            'descreption': product.descreption if product.descreption is not None else None,
            'colores': product.colores if product.colores else None,  # ✅ تحويل القائمة الفارغة إلى null
            'size': product.size if product.size else None,  # ✅ تحويل القائمة الفارغة إلى null
            'stock': product.stock,
            'brand': product.brand if product.brand is not None else None,
            'facebook':facebook_link
        }).execute()

        return response

    except Exception as e:
        return {"error": str(e)} 





class CategoryData(BaseModel):
    name: str
    main_image: str
  




  


@app.post("/save-category")
async def save_product(category: CategoryData):
    try:
        response = supabase.table('categories').insert({
            'name': category.name,
            'image': category.main_image,
        }).execute()

        return response

    except Exception as e:
        return {"error": str(e)}

class ProductUpdate(BaseModel):
    name: str
    price: float
    oldPrice: Optional[float] = None
    mainImage: str
    images: List[str]
    description: Optional[str] = None
    colors: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    stock: int
    brand: Optional[str] = None
    categoryId: int

    class Config:
        extra = "ignore"

@app.put("/update-product/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    data = product.dict(exclude_none=True)
    # هنا نعيد تسمية المفاتيح لتطابق أسماء الأعمدة في قاعدة البيانات
    rename_map = {
        "categoryId": "categories-id",
        "oldPrice": "old-price",
        "mainImage": "main-image",
        "description": "descreption",
        "colors": "colores",
        "sizes": "size",
    }
    data_db = {rename_map.get(k, k): v for k, v in data.items()}

    response = supabase.table("product").update(data_db).eq("id", product_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated successfully", "updated_product": response.data}


   


class categoriesUpdate(BaseModel):
    name: str | None = None,
    image: str | None = None,
    

  


@app.put("/update-categories/{categories_id}")
async def update_product(categories_id: int, categorie: categoriesUpdate):
    try:
        response = supabase.table("categories").update(categorie.dict(exclude_none=True)).eq("id",categories_id ).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="categorie not found")

        return {"message": "categories updated successfully", "updated_categories": response.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")



@app.get("/orders", response_model=List[dict])
def get_():
    response = supabase.table("orders").select("*").execute()
   
    orders=[]

    for row in response.data:
        order={
            "id": row['id'],
            "firstname": row["firstname"],
            'lastname':row['lastname'],
            'ordername':row['ordername'],
            'price':row['price'],
            'phone':row['phone'],
            'color':row['color'],
            'size':row['size'],
            'quantity':row['quantity'],
            'deliveryType':row['deliveryType'],
            'baladiya':row['baladiya'],
            'wilaya':row['wilaya'],
            'deliveryprice':row['deliveryprice'],
            'status':row['status'],
            
        
        }
        orders.append(order)
    return orders










class UpdateRequest(BaseModel):
    status: int




@app.put("/update_order_status/{order_id}")
async def update_order_status(order_id: int, request: UpdateRequest):
    new_status = request.status
    

    # تحديث البيانات في قاعدة البيانات
    update_data = {"status": new_status}
    
    if new_status == 1:
        utc_time = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S.%f%z')
        update_data["status_change_date"] = utc_time  # Adding formatted time

    # تنفيذ التحديث
    result = supabase.table("orders").update(update_data).eq("id", order_id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update status")

    return {"message": "Status updated successfully", "new_status": new_status}






async def check_and_delete_orders():
    # Current time in UTC
    now = datetime.now(pytz.utc)
    
    # Get all orders that haven't been updated in the last 24 hours
    response = supabase.table("orders").select("*").execute()

    if not response.data:
        return
    
    for order in response.data:
        status_change_date = order.get("status_change_date")
        
        if status_change_date:
            # Convert to datetime if it's a string
            if isinstance(status_change_date, str):
                status_change_date = datetime.fromisoformat(status_change_date)
            
            # If the order is older than 24 hours, delete it
            if now - status_change_date > timedelta(hours=24):
                # Deleting the order from the database
                delete_response = supabase.table("orders").delete().eq("id", order["id"]).execute()
                if delete_response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"Failed to delete order {order['id']}")
                print(f"Deleted order {order['id']} due to inactivity")
        else:
            print(f"No status_change_date for order {order['id']}")

# Endpoint to trigger the background task manually (for testing)
@app.get("/check_orders")
async def check_orders(background_tasks: BackgroundTasks):
    background_tasks.add_task(check_and_delete_orders)
    return {"message": "Checking orders... Task will run in the background."}

# Endpoint to manually update order status (for example, changing status and updating the date)
@app.put("/update_order_status/{order_id}")
async def update_order_status(order_id: int, request: dict):
    response = supabase.from_("orders").select("*").filter("id", "eq", order_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Order not found")

    order = response.data[0]  # Get order data

    # Get the new status from the request (default to the current status if not provided)
    current_status = order["status"]
    new_status = request.get("status", current_status)

    # If status is 1, change to 3, otherwise decrement by 1
    if new_status == 1:
        new_status = 3
    else:
        new_status = new_status - 1

    # Update data and include the current time for status change
    update_data = {"status": new_status, "status_change_date": datetime.now(pytz.utc)}

    # Perform the update in the database
    result = supabase.table("orders").update(update_data).eq("id", order_id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update status")

    return {"message": "Status updated successfully", "new_status": new_status}


@app.delete("/delete_product/{product_id}")
async def delete_product(product_id: int):
    try:
        # البحث عن المنتج والتأكد من وجوده
        response = supabase.from_("product").select("id").eq("id", product_id).execute()
        
        # التحقق مما إذا كان المنتج موجودًا
        if not response.data:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # حذف المنتج
        delete_response = supabase.from_("product").delete().eq("id", product_id).execute()

        return {"message": "Product deleted successfully", "product_id": product_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")















@app.delete("/delete_categoury/{categoury_id}")
async def delete_category(categoury_id: int):
    try:
        response = supabase.from_("categories").select("id").eq("id", categoury_id).execute()

        if response.data is None or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Category not found")

        delete_response = supabase.from_("categories").delete().eq("id", categoury_id).execute()

        return {"message": "Category deleted successfully", "category_id": categoury_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting category: {str(e)}")













