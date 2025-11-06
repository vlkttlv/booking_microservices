from sqlalchemy import delete, select, insert, update
from users_service.db import async_session_maker
from users_service.models import RefreshToken, Users
from sqlalchemy.exc import SQLAlchemyError

class UsersDAO:

    model = Users

    @classmethod
    async def find_by_id(cls, model_id: int):
        '''
        Находит одну запись в БД по номеру id
        '''
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        '''
        Находит одну запись в БД c условиями
        '''
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()


    @classmethod
    async def add(cls, **data):
        '''
        Добавляет запись в БД
        '''
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            res = await session.execute(query)
            await session.commit()  # фиксирует изменения в БД, обязательно
            new_id = res.scalar()  # Получаем id новой записи
            return new_id  # Возвращаем id


class RefreshTokenDAO(UsersDAO):

    model = RefreshToken

    @classmethod
    async def update_token(cls, created_at, expires_at, token, user_id: int):
        """
        Обновляет refresh токен в БД

        -Аргументы:
            created_at: время создания токена
            expires_at: время истечения жизни токена
            user_id: индетификатор пользователя
            token: токен
        """
        async with async_session_maker() as session:
            stmt = (
                update(cls.model)
                .where(cls.model.user_id == user_id)
                .values(created_at=created_at, expires_at=expires_at, token=token)
            )
            await session.execute(stmt)
            await session.commit()


    @classmethod
    async def delete(cls, **filter_by):
        """
        Удаляет запись из таблицы БД
        """
        async with async_session_maker() as new_session:
            async with new_session.begin():
                stmt = delete(cls.model).filter_by(**filter_by)
                await new_session.execute(stmt)

