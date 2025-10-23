from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy.future import select 

# Import dependencies for user seeding
from app.core.config import settings, MOCK_USER_A_ID
from app.core.base import Base 
from app.models.user import User # Import User model

# --- Database Setup ---
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Dependency Injection Functions ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session for endpoints."""
    async with AsyncSessionLocal() as session:
        yield session

# Function to initialize database tables AND seed mock data
async def init_db():
    """Initializes the database by creating all defined tables and seeding mock user data."""
        
    async with engine.begin() as conn:
        print("Initializing database...")
        # 1. Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Database structure created.")
        
    # 2. Seed Mock User
    async with AsyncSessionLocal() as session:
        mock_user_id = MOCK_USER_A_ID
        
        # Check if user already exists
        user_result = await session.execute(
            select(User).where(User.user_id == mock_user_id) # <--- Select the User object
        )
        existing_user = user_result.scalars().first()
        
        if not existing_user:
            print(f"Seeding mock user: {mock_user_id}")
            
            mock_user = User(
                user_id=mock_user_id,
                email=settings.MOCK_USER_A_EMAIL,
                password_hash=settings.MOCK_USER_A_PASSWORD_HASH,
                is_active=True
            )
            session.add(mock_user)
            await session.commit()
            print("Mock user seeded successfully.")
        
        # 💥 NEW LOGIC: Always ensure the existing user has the latest configured hash
        else:
            if existing_user.password_hash != settings.MOCK_USER_A_PASSWORD_HASH:
                 print("Updating mock user's password hash in DB.")
                 existing_user.password_hash = settings.MOCK_USER_A_PASSWORD_HASH
                 existing_user.email = settings.MOCK_USER_A_EMAIL
                 session.add(existing_user)
                 await session.commit()
                 print("Mock user password updated.")
            else:
                print("Mock user already exists. Skipping seed.")

        print("Database initialization complete.")
