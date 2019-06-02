from bs4 import BeautifulSoup
from time import gmtime, strftime
import unidecode
import requests
import csv


def get_html(user_session, user_id, user_page=None):
    request_url = 'https://xn--80aaahi2bjaklrrng.xn--p1ai/cardsystem/'

    response = user_session.post(request_url, data={'view': 'login', 'username': str(user_id)})
    # print('Получена главная страница для пользователя %d' % user_id)

    if (user_page):
        params = '?view=cards&card_id=%d&from=&to=&page=%d' % (user_id, user_page)
        response = user_session.get(request_url)
        # print('Получена страница №%d для пользователя %d' % (user_page, user_id))

    return (response.text)


def parse_user_data(response_data):
    user_data = {'Customer': [], 'Transactions': []}

    analyzer_soup = BeautifulSoup(response_data, features='lxml')
    if (not analyzer_soup.find('div', {'class': 'card-info'})):
        # print('Пользователь %d не найден!', user_id)
        return (None)

    client_id = int(analyzer_soup.find('div', {'class': 'card-info'}).find_all('b')[1].text.strip())
    client_balance = analyzer_soup.find('div', {'class': 'card-info'}).find_all('b')[0].text.strip()
    user_data['Customer'].append([client_id, client_balance])

    data_table = analyzer_soup.find_all('tr')[1:]
    transaction_list = []
    for row in data_table:
        transaction = []
        date_time_id = unidecode.unidecode(row.find_all('td')[0].text).strip()

        transaction.append(date_time_id[date_time_id.rfind(' '):].strip())  # Transaction ID
        transaction.append(
            date_time_id[0:date_time_id.index(' ', date_time_id.find(' ') + 1)].strip())  # Transaction DateTime
        transaction.append(client_id)  # Client ID
        transaction.append(row.find_all('td')[1].text.strip())  # Transaction Bill Number
        transaction.append(row.find_all('td')[2].text.strip())  # Transaction Amount
        transaction.append(row.find_all('td')[4].text.strip())  # Transaction Comment

        transaction_list.append(transaction)

    user_data['Transactions'] = transaction_list
    return user_data


def write_csv(data, path, init=False):
    with open(path, mode='a', newline='', encoding="utf-8") as loyality_data:
        loyality_writer = csv.writer(loyality_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if (init):
            loyality_writer.writerow(data)
        else:
            for item in data:
                loyality_writer.writerow(item)


def get_user_data(user_id):
    with requests.Session() as s:

        response_data = get_html(s, user_id)
        user_data = parse_user_data(response_data)

        if (not user_data or user_data['Customer'] == None):
            print('Пользователь %d не найден!' % user_id)
        else:
            write_csv(user_data['Customer'], 'D:/synd_data/customer_data.csv')
            write_csv(user_data['Transactions'], 'D:/synd_data/loyality_data.csv')
            for page_index in range(2, 999):
                response_data = get_html(s, user_id, page_index)
                user_data = parse_user_data(response_data)

                if (user_data):
                    write_csv(user_data['Transactions'], 'D:/synd_data/loyality_data.csv')
                else:
                    break
            print('Прочитан и занесен пользователь %d' % user_id)