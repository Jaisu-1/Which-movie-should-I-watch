#Step 1: Scrape imdb with parameters
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import time, sleep
from random import randint
from warnings import warn

url = "https://www.imdb.com/search/title?title_type=feature&release_date=2000-01-01,2000-12-31&num_votes=10000,&languages=en&sort=user_rating,desc"

response = get(url)
html_soup = BeautifulSoup(response.text, 'html.parser')
movie_container = html_soup.find_all('div',class_ = "lister-item mode-advanced")

"""
Step 2: Ask for the right parameters and scrape those values, take as many features as possible for data analysis

The parameters:
    1. Genre
    2. Runtime
    3. Certificate
    4. Votes
    5. Gross
    6. Director
    7. Billings
    8. Name of movie
    9. Year
    10. imdb rating
    11. metascore rating
"""


#Storing all the movies in a particular calender
names = []
years = []
imdb_ratings = []
metascores = []
votes = []
genres = []
runtimes = []
certifications = []
num_votes = []
revenues = []

director = []
Billings = []


pages = [str(i) for i in range(1,5)]
years_url = [str(i) for i in range(1980,2018)]


headers = {"Accept-Language": "en-US, en;q=0.5"}

# Preparing the monitoring of the loop
start_time = time()
requests = 0

# For every year in the interval 2000-2017
for year_url in years_url:

    # For every page in the interval 1-4
    for page in pages:

        # Make a get request
        response = get('http://www.imdb.com/search/title?release_date=' + year_url + 
        '&sort=num_votes,desc&page=' + page, headers = headers)

        # Pause the loop
        sleep(randint(8,15))

        # Monitor the requests
        requests += 1
        elapsed_time = time() - start_time
        print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))

        # Throw a warning for non-200 status codes
        if response.status_code != 200:
            warn('Request: {}; Status code: {}'.format(requests, response.status_code))

        # Break the loop if the number of requests is greater than expected
        if requests > 72:
            warn('Number of requests was greater than expected.')  
            break 

        # Parse the content of the request with BeautifulSoup
        page_html = BeautifulSoup(response.text, 'html.parser')
        
        # Select all the 50 movie containers from a single page
        movie_container = page_html.find_all('div', class_ = 'lister-item mode-advanced')

        for movie in movie_container:

            if movie.find('div', class_ = 'ratings-metascore') is not None:

                #The name
                name = movie.h3.a.text
                names.append(name)

                #The year
                year = movie.h3.find('span',class_ = 'lister-item-year').text
                years.append(year)

                #The imdb rating
                rating = float(movie.strong.text)
                imdb_ratings.append(rating)

                #The Metascore
                m_score = movie.find('span', class_ = 'metascore').text
                metascores.append(int(m_score))

                #The genre
                movie_genre = movie.find("span", class_ = "genre").text
                genres.append(movie_genre)

                #The runtime
                movie_runtime = movie.find("span", class_ = "runtime").text
                runtimes.append(movie_runtime)

                #The certificate
                movie_cert = movie.find("span", class_ = "certificate")
                if movie_cert is not None:
                    certifications.append(movie_cert.text)
                else:
                    certifications.append("-")

                #The number of votes 
                numbers = movie.find("p", class_ = "sort-num_votes-visible")
                votes_text = numbers.find("span", "text-muted")
                Nums_children = [x for x in votes_text.parent.children if (x != '\n' and x != ' ')]
                votes = Nums_children[1]['data-value']
                num_votes.append(float(votes))

                #The gross of the movie
                Gross =  Nums_children[-1]['data-value'].strip('\'"')
                Gross = Gross.replace(",","") 
                revenues.append(float(Gross))

                #The director of the movie
                first_movie_content = movie.find("div", class_ = "lister-item-content")
                director_name = first_movie_content.find("a", href = re.compile(r'.*dr.*')).text
                director.append(director_name)


                #The stars of the movie
                billings_list = first_movie_content.find_all("a", href = re.compile(r'.*li_st.*'))
                billings = [i.text for i in billings_list]
                Billings.append(billings)



test_df = pd.DataFrame({'Movie': names,
                        'Year':years,
                        'Imdb':imdb_ratings,
                        'Metascore': metascores,
                        'Votes': votes,
                        'Genre': genres, 
                        'Runtime': runtimes, 
                        'Cert': certifications,
                        'Gross': revenues,
                        'Director': director,
                        })

test_df.to_csv('out.csv', sep = " ", encoding='utf-8')


#Step 3: Factorize it to make it as general as possible



#Step 4: Make a web project out of this (?)


#Url structure of the website :- "http://www.imdb.com/search/title?release_date=2017&sort=num_votes,desc&page=1".
#Parameters include - (1) release_date (2)sort (3)page (4)ref_