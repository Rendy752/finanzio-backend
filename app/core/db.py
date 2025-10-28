from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy.future import select
from uuid import UUID 

# Import dependencies for user seeding
from app.core.config import settings, MOCK_USER_A_ID
from app.core.base import Base 
from app.models.user import User # Import User model
from app.models.category import Category, TransactionType # Import Category model
from app.crud.user import get_password_hash # Import password hashing utility

# --- Database Setup ---
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)

# NOTE: Mengubah AsyncSessionLocal menjadi async_sessionmaker (best practice modern)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Dependency Injection Functions ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session for endpoints."""
    # Koneksi yang digunakan oleh endpoints API
    async with AsyncSessionLocal() as session:
        yield session

# Function to initialize database tables AND seed mock data
async def init_db():
    """Initializes the database by creating all defined tables and seeding mock user data."""
    
    # 1. Block DDL (Create Tables)
    async with engine.begin() as conn:
        print("Initializing database...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database structure created.")

    # 2. Block DML (Seeding) - Menggunakan koneksi langsung yang aman
    # Kita menggunakan koneksi baru dari engine untuk isolasi
    async with engine.begin() as conn:
        # Gunakan AsyncSession yang terikat pada transaksi koneksi ini (conn)
        session = AsyncSession(bind=conn)
        mock_user_id = MOCK_USER_A_ID
        
        # --- Seed Mock User ---
        user_result = await session.execute(
            select(User).where(User.user_id == mock_user_id)
        )
        existing_user = user_result.scalars().first()
        
        # Gunakan password hash yang benar
        hashed_password = get_password_hash(settings.MOCK_USER_A_PASSWORD)
        
        if not existing_user:
            print(f"Seeding mock user: {mock_user_id}")
            
            mock_user = User(
                user_id=mock_user_id,
                email=settings.MOCK_USER_A_EMAIL,
                # Menggunakan password hash yang benar dari settings
                password_hash=hashed_password, 
                is_active=True
            )
            session.add(mock_user)
            print("Mock user seeded successfully.")
        
        # --- Update User/Password Hash jika sudah ada (untuk testing) ---
        else:
            if existing_user.password_hash != hashed_password:
                print("Updating mock user's password hash in DB.")
                existing_user.password_hash = hashed_password
                existing_user.email = settings.MOCK_USER_A_EMAIL
                session.add(existing_user)
                print("Mock user password updated.")
            else:
                print("Mock user already exists. Skipping seed.")

        # --- Seed System Categories (untuk Transfer Logic) ---
        transfer_categories = [
            (UUID('ffffffff-0000-0000-0000-000000000001'), "Transfer In", TransactionType.INCOME),
            (UUID('ffffffff-0000-0000-0000-000000000002'), "Transfer Out", TransactionType.EXPENSE)
        ]

        for id, name, type in transfer_categories:
            cat_exists = await session.execute(select(Category.category_id).where(Category.category_id == id))
            if not cat_exists.scalar_one_or_none():
                system_cat = Category(
                    category_id=id,
                    user_id=None, # System Category
                    category_name=name,
                    type=type
                )
                session.add(system_cat)
        
        # Session commit dilakukan, dan transaksi di-commit oleh engine.begin()
        await session.commit()
        print("System transfer categories ensured.")
        
        # Session ditutup secara otomatis saat keluar dari context manager

    print("Database initialization complete.")
