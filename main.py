from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import engine, SessionLocal

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# =========================
# SESSION MIDDLEWARE
# =========================
app.add_middleware(
    SessionMiddleware,
    secret_key="mysecretkey"
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


templates = Jinja2Templates(
    directory="frontend"
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# =========================
# FRONTEND ROUTES
# =========================

@app.get("/")
def home_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


@app.get("/login-page")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.get("/register-page")
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="registration.html"
    )


@app.get("/index")
def index_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/donate-page")
def donate_page(request: Request):

    if not request.session.get("user"):
        return RedirectResponse(
            url="/login-page",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="donate.html"
    )


@app.get("/foods-page")
def foods_page(request: Request):

    if not request.session.get("user"):
        return RedirectResponse(
            url="/login-page",
            status_code=303
        )

    db = SessionLocal()

    foods = db.query(
        models.Food
    ).all()

    return templates.TemplateResponse(

        request=request,

        name="foods.html",

        context={
            "foods": foods
        }

    )


# =========================
# API ROUTES
# =========================

@app.post("/register")
def register(

    request: Request,
    username: str = Form(...),
    password: str = Form(...)

):

    db = SessionLocal()

    existing_user = db.query(
        models.User
    ).filter(
        models.User.username == username
    ).first()

    if existing_user:

        return {
            "message": "Username already exists"
        }

    hashed_password = hash_password(
        password
    )

    new_user = models.User(

        username=username,
        password=hashed_password

    )

    db.add(new_user)

    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="success.html"
    )


@app.post("/login")
def login(

    request: Request,
    username: str = Form(...),
    password: str = Form(...)

):

    db = SessionLocal()

    db_user = db.query(
        models.User
    ).filter(
        models.User.username == username
    ).first()

    if db_user is None:

        return {
            "message": "User not found"
        }

    if not verify_password(
        password,
        db_user.password
    ):

        return {
            "message": "Incorrect password"
        }

    # Store user in session
    request.session["user"] = username

    # Redirect to home page after successful login
    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.get("/profile")
def profile(
    token: str = Depends(oauth2_scheme)
):

    payload = verify_token(token)

    return {
        "message": "Protected Route",
        "user": payload
    }


@app.post("/donate")
def donate_food(

    request: Request,
    donor: str = Form(...),
    food: str = Form(...),
    quantity: int = Form(...),
    location: str = Form(...),
    phone: str = Form(...)

):

    if not request.session.get("user"):
        return RedirectResponse(
            url="/login-page",
            status_code=303
        )

    db = SessionLocal()

    new_food = models.Food(

        donor=donor,
        food=food,
        quantity=quantity,
        location=location,
        phone=phone,
        status="available"
    )

    db.add(new_food)

    db.commit()

    return RedirectResponse(
        url="/foods-page",
        status_code=303
    )


@app.get("/foods")
def get_foods():

    db = SessionLocal()

    foods = db.query(
        models.Food
    ).all()

    return foods


@app.post("/order/{food_id}")
def order_food(
    request: Request,
    food_id: int
):

    if not request.session.get("user"):
        return RedirectResponse(
            url="/login-page",
            status_code=303
        )

    db = SessionLocal()

    food = db.query(
        models.Food
    ).filter(
        models.Food.id == food_id
    ).first()

    if food is None:

        return RedirectResponse(
            url="/foods-page",
            status_code=303
        )

    if food.status != "available":

        return RedirectResponse(
            url="/foods-page",
            status_code=303
        )

    food.status = "ordered"

    db.commit()

    return RedirectResponse(
        url="/foods-page",
        status_code=303
    )


@app.delete("/delete/{food_id}")
def delete_food(
    food_id: int,
    token: str = Depends(oauth2_scheme)
):

    db = SessionLocal()

    verify_token(token)

    food = db.query(
        models.Food
    ).filter(
        models.Food.id == food_id
    ).first()

    if food is None:

        return {
            "error": "Food not found"
        }

    db.delete(food)

    db.commit()

    return {
        "message": "Food deleted successfully"
    }