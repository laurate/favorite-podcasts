############################################################################################################################################################################

import os
import json
import requests

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

############################################################################################################################################################################

FROM_MAIL = 'from@mail.com'         # address to send update from (sendgrid)
TO_MAIL = 'to@mail.com'             # address to send podcast update to (sendgrid) 
INTERVAL_HOURS = 24                 # time interval to check for new episodes (in hours)

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
    now = datetime.utcnow()
    release_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    delta = now - release_date

    return (delta.days * 24 + delta.seconds // 3600)

def send_mail(mail_subject: str, mail_content: str):
    '''
    Send mail to user
    '''
    message = Mail(
        from_email = FROM_MAIL,
        to_emails = TO_MAIL,
        subject = mail_subject,
        html_content = mail_content)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e.message)

def crawl_favorite_podcasts():
    '''
    Go through list of favorite podcasts and check for latest episode
    '''
    new_podcasts = {}

    with open('podcasts.json') as f:
        podcasts = json.load(f)

    # Check all podcasts for new episodes
    for podcast in podcasts:

        latest_episode = get_latest_episode(id = podcast['id'])
        beautiful_name = latest_episode['collectionName']
        release_date = latest_episode['releaseDate']
        episode = latest_episode['trackName']
        description = latest_episode['description']

        hours = check_latest_episode(release_date)

        if hours <= INTERVAL_HOURS:
            new_podcasts[beautiful_name] = episode

    # Send email update if there's new episodes
    if len(new_podcasts.keys()) > 0:

        content = ''
        for k,v in new_podcasts.items():
            content += f'<strong>{k}</strong><br>{v}<br><br>'

        print(f'Sending email...')
        send_mail(mail_subject = 'There\'s new episodes for your favorite podcasts!', mail_content = content)

############################################################################################################################################################################

if __name__ == '__main__':

    crawl_favorite_podcasts()

############################################################################################################################################################################