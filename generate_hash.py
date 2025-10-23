# Use a temporary script to generate the hash
from app.crud.user import get_password_hash

# The client is sending 'testpassword123' (see Dio Request in original prompt)
password_to_hash = "testpassword123" 
hashed_value = get_password_hash(password_to_hash)

print(hashed_value)