import requests
from bs4 import BeautifulSoup as bSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By


def write_csv(list_of_companies_data):
    with open('companies.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'website', 'phone', 'tels']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in list_of_companies_data:
            writer.writerow(item)


def get_html(url):
    r = requests.get(url)
    if r.ok:
        return r.text
    print(r.status_code)


def get_page_data(html):
    company_list = []
    soup = bSoup(html, 'lxml')
    companies = soup.find('ul', class_='logotypes-squares').find_all('li')
    for company in companies:
        name = company.find('a').find('h5').text
        company_url = 'https://www.work.ua' + company.find('a').get('href')
        data = {'name': name, 'url': company_url}
        company_list.append(data)
    return company_list


def get_company_data(list_of_companies):
    list_of_companies_data = []
    for item in list_of_companies:
        new_request = requests.get(item['url'])
        if new_request.ok:
            company_soup = bSoup(new_request.text, 'lxml')
            name_of_company = company_soup.find('h1').text
            website_of_company = company_soup.find('span', class_='website-company')
            if website_of_company:
                website = website_of_company.find('a').get('href')
            else:
                website = None
            glyphicon_phone = company_soup.find('span', class_='glyphicon-phone')
            if glyphicon_phone:
                tel_contact = glyphicon_phone.find_parent('p')
            else:
                tel_contact = None
            if tel_contact:
                tel_a = tel_contact.find('a')
            else:
                tel_a = None
            if tel_a:
                tel = tel_a.text
            else:
                tel = None
            vacancies_link = []
            job_links = company_soup.find_all('div', class_='job-link')
            for new_item in job_links:
                a_name = 'https://www.work.ua' + new_item.find('h2').find('a').get('href')
                vacancies_link.append(a_name)
                tels = []
                for vacancy in vacancies_link:
                    driver = webdriver.Firefox()
                    driver.get(vacancy)
                    try:
                        driver.find_element(By.CSS_SELECTOR, ".link-phone > span").click()
                        tel_a = driver.find_element(By.CSS_SELECTOR, "#contact-phone").text
                    except Exception:
                        tel_a = None
                    driver.quit()
                    tels.append(tel_a)
            data_company = {'name': name_of_company, 'website': website, 'phone': tel, 'tels': tels}
            list_of_companies_data.append(data_company)
    return list_of_companies_data


def main():
    url = 'https://www.work.ua/ru/jobs/by-company/'
    html = get_html(url)
    all_list = get_page_data(html)
    print(all_list)
    print_list = get_company_data(all_list)
    print(print_list)
    write_csv(print_list)


if __name__ == '__main__':
    main()