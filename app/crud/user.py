from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)

def get_password_hash(password: str) -> str:
    """Securely hashes the provided password."""
    truncated_password = password.encode('utf-8')[:72]
    return pwd_context.hash(truncated_password)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Retrieves a user object by email address."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User | None:
    """
    Creates a new user account if the email does not already exist.
    Returns the new User object or None if the email is taken.
    """
    # Check if user already exists
    if await get_user_by_email(db, email=user_in.email):
        # Return None or raise an exception in a full implementation
        return None 

    # Hash the password for secure storage
    hashed_password = get_password_hash(user_in.password)
    
    # Create the database model instance
    db_user = User(
        user_id=uuid.uuid4(),
        email=user_in.email,
        password_hash=hashed_password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_active=True
    )
    
    # Add to session and commit
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user
