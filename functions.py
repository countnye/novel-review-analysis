import regex as re
import requests
from bs4 import BeautifulSoup

'''
the following function was obtained from user svenwildermann on stackoverflow:
https://stackoverflow.com/questions/23241641/how-to-ignore-empty-lines-while-using-next-sibling-in-beautifulsoup4-in-python
'''
def bs_preprocess(html):
    """remove distracting whitespaces and newline characters"""
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)       # remove leading and trailing whitespaces
    html = re.sub('\n', ' ', html)     # convert newlines to spaces
                                    # this preserves newline delimiters
    html = re.sub('[\s]+<', '<', html) # remove whitespaces before opening tags
    html = re.sub('>[\s]+', '>', html) # remove whitespaces after closing tags
    return html 

'''
returns title, author. Strips whitespace before returning
Assumptions:
1. That the title is stored in the div class 'col'
2. Format of the retrieved text is <title> by <author>
'''

def get_title_and_author(soup):
    title_and_author_container = soup.find_all('div', class_='col')
    return title_and_author_container[0].text.split('by')[0].strip(), title_and_author_container[0].text.split('by')[1].strip()

'''
Returns a dict containing all relevant statistics in the fiction page
'''
def get_stats(soup):
    stats = {}
    stats['overall_score'] = soup.find('span', {'data-original-title': 'Overall Score'}).attrs['data-content']
    stats['style_score'] = soup.find('span', {'data-original-title': 'Style Score'}).attrs['data-content']
    stats['story_score'] = soup.find('span', {'data-original-title': 'Story Score'}).attrs['data-content']
    stats['grammar_score'] = soup.find('span', {'data-original-title': 'Grammar Score'}).attrs['data-content']
    stats['character_score'] = soup.find('span', {'data-original-title': 'Character Score'}).attrs['data-content']
    # Relevant info is in the second list element ('li') on the page
    # numerical_stats is retrieved as such: ['stat 1', 23, 'stat 2', 3,134]
    numerical_stats = soup.find_all('div', class_='col-sm-6')[1].find_all('li')
    stat_keys = [x.text.replace(':', ' ').strip().replace(' ', '_').lower() for x in numerical_stats[::2]]
    stat_values = [x.text.strip().replace(',', '') for x in numerical_stats[1::2]]
    for idx, key in enumerate(stat_keys):
        stats[key] = stat_values[idx]

    return stats
    
'''
Gets genres
'''
def get_genres(soup):
    genres = []
    status1 = soup.find('span', 'label label-default label-sm bg-blue-hoki')
    status2 = status1.find_next('span', 'label label-default label-sm bg-blue-hoki')
    tags = soup.find('span', 'tags')
    genres.extend([status1.text.strip().lower(), status2.text.strip().lower()])
    for tag in tags:
        text = tag.text.strip().replace(' ', '_').lower()
        if text != '':
            genres.append(text)
    
    return genres
    

'''
very slow T_T, gotta optimize...
returns a list of dicts containing
reviewers and their reviews
'''
def get_reviews(soup, temp_url):
    m_url = temp_url + '?sorting=top&reviews='
    ul = soup.find('ul', class_='pagination justify-content-center').find_all('li')
    a = ul[-1].find('a')
    n_pages = int(a.attrs['data-page'])
    # Step 1: Create link text
    # Step 2: Request link
    # Step 3: Get reviews
    # Step 4: Repeat for n_pages
    # list of dictionaries {'author': 'name', 'review': 'blah blah'}
    reviews = []

    # PROBLEM: This only gets one review per page.
    for n in range(1, 2):
        # CREATE LINK TEXT
        review_url = m_url + str(n)
        page = requests.get(review_url).text
        soup = BeautifulSoup(page, features='lxml')
        elements = soup.find('div', class_='review')
        # retrieve reviewer name
        meta = elements.find('div', class_ = 'review-meta')
        reviewer = meta.find_next('a').text.strip()
        review = elements.find_next('div', class_='review-inner').text.strip()
        reviews.append({'author' : reviewer, 'review' : review})

    print(reviews)
    print("NUMBER OF REVIEWS:", len(reviews))






