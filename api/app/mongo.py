import pymongo
from bson.objectid import ObjectId
import app.settings as settings
import app.models as models
import app.web10records as records
import app.exceptions as exceptions
import os
import re


#################################
####### CONNECTING TO DB ########
#################################

client_url = os.environ.get('DB_URL')
if not client_url:
    DB_URL = settings.DB_URL
client = pymongo.MongoClient(DB_URL)
db = client["web10"]


################################
####### USER FUNCTIONS #########
################################

def get_user(username: str):
    #check if user exists [by checking if they have any service terms]
    user_col = db[f'{username}']
    if user_col["services"].count_documents({})==0:
        raise Exception("user does not exist")
    query = {"service":"*"}
    doc = user_col['services'].find_one(query)
    if (doc == None):
        raise Exception("no (*) service found")
    return models.dotdict(doc)

def create_user(form_data, hash):
    username,password = form_data.username,form_data.password
    user_col = db[f'{username}']
    if user_col['services'].count_documents({})!=0:
        return "user already exists"   
    # (*) record that holds both username and the password
    new_user = records.star_record()
    new_user["username"] = username
    new_user["hashed_password"] = hash(password)

    # (services) record that allows auth.localhost to modify service terms
    services_terms = records.services_record()

    # insert the records to create / sign up the user
    user_col['services'].insert_one(new_user) 
    user_col['services'].insert_one(services_terms)
    return "success"

##########################
######### CRUD ###########
##########################

def create(user,service,query,many=False):
    #TODO handle many case
    q = [query]
    if many:q=query
    if star_found([q]): return False
    result = db[f'{user}'][f'{service}'].insert_one(query)
    query["_id"]=str(result.inserted_id)
    return query

def read(user,service,query):
    #TODO whitelists + blacklist filtering
    records = db[f'{user}'][f'{service}'].find(query)
    records=[record for record in records]
    for record in records : 
        if record["_id"] : 
            record["_id"] = str(record["_id"])
    return records

def update(user,service,query,value):
    #TODO whitelists + blacklist filtering
    if "_id" in query:
        query["_id"] = ObjectId(query["_id"])
    if star_selected(user,service,query):
        raise exceptions.STAR
    db[f'{user}'][f'{service}'].update_many(query, value)
    return "success"

def delete(user,service,query):
    #TODO whitelists + blacklist filtering
    if "_id" in query:
        query["_id"] = ObjectId(query["_id"])
    if star_selected(user,service,query):
        raise exceptions.STAR
    db[f'{user}'][f'{service}'].delete_many(query)
    return "success"


##########################
####### Protection #######
##########################

# returns true if star service is inside the input
def star_found(services_docs):
    star = list(filter(lambda x:"service" in x and x["service"]=="*",services_docs))
    if len(star)>0:return True
    return False

# sees if a mongodb query selects the star service
def star_selected(user,service,query):
    if service == "services":
        records = read(user,service,query)
        return star_found(records)
    return False

def is_in_cross_origins(site, username, service):
    record = db[f'{username}']['services'].find_one({"service":service})
    if record == None: return False
    return (site in record["cross_origins"])

def get_approved(username,provider, owner, service, action):
    record = db[f'{owner}']['services'].find_one({"service":service})
    if record == None: return False
    if (username == owner) and (provider == settings.PROVIDER): return True

    def is_listed(e):
        list_hit = (bool(re.fullmatch(e["username"],username))) and (bool(re.fullmatch(e["provider"],provider)))
        action_permitted = action in e and e[action] == True
        all_permitted = "all" in e and e["all"] == True
        return list_hit and (action_permitted or all_permitted)

    on_whitelist = (len(list(filter(is_listed, record["whitelist"]))) > 0)
    on_blacklist =  (len(list(filter(is_listed, record["blacklist"]))) > 0)
    return not(on_blacklist) and on_whitelist
