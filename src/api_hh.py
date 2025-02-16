from typing import List

import requests


class HeadHunterAPI:
    """
    Класс для работы с API HeadHunter
    """

    def __init__(self) -> None:
        """Инициализация"""
        self.url = 'https://api.hh.ru/vacancies'
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.employers = [2180, 673, 84585, 3529, 1740,
                          15478, 588914, 49357, 9352463, 3776]  # ID компаний
        self.vacancies = []
        self.companies = []

    def load_vacancies(self) -> None:
        """Получение вакансий"""

        for employer_id in self.employers:
            params = {
                "employer_id": employer_id,
                "per_page": 2,  # Запрашиваем сразу 2 вакансии
                "page": 0,
                # "text": "Python",  # Поиск вакансий с Python в названии
                # "search_field": "name",
            }

            try:
                response = requests.get(self.url,
                                        headers=self.headers, params=params)
                # Бросает исключение, если статус-код не 200-299
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Произошла ошибка {e}")
            else:
                if response.status_code == 200:
                    vacancies = response.json().get("items", [])
                    if not vacancies:  # Если нет вакансий, выходим из цикла
                        break

                    for vacancy in vacancies:
                        self.vacancies.append({
                            "vacancy_id": vacancy["id"],
                            "company_id": vacancy["employer"]["id"],
                            "title": vacancy["name"],
                            "salary": self.format_salary(vacancy["salary"]),
                            "vacancy_url": vacancy["alternate_url"]
                        })

                    company_info = \
                        {"company_id": vacancies[0]["employer"]["id"],
                         "title": vacancies[0]["employer"]["name"]}
                    if company_info not in self.companies:
                        self.companies.append(company_info)

    def format_salary(self, salary: dict) -> float | None:
        """Форматирование зарплаты (если её нет, возвращаем None)"""
        if not salary:
            return None
        if salary["from"] and salary["to"]:
            return (salary['from']+salary['to'])/2
        if salary["from"]:
            return salary['from']
        if salary["to"]:
            return salary['to']
        return None

    def get_vacancies(self) -> List:
        """Получение вакансий"""
        return self.vacancies

    def get_companies(self) -> List:
        """Получение вакансий"""
        return self.companies
