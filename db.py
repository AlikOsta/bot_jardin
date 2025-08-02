import aiosqlite
import asyncio

DB_NAME = "data.db"

AGE_GROUPS = ["2-3 года", "3-4 года", "4-5 лет", "5-7 лет"]
SHIFTS = ["Утро", "Вечер", "Полный день"]

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_telegram INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT,
            username TEXT NOT NULL, 
            is_staff BOOLEAN NOT NULL
        );
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age_group TEXT NOT NULL,
            shift TEXT NOT NULL,
            available BOOLEAN NOT NULL
        );
        """)

        cursor = await db.execute("SELECT COUNT(*) FROM slots")
        count = (await cursor.fetchone())[0]
        if count == 0:
            for age in AGE_GROUPS:
                for shift in SHIFTS:
                    await db.execute("""
                    INSERT INTO slots (age_group, shift, available)
                    VALUES (?, ?, ?)
                    """, (age, shift, True))
            print("Таблица заполнена начальными значениями.")
        else:
            print("Таблица уже содержит данные.")

        await db.commit()


async def get_availability(age_group: str, shift: str) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT available FROM slots WHERE age_group = ? AND shift = ?",
            (age_group, shift)
        )
        row = await cursor.fetchone()
        return bool(row[0]) if row else None


async def set_availability(age_group: str, shift: str, value: bool):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "UPDATE slots SET available = ? WHERE age_group = ? AND shift = ?",
            (int(value), age_group, shift)
        )
        await db.commit()
        

async def add_user(id_telegram: int, first_name: str, last_name: str, username: str | None, is_staff: bool = False):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users (id_telegram, first_name, last_name, username, is_staff)
            VALUES (?, ?, ?, ?, ?)
        """, (id_telegram, first_name, last_name, username, int(is_staff)))
        await db.commit()


async def get_user(id_telegram: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE id_telegram = ?",
            (id_telegram,)
        )
        row = await cursor.fetchone()
        return row
    

async def get_user_id(username:str) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id_telegram FROM users WHERE username = ?",
            (username,)
        )
        row = await cursor.fetchone()
        if row is None:
            return False 
        return row[0]


async def get_is_staff(id_telegram: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT is_staff FROM users WHERE id_telegram = ?",
            (id_telegram,)
        )
        row = await cursor.fetchone()
        if row is None:
            return False 
        return bool(row[0])
    

async def all_staff():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id_telegram, first_name, last_name, username FROM users WHERE is_staff = 1"
        )
        rows = await cursor.fetchall()
        return rows 


async def set_is_staff(id_telegram: int, value: bool):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "UPDATE users SET is_staff = ? WHERE id_telegram = ?",
            (int(value), id_telegram)
        )
        await db.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
