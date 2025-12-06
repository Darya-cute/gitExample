import json
import csv
import xml.etree.ElementTree as ET
import yaml
import os
from src.database.db import Database
from src.repository.repository import ClientRepository, ApplicationRepository, PollutionStatusRepository, \
    ApplicationStatusRepository


class DataExporter:
    def __init__(self):
        self.db = Database()
        self.client_repo = ClientRepository(self.db)
        self.application_repo = ApplicationRepository(self.db)
        self.pollution_repo = PollutionStatusRepository(self.db)
        self.status_repo = ApplicationStatusRepository(self.db)
        self.output_dir = "out"
        self._ensure_output_directory()

    def _ensure_output_directory(self):
        """Создает папку out, если её нет"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_application_data_with_relations(self):
        """Получает данные заявок с связанными данными"""
        applications = self.application_repo.find_all()
        result = []

        for app in applications:
            client = self.client_repo.find_by_id(app.Client_ID)
            pollution = self.pollution_repo.find_by_id(app.PollutionStatus_ID)
            status = self.status_repo.find_by_id(app.ApplicationStatus_ID)

            application_data = {
                "application_id": app.Application_ID,
                "number_of_items": app.Number_of_items,
                "time_of_receipt": app.Time_of_receipt,
                "client": {
                    "client_id": client.Client_ID if client else None,
                    "last_name": client.last_name if client else None,
                    "name": client.name if client else None,
                    "patronymic": client.patronymic if client else None,
                    "phone_number": client.phone_number if client else None,
                    "email": client.email if client else None
                },
                "pollution_status": {
                    "pollution_status_id": pollution.PollutionStatus_ID if pollution else None,
                    "name": pollution.name if pollution else None,
                    "comment": pollution.comment if pollution else None
                },
                "application_status": {
                    "application_status_id": status.ApplicationStatus_ID if status else None,
                    "name": status.name if status else None,
                    "comment": status.comment if status else None
                }
            }
            result.append(application_data)

        return result

    def export_to_json(self, data):
        """Экспорт в JSON"""
        with open(f"{self.output_dir}/data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def export_to_csv(self, data):
        """Экспорт в CSV"""
        with open(f"{self.output_dir}/data.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Заголовки
            writer.writerow([
                "application_id", "number_of_items", "time_of_receipt",
                "client_id", "client_name", "client_phone",
                "pollution_status", "application_status"
            ])

            # Данные
            for item in data:
                writer.writerow([
                    item["application_id"],
                    item["number_of_items"],
                    item["time_of_receipt"],
                    item["client"]["client_id"],
                    f"{item['client']['last_name']} {item['client']['name']}",
                    item["client"]["phone_number"],
                    item["pollution_status"]["name"],
                    item["application_status"]["name"]
                ])

    def export_to_xml(self, data):
        """Экспорт в XML"""
        root = ET.Element("applications")

        for item in data:
            app_elem = ET.SubElement(root, "application")

            ET.SubElement(app_elem, "id").text = str(item["application_id"])
            ET.SubElement(app_elem, "number_of_items").text = str(item["number_of_items"])
            ET.SubElement(app_elem, "time_of_receipt").text = str(item["time_of_receipt"])

            # Клиент
            client_elem = ET.SubElement(app_elem, "client")
            ET.SubElement(client_elem, "id").text = str(item["client"]["client_id"])
            ET.SubElement(client_elem, "last_name").text = item["client"]["last_name"]
            ET.SubElement(client_elem, "name").text = item["client"]["name"]
            ET.SubElement(client_elem, "patronymic").text = item["client"]["patronymic"]
            ET.SubElement(client_elem, "phone").text = str(item["client"]["phone_number"])
            ET.SubElement(client_elem, "email").text = item["client"]["email"]

            # Статус загрязнения
            pollution_elem = ET.SubElement(app_elem, "pollution_status")
            ET.SubElement(pollution_elem, "id").text = item["pollution_status"]["pollution_status_id"]
            ET.SubElement(pollution_elem, "name").text = item["pollution_status"]["name"]
            ET.SubElement(pollution_elem, "comment").text = item["pollution_status"]["comment"]

            # Статус заявки
            status_elem = ET.SubElement(app_elem, "application_status")
            ET.SubElement(status_elem, "id").text = item["application_status"]["application_status_id"]
            ET.SubElement(status_elem, "name").text = item["application_status"]["name"]
            ET.SubElement(status_elem, "comment").text = item["application_status"]["comment"]

        tree = ET.ElementTree(root)
        tree.write(f"{self.output_dir}/data.xml", encoding="utf-8", xml_declaration=True)

    def export_to_yaml(self, data):
        """Экспорт в YAML"""
        with open(f"{self.output_dir}/data.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def run(self):
        """Запуск экспорта"""
        print("Сбор данных из базы...")
        data = self.get_application_data_with_relations()

        if not data:
            print("Нет данных для экспорта!")
            return

        print(f"Найдено {len(data)} заявок")

        print("Экспорт в JSON: ")
        self.export_to_json(data)

        print("Экспорт в CSV: ")
        self.export_to_csv(data)

        print("Экспорт в XML: ")
        self.export_to_xml(data)

        print("Экспорт в YAML: ")
        self.export_to_yaml(data)

        print("Экспорт завершен! Файлы сохранены в папке 'out/'")


if __name__ == "__main__":
    exporter = DataExporter()
    exporter.run()