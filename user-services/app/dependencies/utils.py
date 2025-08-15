#utitly function
from passlib.context import CryptContext


#telling passlib about hashing method which is bcrypt
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

#generate a hash for a our passowrd
def hash_password(password:str)->str:
    return pwd_context.hash(password)

#verify hashed password
def verify_password(plane_password,hashed_password):
    return pwd_context.verify(plane_password,hashed_password)