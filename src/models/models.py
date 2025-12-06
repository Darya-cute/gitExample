class Client:
    """
    Модель для таблицы Clients
    Поля:
    - id: уникальный идентификатор клиента (PK)
    - last_name: фамилия клиента
    - name: имя клиента
    - patronymic: отчество клиента
    - phone_number: номер телефона клиента
    - email: почта клиента
    """
    def __init__(self, id, last_name, name, patronymic, phone_number, email):
        self.Client_ID = id
        self.last_name = last_name
        self.name = name
        self.patronymic = patronymic
        self.phone_number = phone_number
        self.email = email

class Admin:
    """
    Модель для таблицы Admins
    Поля:
    - id: уникальный идентификатор админа (PK)
    - last_name: фамилия админа
    - name: имя админа
    - patronymic: отчество админа
    - phone_number: номер телефона админа
    - email: почта админа
    """
    def __init__(self, id, last_name, name, patronymic, phone_number, email):
        self.Admin_ID = id
        self.last_name = last_name
        self.name = name
        self.patronymic = patronymic
        self.phone_number = phone_number
        self.email = email

class ApplicationStatus:
    """
    Модель для таблицы Application Status
    Поля:
    - id: уникальный идентификатор статуса заявки (PK)
    - name: короткое название заявки
    - comment: статусы заявок
    """
    def __init__(self, id, name, comment):
        self.ApplicationStatus_ID = id
        self.name = name
        self.comment = comment

class PollutionStatus:
    """
    Модель для таблицы PollutionStatus
    Поля:
    - id: уникальный идентификатор степени загрязнения (PK)
    - name: короткое название степени загрязнения
    - comment: статусы заявок
    """
    def __init__(self, id, name, comment):
        self.PollutionStatus_ID = id
        self.name = name
        self.comment = comment

class Application:
    """
    Модель для таблицы Applications
    Поля:
    - id: уникальный идентификатор заявки (PK)
    - client_ID: уникальный идентификатор клиента (FK)
    - number_of_items: количество вещей в заявке (FK)
    - pollutionStatus_ID: степень загрязнения
    - applicationStatus_ID: статус заявки (FK)
    """
    def __init__(self, id, client_ID, number_of_items, pollutionStatus_ID, applicationStatus_ID):
        self.Application_ID = id
        self.Client_ID = client_ID
        self.Number_of_items = number_of_items
        self.PollutionStatus_ID = pollutionStatus_ID
        self.ApplicationStatus_ID = applicationStatus_ID

