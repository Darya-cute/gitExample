import sqlite3
import os


class Database:
    def __init__(self, db_path = "laundry.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self.init_database()

    def get_connection(self):
        """Создает соединение с базой данных"""
        return sqlite3.connect(self.db_path)

    def _ensure_db_directory(self):
        """Создаёт директорию для БД, если ее нет"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def init_database(self):
        """Создание таблиц и ввод начальных данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица Client
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Client (
                Client_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT NOT NULL,
                name TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                phone_number NUMBER NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE
            )
        ''')

        # Таблица PollutionStatus
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS PollutionStatus (
                PollutionStatus_ID TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                comment TEXT  
            )       
        ''')

        #Таблица ApplicationStatus
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ApplicationStatus (
                ApplicationStatus_ID TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                comment TEXT
            )
        ''')

        # Таблица Application
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Application (
                Application_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Client_ID INTEGER NOT NULL,
                Number_of_items INTEGER NOT NULL,
                PollutionStatus_ID TEXT NOT NULL,
                ApplicationStatus_ID TEXT NOT NULL,
                FOREIGN KEY(Client_ID) REFERENCES Client(Client_ID),
                FOREIGN KEY(PollutionStatus_ID) REFERENCES PollutionStatus(PollutionStatus_ID),
                FOREIGN KEY(ApplicationStatus_ID) REFERENCES ApplicationStatus(ApplicationStatus_ID)
            )
        ''')

        #Таблица Admin
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Admin (
                Admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT NOT NULL,
                name TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                phone_number NUMBER NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE
            )
        ''')
        self._insert_initial_data(cursor) #Заполняет начальными данными
        conn.commit()
        conn.close()

    def _insert_initial_data(self, cursor):
        """Вставляет начальные данные в таблицу"""

        # Проверяем, есть ли уже данные в таблицах
        cursor.execute('SELECT COUNT(*) FROM Client')
        client_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM Admin')
        admin_count = cursor.fetchone()[0]

        # PollutionStatus
        pollution_statuses = [
            ('LOW', 'Небольшое' , 'Легкое загрязнение'),
            ('MEDIUM', 'Обычное' , 'Среднее/Обычное загрязнение'),
            ('HIGH', 'Сильное' , 'Сильное загрязнение'),
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO PollutionStatus (PollutionStatus_ID, name, comment) VALUES (?, ?, ?)',
            pollution_statuses
        )
        # ApplicationStatus
        application_statuses = [
            ('IN_PROGRESS', 'В обработке', 'Заявка в работе'),
            ('COMPLETED', 'Ожидание', 'Заявка ожидает оплаты'),
            ('CANCELLED', 'Отмена', 'Заявка отклонена')
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO ApplicationStatus (ApplicationStatus_ID, name, comment) VALUES (?, ?, ?)',
            application_statuses
        )
        # Client - вставляем только если таблица пустая
        if client_count == 0:
            clients = [
                ('Невская', 'Есения', 'Ивановна', 79161234567, 'nevskay@mail.ru'),
                ('Горячева', 'Мария', 'Сергеевна', 79167654321, 'goryacheva@mail.ru'),
                ('Федоров', 'Алексей', 'Владимирович', 79169998877, 'sidorov@mail.ru')
            ]
            cursor.executemany(
                'INSERT OR IGNORE INTO Client (last_name, name, patronymic, phone_number, email) VALUES (?, ?, ?, ?, ?)',
                clients
            )

        # Admin - вставляем только если таблица пустая
        if admin_count == 0:
            admins = [
                ('Макаров', 'Александр', 'Максимович', 79182356841, 'makarov@laundry.ru'),
                ('Погодина', 'Евгения', 'Васильевна', 79213894750, 'pogodina@laundry.ru'),
                ('Марычев', 'Павел', 'Аркадьевич', 79569786342, 'marychev@laundry.ru')
            ]
            cursor.executemany(
                'INSERT OR IGNORE INTO Admin (last_name, name, patronymic, phone_number, email) VALUES (?, ?, ?, ?, ?)',
                admins
            )