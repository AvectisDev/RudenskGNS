import asyncpg
from datetime import datetime

DB_CRD = {'name': 'PinskGNS', 'host': 'localhost', 'user': 'postgres', 'password': '.avectis1', 'port': '5432'}


async def write_balloons_amount(reader_number: int):
    """Функция записывает в базу данных количество баллонов, пройденных через каждый считыватель"""
    try:
        conn = await asyncpg.connect(
            database=DB_CRD['name'],
            host=DB_CRD['host'],
            user=DB_CRD['user'],
            password=DB_CRD['password'],
            port=DB_CRD['port']
        )

        current_date = datetime.now()
        select_query = """SELECT * 
                          FROM public.filling_station_balloonamount 
                          WHERE reader_id = $1 AND change_date = $2"""

        select_data = await conn.fetch(select_query, reader_number, current_date.date())

        if len(select_data) == 0:  # если данных еще нет в базе
            insert_query = """INSERT INTO filling_station_balloonamount 
                              (reader_id, amount_of_balloons, change_date, change_time) 
                              VALUES ($1, $2, $3, $4)"""
            await conn.execute(insert_query, reader_number, 1, current_date.date(), current_date.time())
            print("Amount added to database")
        else:
            update_query = """UPDATE public.filling_station_balloonamount 
                              SET amount_of_balloons = amount_of_balloons + 1, change_time = $1 
                              WHERE reader_id = $2 AND change_date = $3"""
            await conn.execute(update_query, current_date.time(), reader_number, current_date.date())
            print("Data updated")

    except Exception as e:
        print('Can`t establish connection to database:', e)

    finally:
        await conn.close()
