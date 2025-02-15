from utils.API_hh import HeadHunterAPI
from src.DBManager import create_database, save_data_to_database, DBManager
from config import config


def main() -> None:
    hh_api = HeadHunterAPI()
    hh_api.load_vacancies()
    vacancies = hh_api.get_vacancies()
    companies = hh_api.get_companies()
    params = config()
    create_database('hh', params)
    save_data_to_database(vacancies, companies, 'hh', params)
    db_data = DBManager('hh', params)
    print(f'Список компаний и количество вакансий у каждой: {db_data.get_companies_and_vacancies_count()}')
    print(f'Список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.: {db_data.get_all_vacancies()}')
    print(f'средняя зарплата по вакансиям: {db_data.get_avg_salary()}')
    print(f'Список всех вакансий, у которых зарплата выше средней по всем вакансиям: {db_data.get_vacancies_with_higher_salary()}')
    print(f'Список всех вакансий, в названии которых содержатся переданные в метод слова, например python: {db_data.get_vacancies_with_keyword()}')



if __name__ == '__main__':
    main()