from datetime import datetime, timedelta
from fastapi import FastAPI, Request, status
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
import requests
import jwt

import app.settings as settings
import app.docs as docs
import app.models as models
import app.mongo as mongo
import app.exceptions as exceptions

#############################################
########### APP INITIALIZATION ##############
#############################################
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(
    title="web10",
    openapi_tags=docs.tags_metadata,
    description=docs.description,
    version="10.0.0.0",
    terms_of_service="http://example.com/terms/",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

####################################################
########### User Password Authentication ###########
####################################################
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = mongo.get_user(username)
    if not user:
        raise exceptions.LOGIN
    if not verify_password(password, user.hashed_password):
        return exceptions.LOGIN
    return user


##################################################
########### Token Based Authentication ###########
##################################################
def decode_token(token: str, private_key=False) -> models.TokenData:
    if private_key:
        payload = jwt.decode(
            token, settings.PRIVATE_KEY, algorithms=[settings.ALGORITHM]
        )
    else:
        payload = jwt.decode(token, verify=False)
    token_data = models.TokenData()
    token_data.populate_from_payload(payload)
    return token_data


# check if a token can be minted given a submitted token
def can_mint(submission_token, mint_token):
    # TODO CHECK FOR PROTOCOL
    if submission_token.username == mint_token.username:
        pass
    else:
        raise exceptions.MINT
    if not submission_token.site:
        pass
    elif submission_token.site in settings.CORS_SERVICE_MANAGERS:
        pass
    elif submission_token.site == mint_token.site:
        pass
    else:
        raise exceptions.MINT

    if submission_token.provider == settings.PROVIDER:
        if submission_token.provider == mint_token.provider:
            pass
    else:
        raise exceptions.MINT

    return True


# certify a web10 token with a remote provider
def certify_with_remote_provider(token: models.Token):
    decoded = decode_token(token.token)
    url = f"{decoded.provider}/certify"
    response = requests.post(url, json=token.json())
    return response.status_code == 200


# checks if :
# a token certifies with it's provider, is targetted to this provider, is cross origin approved, and whitelisted
def is_permitted(token: models.Token, username, service, action):
    # TODO ADD WHITELIST AND BLACKLISING

    decoded = decode_token(token.token)
    if settings.PROVIDER == decoded.provider:
        certified = certify(token)
    else:
        certified = certify_with_remote_provider(token)

    if certified:
        decoded = models.dotdict(jwt.decode(token.token, verify=False))
        if not decoded.target:
            if decoded.username == username and decoded.provider == settings.PROVIDER:
                return True
            else:
                return False
        elif decoded.target != settings.PROVIDER:
            return False

        if mongo.is_in_cross_origins(decoded.site, username, service):
            if mongo.get_approved(
                decoded.username, decoded.provider, username, service, action
            ):
                return True
    return False


##############################################
############ Web10 Routes For You ############
##############################################
# check that a token is a valid non expired token written by this web10 server.
@app.post("/certify")
async def certify_token(token: models.Token):
    return certify(token)


def certify(token: models.Token):
    try:
        token_data = decode_token(token.token, private_key=True)
        if token_data.provider != settings.PROVIDER:
            raise exceptions.TOKEN
        if token_data.username is None:
            raise exceptions.TOKEN
        if datetime.utcnow() > datetime.fromisoformat(token_data.expires):
            raise exceptions.TOKEN
    except:
        raise exceptions.TOKEN
    return True


# make a web10 token via. user password flow, or via. submitted token
@app.post("/web10token", response_model=models.Token)
async def create_web10_token(form_data: models.TokenForm):
    token_data = models.TokenData()
    token_data.populate_from_token_form(form_data)
    try:
        if form_data.password:
            if authenticate_user(form_data.username, form_data.password):
                pass
        elif form_data.token:
            if certify(models.Token(token=form_data.token)):
                if can_mint(decode_token(form_data.token), token_data):
                    pass
    except Exception as e:
        raise e
    token_data.expires = (
        datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    ).isoformat()
    token_data.provider = settings.PROVIDER
    return {
        "token": jwt.encode(
            token_data.dict(), settings.PRIVATE_KEY, algorithm=settings.ALGORITHM
        )
    }


# make a new web10 account
@app.post("/signup")
async def signup(form_data: models.SignUpForm):
    return mongo.create_user(models.dotdict(form_data), get_password_hash)


#####################################################
############ Web10 Routes Managed By You ############
#####################################################
@app.post("/{user}/{service}", tags=["web10"])
async def create_records(user, service, token: models.Token):
    if not is_permitted(token, user, service, "create"):
        raise exceptions.CRUD
    return mongo.create(user, service, token.query)


# web10 uses patch for get in CRUD since get requests can't have a secure body
@app.patch("/{user}/{service}", tags=["web10"])
async def read_records(user, service, token: models.Token):
    if not is_permitted(token, user, service, "read"):
        raise exceptions.CRUD
    result = mongo.read(user, service, token.query)
    return result


@app.put("/{user}/{service}", tags=["web10"])
async def update_records(user, service, token: models.Token):
    if not is_permitted(token, user, service, "update"):
        raise exceptions.CRUD
    return mongo.update(user, service, token.query, token.value)


@app.delete("/{user}/{service}", tags=["web10"])
async def delete_records(user, service, token: models.Token):
    if not is_permitted(token, user, service, "delete"):
        raise exceptions.CRUD
    return mongo.delete(user, service, token.query)