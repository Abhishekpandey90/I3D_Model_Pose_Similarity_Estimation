import jwt  # This is from the PyJWT library, not your file!
import datetime

# Secret key provided by the server
JWT_SECRET = "AqHBFWJqdPo6vaVtaXtD"
JWT_ALGORITHM = "HS256"

# Function to generate JWT token
def generate_jwt(user_id: str, expiration_minutes: int = 60):
    """Generates a JWT token valid for a specific time"""

    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)

    payload = {
        "user_id": user_id,
        "exp": expiration_time,  # Expiration time
        "iat": datetime.datetime.utcnow(),  # Issued at
    }

    # Generate token using PyJWT's jwt.encode()
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)  # ✅ Use jwt directly
    return token

# Example Usage
user_id = "coach123"
token = generate_jwt(user_id)
print('------', token)
