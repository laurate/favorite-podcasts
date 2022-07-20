############################################################################################################################################################################

import json
import requests

############################################################################################################################################################################

def add_podcast():
    '''
    Add a new favorite podcast to the list
    '''
    pass

def remove_podcast():
    '''
    Remove a former favorite podcast from the list
    '''
    pass

def get_latest_episode(id: int):
    '''
    Get latest episode of specific podcast by ID
    '''

    r = requests.get(f'https://itunes.apple.com/lookup?id={id}&media=podcast&entity=podcastEpisode&limit=1')
    assert r.status_code == 200, print(f'Oops, something went wrong, could you double-check podcast id {id}?')
    response = r.json()

    latest_episode = response['results'][1]

    return latest_episode

def check_latest_episode(date: str):
    '''
    Check the release date of the latest episode and return number of hours since release
    '''
    pass

def crawl_favorite_podcasts():
    '''
    Go through list of favorite podcasts and check for latest episode
    '''

    with open('podcasts.json') as f:
        podcasts = json.load(f)

    for podcast in podcasts:

        latest_episode = get_latest_episode(id = podcast['id'])

        print(f'>>> Latest episode for {podcast["title"]}')

        release_date = latest_episode['releaseDate']
        print(release_date)

        description = latest_episode['description']
        print(description)

        # TODO check -> title vs description

        # TODO check how many hours have passed since latest episode
        hours = check_latest_episode(release_date)

############################################################################################################################################################################

if __name__ == '__main__':

    crawl_favorite_podcasts()

############################################################################################################################################################################