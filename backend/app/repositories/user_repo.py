from typing import Optional

from beanie import PydanticObjectId

from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)


class UserRepository:
    async def create(
        self,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
        )
        await user.insert()
        logger.info("User created", user_id=str(user.id))
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        return await User.get(PydanticObjectId(user_id))

    async def get_by_email(self, email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    async def exists_by_email(self, email: str) -> bool:
        return await User.find_one(User.email == email) is not None

    async def count(self) -> int:
        return await User.count()


user_repo = UserRepository()
