from src.database.db import Database
from src.repository.repository import ClientRepository, AdminRepository, ApplicationStatusRepository, \
    PollutionStatusRepository, ApplicationRepository
from src.models.models import Client, Admin, Application


class LaundrySystem:
    def __init__(self):
        self.db = Database()
        self.client_repo = ClientRepository(self.db)
        self.admin_repo = AdminRepository(self.db)
        self.application_repo = ApplicationRepository(self.db)
        self.pollution_status_repo = PollutionStatusRepository(self.db)
        self.application_status_repo = ApplicationStatusRepository(self.db)
        self.current_user = None
        self.user_type = None

        self.cleanup_duplicates()

    def get_all_clients(self):
        return self.client_repo.find_all()

    def get_client_by_id(self, client_id):
        return self.client_repo.find_by_id(client_id)

    def create_client(self, last_name, name, patronymic, phone_number, email):
        if not last_name or not last_name.strip():
            raise ValueError("Фамилия не может быть пустой")
        if not name or not name.strip():
            raise ValueError("Имя не может быть пустым")
        if not patronymic or not patronymic.strip():
            raise ValueError("Отчество не может быть пустым")
        client = Client(None, last_name, name, patronymic, phone_number, email)
        return self.client_repo.save(client)

    def delete_client(self, client_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        # Сначала удаляем связанные заявки
        cursor.execute('DELETE FROM Application WHERE Client_ID = ?', (client_id,))
        # Затем удаляем клиента
        cursor.execute('DELETE FROM Client WHERE Client_ID = ?', (client_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return affected_rows > 0

    def get_all_admins(self):
        return self.admin_repo.find_all()

    def create_admin(self, last_name, name, patronymic, phone_number, email):
        if not last_name or not last_name.strip():
            raise ValueError("Фамилия не может быть пустой")
        if not name or not name.strip():
            raise ValueError("Имя не может быть пустым")
        if not patronymic or not patronymic.strip():
            raise ValueError("Отчество не может быть пустым")
        admin = Admin(None, last_name, name, patronymic, phone_number, email)
        return self.admin_repo.save(admin)

    def delete_admin(self, admin_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Admin WHERE Admin_ID = ?', (admin_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return affected_rows > 0

    def get_all_applications(self):
        return self.application_repo.find_all()

    def get_applications_by_client(self, client_id):
        if not self.get_client_by_id(client_id):
            raise ValueError(f"Клиент с ID {client_id} не существует")
        return self.application_repo.find_by_client_id(client_id)

    def create_application(self, client_id, pollution_status_id, application_status_id, number_of_items):
        if not self.get_client_by_id(client_id):
            raise ValueError(f"Клиент с ID {client_id} не существует")
        if not self.pollution_status_repo.find_by_id(pollution_status_id):
            raise ValueError(f"Статус загрязнения {pollution_status_id} не существует")
        if not self.application_status_repo.find_by_id(application_status_id):
            raise ValueError(f"Статус заявки {application_status_id} не существует")
        if number_of_items <= 0:
            raise ValueError("Количество вещей должно быть положительным числом")
        application = Application(None, client_id, number_of_items, pollution_status_id, None, application_status_id)
        return self.application_repo.save(application)

    def update_application_status(self, application_id, status_id):
        if not self.application_repo.find_by_id(application_id):
            raise ValueError(f"Заявка с ID {application_id} не существует")
        if not self.application_status_repo.find_by_id(status_id):
            raise ValueError(f"Статус заявки {status_id} не существует")
        return self.application_repo.update_status(application_id, status_id)

    def delete_application(self, application_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Application WHERE Application_ID = ?', (application_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        return affected_rows > 0

    def cleanup_duplicates(self):
        """Очищает дублирующиеся записи клиентов и администраторов"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Удаляем дубликаты клиентов (оставляем запись с минимальным ID)
        cursor.execute('''
            DELETE FROM Client 
            WHERE Client_ID NOT IN (
                SELECT MIN(Client_ID) 
                FROM Client 
                GROUP BY phone_number
            )
        ''')
        # Удаляем дубликаты администраторов (оставляем запись с минимальным ID)
        cursor.execute('''
            DELETE FROM Admin 
            WHERE Admin_ID NOT IN (
                SELECT MIN(Admin_ID) 
                FROM Admin 
                GROUP BY phone_number
            )
        ''')
        conn.commit()
        conn.close()

    def get_all_pollution_statuses(self):
        return self.pollution_status_repo.find_all()

    def get_all_application_statuses(self):
        return self.application_status_repo.find_all()

    def authenticate_client(self, name, phone_number):
        clients = self.get_all_clients()
        for client in clients:
            if (client.name.lower() == name.lower() and
                    str(client.phone_number) == str(phone_number)):
                return client
        return None

    def authenticate_admin(self, name, phone_number):
        admins = self.get_all_admins()
        for admin in admins:
            if (admin.name.lower() == name.lower() and
                    str(admin.phone_number) == str(phone_number)):
                return admin
        return None

    def display_main_menu(self):
        print("\nДобро пожаловать в систему учета прачечной")
        print("1. Я - клиент")
        print("2. Я - администратор")
        print("3. Регистрация клиента")
        print("0. Выход")

    def display_client_menu(self):
        print(f"\nКлиент: {self.current_user.name} {self.current_user.last_name}")
        print("1. Создать заявку")
        print("2. Показать мои заявки")
        print("3. Редактировать профиль")
        print("4. Удалить профиль")
        print("5. Выйти")

    def display_admin_menu(self):
        print(f"\nАдминистратор: {self.current_user.name} {self.current_user.last_name}")
        print("1. Показать всех клиентов")
        print("2. Показать все заявки")
        print("3. Обновить статус заявки")
        print("4. Показать всех администраторов")
        print("5. Добавить администратора")
        print("6. Удалить администратора")
        print("7. Удалить клиента")
        print("8. Удалить заявку")
        print("9. Выйти")

    def _get_valid_input(self, prompt, validation_func, error_message):
        while True:
            try:
                value = input(prompt)
                if validation_func(value):
                    return value
                else:
                    print(f" {error_message}")
            except Exception as e:
                print(f" Ошибка ввода: {e}")

    def _validate_not_empty(self, value):
        return bool(value.strip())

    def _validate_phone(self, value):
        try:
            phone = int(value)
            return len(value) == 11 and value.startswith('7')
        except ValueError:
            return False

    def _validate_email(self, value):
        if not value:
            return True
        return '@' in value and '.' in value

    def _validate_number(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _validate_positive_number(self, value):
        try:
            return int(value) > 0
        except ValueError:
            return False

    def _validate_client_exists(self, value):
        if not self._validate_number(value):
            return False
        return self.get_client_by_id(int(value)) is not None

    def _validate_admin_exists(self, value):
        if not self._validate_number(value):
            return False
        admins = self.get_all_admins()
        for admin in admins:
            if admin.Admin_ID == int(value):
                return True
        return False

    def _validate_application_exists(self, value):
        if not self._validate_number(value):
            return False
        return self.application_repo.find_by_id(int(value)) is not None

    def _validate_pollution_status(self, value):
        return value in ['1', '2', '3']

    def _validate_application_status(self, value):
        return value in ['1', '2', '3']

    def client_login(self):
        print("\nВход клиента: ")

        # Показываем всех клиентов для справки
        print("\nСуществующие клиенты: ")
        clients = self.get_all_clients()
        if clients:
            for client in clients:
                print(f"Имя: {client.name}, Телефон: {client.phone_number}")
        else:
            print("Зарегистрированных клиентов нет")
        print("---")

        name = self._get_valid_input("Имя: ", self._validate_not_empty, "Имя не может быть пустым!")
        phone_number = self._get_valid_input("Номер телефона: ", self._validate_phone,
                                             "Неверный формат телефона! Пример: 79161234567")

        client = self.authenticate_client(name, phone_number)
        if client:
            self.current_user = client
            self.user_type = 'client'
            print(f"Успешный вход! Добро пожаловать, {client.name}!")
            return True
        else:
            print("Клиент не найден. Проверьте данные или зарегистрируйтесь.")
            return False

    def admin_login(self):
        print("\nВход администратора: ")

        # Показываем всех администраторов для справки
        print("\nСуществующие администраторы: ")
        admins = self.get_all_admins()
        if admins:
            for admin in admins:
                print(f"Имя: {admin.name}, Телефон: {admin.phone_number}")
        else:
            print("Администраторов нет в системе")
        print("---")

        name = self._get_valid_input("Имя: ", self._validate_not_empty, "Имя не может быть пустым!")
        phone_number = self._get_valid_input("Номер телефона: ", self._validate_phone,
                                             "Неверный формат телефона! Пример: 79161234567")

        admin = self.authenticate_admin(name, phone_number)
        if admin:
            self.current_user = admin
            self.user_type = 'admin'
            print(f"Успешный вход! Добро пожаловать, {admin.name}!")
            return True
        else:
            print("Администратор не найден. Проверьте данные.")
            return False

    def register_client(self):
        print("\nРегистрация клиента: ")
        last_name = self._get_valid_input("Фамилия: ", self._validate_not_empty, "Фамилия не может быть пустой!")
        name = self._get_valid_input("Имя: ", self._validate_not_empty, "Имя не может быть пустым!")
        patronymic = self._get_valid_input("Отчество: ", self._validate_not_empty, "Отчество не может быть пустым!")
        phone_number = self._get_valid_input("Номер телефона (11 цифр, начинается с 7): ", self._validate_phone,
                                             "Неверный формат телефона! Пример: 79161234567")
        email = self._get_valid_input("Email: ", self._validate_email,
                                      "Неверный формат email! Пример: example@mail.ru")
        try:
            client = self.create_client(last_name, name, patronymic, int(phone_number), email)
            print(f"Клиент зарегистрирован с ID: {client.Client_ID}")
            return client
        except Exception as e:
            print(f" Ошибка: {e}")
            return None

    def add_client(self):
        print("\nДобавление клиента: ")
        last_name = self._get_valid_input("Фамилия: ", self._validate_not_empty, "Фамилия не может быть пустой!")
        name = self._get_valid_input("Имя: ", self._validate_not_empty, "Имя не может быть пустым!")
        patronymic = self._get_valid_input("Отчество: ", self._validate_not_empty, "Отчество не может быть пустым!")
        phone_number = self._get_valid_input("Номер телефона (11 цифр, начинается с 7): ", self._validate_phone,
                                             "Неверный формат телефона! Пример: 79161234567")
        email = self._get_valid_input("Email: ", self._validate_email,
                                      "Неверный формат email! Пример: example@mail.ru")
        try:
            client = self.create_client(last_name, name, patronymic, int(phone_number), email)
            print(f" Клиент добавлен с ID: {client.Client_ID}")
        except Exception as e:
            print(f" Ошибка: {e}")

    def show_all_clients(self):
        print("\nВсе клиенты: ")
        clients = self.get_all_clients()
        if not clients:
            print("Клиенты не найдены")
        else:
            for client in clients:
                print(
                    f"ID: {client.Client_ID}, ФИО: {client.last_name} {client.name} {client.patronymic}, Телефон: {client.phone_number}, Email: {client.email}")

    def show_all_admins_info(self):
        """Показывает всех администраторов с их данными"""
        print("\nВсе администраторы: ")
        admins = self.get_all_admins()
        if not admins:
            print("Администраторы не найдены")
        else:
            for admin in admins:
                print(
                    f"ID: {admin.Admin_ID}, ФИО: {admin.last_name} {admin.name} {admin.patronymic}, "
                    f"Телефон: {admin.phone_number}, Email: {admin.email}"
                )

    def create_application_flow(self):
        print("\nСоздание заявки: ")

        pollution_status = self._get_valid_input(
            "\nСтатус загрязнения:\n1. Легкое загрязнение\n2. Среднее/Обычное загрязнение\n3. Сильное загрязнение\nВыберите статус загрязнения (1-3): ",
            self._validate_pollution_status, "Неверный выбор! Введите 1, 2 или 3")

        pollution_mapping = {
            '1': 'LOW',
            '2': 'MEDIUM',
            '3': 'HIGH'
        }
        pollution_status_id = pollution_mapping[pollution_status]

        app_status_id = 'IN_PROGRESS'

        number_of_items = self._get_valid_input("\nКоличество вещей: ", self._validate_positive_number,
                                                "Количество вещей должно быть положительным числом!")

        try:
            if self.user_type == 'client':
                client_id = self.current_user.Client_ID
            else:
                self.show_all_clients()
                client_id = self._get_valid_input("ID клиента: ", self._validate_client_exists,
                                                  "Неверный ID клиента или клиент не существует!")

            application = self.create_application(int(client_id), pollution_status_id, app_status_id,
                                                  int(number_of_items))
            print(f"Заявка создана с ID: {application.Application_ID}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def show_all_applications(self):
        print("\nВсе заявки: ")
        applications = self.get_all_applications()

        if not applications:
            print("Заявки не найдены")
        else:
            for app in applications:
                client = self.get_client_by_id(app.Client_ID)
                pollution = self.pollution_status_repo.find_by_id(app.PollutionStatus_ID)
                status = self.application_status_repo.find_by_id(app.ApplicationStatus_ID)
                client_name = f"{client.last_name} {client.name} {client.patronymic}" if client else "Неизвестный клиент"
                pollution_name = pollution.name if pollution else "Неизвестно"
                status_name = status.name if status else "Неизвестно"
                print(
                    f"Заявка ID: {app.Application_ID}, Клиент: {client_name}, Кол-во вещей: {app.Number_of_items}, Загрязнение: {pollution_name}, Статус: {status_name}, Время: {app.Time_of_receipt}")

    def show_client_applications(self):
        print("\nМои заявки:")
        try:
            if self.user_type == 'client':
                applications = self.get_applications_by_client(self.current_user.Client_ID)
            else:
                self.show_all_clients()
                client_id = self._get_valid_input("ID клиента: ", self._validate_client_exists,
                                                  "Неверный ID клиента или клиент не существует!")
                applications = self.get_applications_by_client(int(client_id))

            if not applications:
                print("Заявки не найдены")
            else:
                for app in applications:
                    pollution = self.pollution_status_repo.find_by_id(app.PollutionStatus_ID)
                    status = self.application_status_repo.find_by_id(app.ApplicationStatus_ID)
                    pollution_name = pollution.name if pollution else "Неизвестно"
                    status_name = status.name if status else "Неизвестно"
                    print(
                        f"Заявка ID: {app.Application_ID}, Кол-во вещей: {app.Number_of_items}, Загрязнение: {pollution_name}, Статус: {status_name}, Время: {app.Time_of_receipt}")
        except Exception as e:
            print(f"Ошибка: {e}")

    def update_application_status_flow(self):
        print("\nОбновление статуса заявки: ")
        self.show_all_applications()
        applications = self.get_all_applications()
        if not applications:
            print("Нет заявок для обновления!")
            return
        app_id = self._get_valid_input("ID заявки: ", self._validate_application_exists,
                                       "Неверный ID заявки или заявка не существует!")

        application_status = self._get_valid_input(
            "\nНовый статус заявки:\n1. В обработке\n2. Ожидает оплаты\n3. Отменена\nВыберите статус заявки (1-3): ",
            self._validate_application_status, "Неверный выбор! Введите 1, 2 или 3")

        application_mapping = {
            '1': 'IN_PROGRESS',
            '2': 'COMPLETED',
            '3': 'CANCELLED'
        }
        new_status = application_mapping[application_status]

        try:
            if self.update_application_status(int(app_id), new_status):
                print("Статус заявки обновлен")
            else:
                print("Ошибка обновления статуса")
        except Exception as e:
            print(f"Ошибка: {e}")

    def show_admins(self):
        print("\nАдминистраторы: ")
        admins = self.get_all_admins()
        if not admins:
            print("Администраторы не найдены")
        else:
            for admin in admins:
                print(
                    f"ID: {admin.Admin_ID}, ФИО: {admin.last_name} {admin.name} {admin.patronymic}, Телефон: {admin.phone_number}, Email: {admin.email}")

    def add_admin(self):
        print("\nДобавление администратора: ")
        last_name = self._get_valid_input("Фамилия: ", self._validate_not_empty, "Фамилия не может быть пустой!")
        name = self._get_valid_input("Имя: ", self._validate_not_empty, "Имя не может быть пустым!")
        patronymic = self._get_valid_input("Отчество: ", self._validate_not_empty, "Отчество не может быть пустым!")
        phone_number = self._get_valid_input("Номер телефона (11 цифр, начинается с 7): ", self._validate_phone,
                                             "Неверный формат телефона! Пример: 79161234567")
        email = self._get_valid_input("Email: ", self._validate_email,
                                      "Неверный формат email! Пример: example@mail.ru")
        try:
            admin = self.create_admin(last_name, name, patronymic, int(phone_number), email)
            print(f" Администратор добавлен с ID: {admin.Admin_ID}")
        except Exception as e:
            print(f" Ошибка: {e}")

    def delete_client_flow(self):
        print("\nУдаление клиента: ")
        self.show_all_clients()
        client_id = self._get_valid_input("ID клиента для удаления: ", self._validate_client_exists,
                                          "Неверный ID клиента или клиент не существует!")
        try:
            if self.delete_client(int(client_id)):
                print("Клиент успешно удален")
            else:
                print("Ошибка удаления клиента")
        except Exception as e:
            print(f"Ошибка: {e}")

    def delete_admin_flow(self):
        print("\nУдаление администратора: ")
        self.show_admins()
        admin_id = self._get_valid_input("ID администратора для удаления: ", self._validate_admin_exists,
                                         "Неверный ID администратора или администратор не существует!")
        try:
            if self.delete_admin(int(admin_id)):
                print("Администратор успешно удален")
            else:
                print("Ошибка удаления администратора")
        except Exception as e:
            print(f"Ошибка: {e}")

    def delete_application_flow(self):
        print("\nУдаление заявки: ")
        self.show_all_applications()
        app_id = self._get_valid_input("ID заявки для удаления: ", self._validate_application_exists,
                                       "Неверный ID заявки или заявка не существует!")
        try:
            if self.delete_application(int(app_id)):
                print("Заявка успешно удалена")
            else:
                print("Ошибка удаления заявки")
        except Exception as e:
            print(f"Ошибка: {e}")

    def edit_client_profile(self):
        print("\nРедактирование профиля: ")
        print(f"Текущие данные: {self.current_user.last_name} {self.current_user.name} {self.current_user.patronymic}")

        last_name = self._get_valid_input("Новая фамилия: ", self._validate_not_empty, "Фамилия не может быть пустой!")
        name = self._get_valid_input("Новое имя: ", self._validate_not_empty, "Имя не может быть пустым!")
        patronymic = self._get_valid_input("Новое отчество: ", self._validate_not_empty,
                                           "Отчество не может быть пустым!")
        phone_number = self._get_valid_input("Новый номер телефона: ", self._validate_phone,
                                             "Неверный формат телефона! Пример: 79161234567")
        email = self._get_valid_input("Новый email: ", self._validate_email,
                                      "Неверный формат email! Пример: example@mail.ru")

        try:
            self.current_user.last_name = last_name
            self.current_user.name = name
            self.current_user.patronymic = patronymic
            self.current_user.phone_number = int(phone_number)
            self.current_user.email = email

            self.client_repo.save(self.current_user)
            print("Профиль успешно обновлен")
        except Exception as e:
            print(f"Ошибка: {e}")

    def delete_own_profile(self):
        confirm = input("Вы уверены, что хотите удалить свой профиль? (да/нет): ")
        if confirm.lower() == 'да':
            try:
                if self.delete_client(self.current_user.Client_ID):
                    print("Ваш профиль успешно удален")
                    self.current_user = None
                    self.user_type = None
                    return True
                else:
                    print("Ошибка удаления профиля")
            except Exception as e:
                print(f"Ошибка: {e}")
        return False

    def run_client_session(self):
        while True:
            self.display_client_menu()
            choice = input("Выберите действие: ")
            try:
                if choice == '1':
                    self.create_application_flow()
                elif choice == '2':
                    self.show_client_applications()
                elif choice == '3':
                    self.edit_client_profile()
                elif choice == '4':
                    if self.delete_own_profile():
                        return
                elif choice == '5':
                    self.current_user = None
                    self.user_type = None
                    print("Выход из аккаунта клиента")
                    return
                else:
                    print("Неверный выбор")
            except Exception as e:
                print(f"Ошибка: {e}")

    def run_admin_session(self):
        while True:
            self.display_admin_menu()
            choice = input("Выберите действие: ")
            try:
                if choice == '1':
                    self.show_all_clients()
                elif choice == '2':
                    self.show_all_applications()
                elif choice == '3':
                    self.update_application_status_flow()
                elif choice == '4':  # Новый пункт - показать всех администраторов
                    self.show_all_admins_info()
                elif choice == '5':
                    self.add_admin()
                elif choice == '6':
                    self.delete_admin_flow()
                elif choice == '7':
                    self.delete_client_flow()
                elif choice == '8':
                    self.delete_application_flow()
                elif choice == '9':
                    self.current_user = None
                    self.user_type = None
                    print("Выход из аккаунта администратора")
                    return
                else:
                    print("Неверный выбор")
            except Exception as e:
                print(f"Ошибка: {e}")

    def run(self):
        while True:
            self.display_main_menu()
            choice = input("Выберите действие: ")
            try:
                if choice == '1':
                    if self.client_login():
                        self.run_client_session()
                elif choice == '2':
                    if self.admin_login():
                        self.run_admin_session()
                elif choice == '3':
                    client = self.register_client()
                    if client:
                        self.current_user = client
                        self.user_type = 'client'
                        self.run_client_session()
                elif choice == '0':
                    print("Выход из системы")
                    break
                else:
                    print("Неверный выбор")
            except Exception as e:
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    system = LaundrySystem()
    system.run()