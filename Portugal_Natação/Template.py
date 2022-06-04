from bs4 import BeautifulSoup as bs
import requests
import csv

def find_name(soup):
    text = soup.find('class_='lead mb-0'').text.strip()
    index = text.find('(') # find the first instance of '(' because we only want the name for now
    if index == -1:
        return text
    return text[:index -1]
def find_address(soup):
    if soup.find(class_='address tight') is not None:
        text = soup.find(class_='address tight').get_text(separator=" ").strip()
        if text == '':
            return None
        return text
    return None
def find_city(soup):
    '''
    For city the format we use in the database is always City - Two letter acronym for state. It is important that cities
    always follow this format. Example:
    Los Angeles - CA
    New York - NY
    Baltimore - MD
    '''
    if soup.find(class_='address tight'):
        text = soup.find(class_='address tight').get_text(separator="||").strip()
        ind = text.find("||")
        if ind == -1:
            return None
        res = text[ind + 2:].split(',')
        return res[0] + ' -' + res[1][:3]
    return None
def find_state(city):
    if city is None:
        return None
    return city[-2:]
def find_phone(soup):
    all_data = soup.find_all(class_='tight')
    for data in all_data:
        if len(data.text) > 0:
            if data.text[0] == '(':    # this line checks if its a phone number
                return data.text
    return None
def find_email(soup):
    all_data = soup.find_all(class_='tight')
    for data in all_data:
        if '@' in data.text:
            return data.text
    return None
def find_website(soup):
    all_data = soup.find_all(class_='tight')
    for data in all_data:
        if soup.find('a'):
            return soup.find('a')['href']
    return None
def find_acronym(soup):
    text = soup.find(class_='lead mb-0').text.strip()
    index = text.find('(') # find the first instance of '(' because we only want the name for now
    if index == -1:
        return None
    return text[index + 1:-1]
def main():
    #this list will store every dictionary of each club
    my_list = []
    
    #used for iterating over pages. There are 60 pages of data  
    for i in range (1,61):   #1 to 61
        print(i)
       
        #requesting the data
        url = 'https://member.usafencing.org/clubs?page=' + str(i)
        req = requests.get(url)
        soup = bs(req.content)
        
        # Every club is in a "tr" tag. So I will separate each club first to make it easier
        all_clubs = soup.find_all('tr')
        
        for row in all_clubs[1:]:
            # This dict will store the information of each club
            my_dict = {}
            
            my_dict['name'] = find_name(row)
            my_dict['acronym']= find_acronym(row)
            my_dict['address'] = find_address(row)
            my_dict['city'] = find_city(row)
            my_dict['state'] = find_state(my_dict['city'])
            my_dict['phone'] = find_phone(row)
            my_dict['email'] = find_email(row)
            my_dict['website'] = find_website(row)
            
            #this are all the constants that must be added
            my_dict['country'] = 'United States of America'
            my_dict['Affilated'] = 'USA Fencing'
            my_dict['Recorded By'] = 'Cezar Pekelman'
            my_dict['Recorded Date'] = '10/10/2021'

            my_list.append(my_dict)
            
        
        i = i + 1
    
    return my_list
        
res = main()
res # this is what the output looks like as a list of dictionaries

#Exporting to CSV

keys = res[0].keys()


with open('US_fencing.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = keys
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(res)
    
csvfile.close()