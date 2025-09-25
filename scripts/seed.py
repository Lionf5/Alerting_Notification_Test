from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.models.user import Team, User


async def main() -> None:
    async with SessionLocal() as session:  # type: AsyncSession
        eng = Team(name="Engineering")
        mkt = Team(name="Marketing")
        session.add_all([eng, mkt])
        await session.flush()

        session.add_all(
            [
                User(name="Alice", team_id=eng.id),
                User(name="Bob", team_id=eng.id),
                User(name="Cara", team_id=mkt.id),
            ]
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())


