from typing import Any, List

import psycopg2
from psycopg2 import sql


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения
     данных о вакансиях и компаниях."""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").
                format(sql.Identifier(database_name)))

    cur.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8'").
                format(sql.Identifier(database_name)))

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                company_id INT NOT NULL REFERENCES companies(company_id),
                title VARCHAR(255) NOT NULL,
                salary FLOAT,
                vacancy_url TEXT NOT NULL
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(vacancies: list[dict[str, Any]],
                          companies: list[dict[str, Any]],
                          database_name: str, params: dict) -> None:
    """Сохранение данных о вакансиях и компаниях в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for company in companies:
            cur.execute(
                """
                INSERT INTO companies (company_id, title)
                VALUES (%s, %s)
                ON CONFLICT (company_id) DO NOTHING
                """,
                (company['company_id'], company['title'])
            )

        for vacancy in vacancies:
            cur.execute(
                """
                INSERT INTO vacancies (vacancy_id, company_id,
                                       title, salary, vacancy_url)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (vacancy['vacancy_id'], vacancy['company_id'],
                 vacancy['title'], vacancy['salary'], vacancy['vacancy_url'])
                      )

    conn.commit()
    conn.close()


class DBManager:
    """Класс для сортировки данных"""
    def __init__(self, database_name: str, params: dict):
        """Инициализация"""
        self.database_name = database_name
        self.params = params

    def get_companies_and_vacancies_count(self) -> List:
        """Возвращает список компаний и количество вакансий у каждой."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                select c.title, count(v.vacancy_id) from companies c
                left join vacancies v on c.company_id=v.company_id
                group by c.title
                """
            )
            result = cur.fetchall()

        conn.close()
        return result

    def get_all_vacancies(self) -> List:
        """Возвращает список всех вакансий с указанием названия компании,
         названия вакансии и зарплаты и ссылки на вакансию."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                select v.title company,
                c.title vacancy,
                c.salary,
                c.vacancy_url
                from vacancies c
                left join companies v on c.company_id=v.company_id
                """
            )
            result = cur.fetchall()

        conn.close()
        return result

    def get_avg_salary(self) -> List:
        """Возвращает среднюю зарплату по вакансиям."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                select avg(c.salary)
                from vacancies c
                """
            )
            result = cur.fetchall()

        conn.close()
        return result

    def get_vacancies_with_higher_salary(self) -> List:
        """Возвращает список всех вакансий,
         у которых зарплата выше средней по всем вакансиям."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                select v.title company,
                c.title vacancy,
                c.salary,
                c.vacancy_url
                from vacancies c
                left join companies v on c.company_id=v.company_id
                where c.salary > (select avg(c.salary)
                from vacancies c)
                """
            )
            result = cur.fetchall()

        conn.close()
        return result

    def get_vacancies_with_keyword(self, keyword: str) -> List:
        """Возвращает список всех вакансий, в названии которых
         содержатся переданные в метод слова, например python."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                """
                select v.title company,
                c.title vacancy,
                c.salary,
                c.vacancy_url
                from vacancies c
                left join companies v on c.company_id=v.company_id
                where c.title ilike %s
                """, (keyword,)
            )
            result = cur.fetchall()

        conn.close()
        return result
