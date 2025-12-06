from src.database.db import Database
from src.models.models import Client, Admin, Application, PollutionStatus, ApplicationStatus

class ClientRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Client_ID, last_name, name, patronymic, phone_number, email FROM Client')
        clients = []
        for row in cursor.fetchall():
            clients.append(Client(row[0], row[1], row[2], row[3], row[4], row[5]))
        conn.close()
        return clients

    def find_by_id(self, client_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Client_ID, last_name, name, patronymic, phone_number, email FROM Client WHERE Client_ID = ?',
            (client_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Client(row[0], row[1], row[2], row[3], row[4], row[5])
        return None

    def save(self, client):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if client.Client_ID:
            cursor.execute(
                'UPDATE Client SET last_name = ?, name = ?, patronymic = ?, phone_number = ?, email = ? WHERE Client_ID = ?',
                (client.last_name, client.name, client.patronymic, client.phone_number, client.email, client.Client_ID))
        else:
            cursor.execute(
                'INSERT INTO Client (last_name, name, patronymic, phone_number, email) VALUES (?, ?, ?, ?, ?)',
                (client.last_name, client.name, client.patronymic, client.phone_number, client.email))
            client.Client_ID = cursor.lastrowid
        conn.commit()
        conn.close()
        return client

class AdminRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT Admin_ID, last_name, name, patronymic, phone_number, email FROM Admin')
        admins = []
        for row in cursor.fetchall():
            admins.append(Admin(row[0], row[1], row[2], row[3], row[4], row[5]))
        conn.close()
        return admins

    def find_by_id(self, admin_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Admin_ID, last_name, name, patronymic, phone_number, email FROM Admin WHERE Admin_ID = ?',
            (admin_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Admin(row[0], row[1], row[2], row[3], row[4], row[5])
        return None

    def save(self, admin):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if admin.Admin_ID:
            cursor.execute(
                'UPDATE Admin SET last_name = ?, name = ?, patronymic = ?, phone_number = ?, email = ? WHERE Admin_ID = ?',
                (admin.last_name, admin.name, admin.patronymic, admin.phone_number, admin.email, admin.Admin_ID))
        else:
            cursor.execute(
                'INSERT INTO Admin (last_name, name, patronymic, phone_number, email) VALUES (?, ?, ?, ?, ?)',
                (admin.last_name, admin.name, admin.patronymic, admin.phone_number, admin.email))
            admin.Admin_ID = cursor.lastrowid
        conn.commit()
        conn.close()
        return admin

class ApplicationStatusRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT ApplicationStatus_ID, name, comment FROM ApplicationStatus')
        statuses = []
        for row in cursor.fetchall():
            statuses.append(ApplicationStatus(row[0], row[1], row[2]))
        conn.close()
        return statuses

    def find_by_id(self, status_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ApplicationStatus_ID, name, comment FROM ApplicationStatus WHERE ApplicationStatus_ID = ?',
            (status_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return ApplicationStatus(row[0], row[1], row[2])
        return None

class PollutionStatusRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT PollutionStatus_ID, name, comment FROM PollutionStatus')
        statuses = []
        for row in cursor.fetchall():
            statuses.append(PollutionStatus(row[0], row[1], row[2]))
        conn.close()
        return statuses

    def find_by_id(self, status_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT PollutionStatus_ID, name, comment FROM PollutionStatus WHERE PollutionStatus_ID = ?',
                       (status_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return PollutionStatus(row[0], row[1], row[2])
        return None

class ApplicationRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Application_ID, Client_ID, Number_of_items, PollutionStatus_ID, ApplicationStatus_ID FROM Application')
        applications = []
        for row in cursor.fetchall():
            applications.append(Application(row[0], row[1], row[2], row[3], row[4]))
        conn.close()
        return applications

    def find_by_client_id(self, client_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Application_ID, Client_ID, Number_of_items, PollutionStatus_ID, ApplicationStatus_ID FROM Application WHERE Client_ID = ?',
            (client_id,))
        applications = []
        for row in cursor.fetchall():
            applications.append(Application(row[0], row[1], row[2], row[3], row[4]))
        conn.close()
        return applications

    def save(self, application):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if application.Application_ID:
            cursor.execute(
                'UPDATE Application SET Client_ID = ?, Number_of_items = ?, PollutionStatus_ID = ?, ApplicationStatus_ID = ? WHERE Application_ID = ?',
                (application.Client_ID, application.Number_of_items, application.PollutionStatus_ID,
                 application.ApplicationStatus_ID, application.Application_ID))
        else:
            cursor.execute(
                'INSERT INTO Application (Client_ID, Number_of_items, PollutionStatus_ID, ApplicationStatus_ID) VALUES (?, ?, ?, ?)',
                (application.Client_ID, application.Number_of_items, application.PollutionStatus_ID,
                 application.ApplicationStatus_ID))
            application.Application_ID = cursor.lastrowid
        conn.commit()
        conn.close()
        return application

    def find_by_id(self, application_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT Application_ID, Client_ID, Number_of_items, PollutionStatus_ID, ApplicationStatus_ID FROM Application WHERE Application_ID = ?',
            (application_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Application(row[0], row[1], row[2], row[3], row[4])
        return None

    def update_status(self, application_id, status_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Application SET ApplicationStatus_ID = ? WHERE Application_ID = ?',
                       (status_id, application_id))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return affected_rows > 0




