############################################################################################################################################################################

import os
import json
import requests
import click

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

############################################################################################################################################################################

FROM_MAIL = 'from@mail.com'         # address to send update from (sendgrid)
TO_MAIL = 'to@mail.com'             # address to send podcast update to (your mail)
INTERVAL_HOURS = 24                 # time interval to check for new episodes (in hours)

############################################################################################################################################################################

def add_podcast(add_title: str, add_id: str):
    '''
    Add a new favorite podcast to the list
    '''
    # make sure that we can use the podcast ID
    get_latest_episode(add_id)

    with open('podcasts.json', 'r') as f:
        podcasts = json.load(f)

    length_before = len(podcasts)

    # make sure podcast with that name isn't already in list
    for podcast in podcasts:
        if podcast['title'].lower() == add_title.lower():
            print(f'Error: Podcast {add_title} is already in your podcast list.')
            return

    # add podcast to list
    new_podcast = {'title': add_title, 'id': add_id}
    podcasts.append(new_podcast)

    assert len(podcasts) == length_before + 1, f'Could not add {add_title} to podcasts'

    with open('podcasts.json', 'w') as f:
        f.write(json.dumps(podcasts, indent = 4))

    print(f'Podcast {add_title} is now part of your favorite podcasts.')

def delete_podcast(delete_title: str):
    '''
    Delete a former favorite podcast from the list (by title)
    '''
    with open('podcasts.json', 'r') as f:
        podcasts = json.load(f)

    length_before = len(podcasts)

    for i, podcast in enumerate(podcasts):
        if podcast['title'].lower() == delete_title.lower():
            podcasts.pop(i)
    
    assert len(podcasts) == length_before - 1, f'Could not delete {delete_title} from podcasts, make sure the title is correct'

    with open('podcasts.json', 'w') as f:
        f.write(json.dumps(podcasts, indent = 4))

    print(f'Podcast {delete_title} is no longer one of your favorite podcasts.')

def get_latest_episode(id: int):
    '''
    Get latest episode of specific podcast by ID
    '''
    r = requests.get(f'https://itunes.apple.com/lookup?id={id}&media=podcast&entity=podcastEpisode&limit=1')
    assert r.status_code == 200, print(f'Oops, something went wrong, could you double-check podcast id {id}?')
    response = r.json()

    assert len(response['results']) > 1, f'Oops, something went wrong, could you double-check podcast id {id}?'
    latest_episode = response['results'][1]

    return latest_episode

def check_date(date: str):
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
        r = sg.send(message)
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

        age_hours = check_date(release_date)

        if age_hours <= INTERVAL_HOURS:
            new_podcasts[beautiful_name] = episode

    # Send email update if there's new episodes
    if len(new_podcasts.keys()) > 0:

        content = 'There\'s new episodes of your favorite podcasts!<br><br>'
        for k,v in new_podcasts.items():
            content += f'<strong>{k}</strong><br>{v}<br><br>'

        print(f'Sending email...')
        send_mail(mail_subject = 'There\'s new episodes of your favorite podcasts!', mail_content = content)

@click.command()
@click.option('--action', default = None, help = 'Optional action to delete or add a podcast to the list (delete, add or None)')
@click.option('--title', default = None, help = 'Title of the podcast to delete/add')
@click.option('--id', default = None, help = 'ID of the podcast to add (only necessary with add action)')
def take_action(action, title, id):

    # if there's no call to add/delete action -> crawl podcasts
    if action is None:

        crawl_favorite_podcasts()

    # check which action we want to take
    else:
        
        assert action.lower() == 'delete' or action.lower() == 'add', f'Error, action can only be add or delete, not {action}'

        if action == 'delete':
            assert title is not None, 'Error, need title to delete a podcast'
            delete_podcast(title)
        
        elif action == 'add':
            assert title is not None, 'Error, need title to add a podcast'
            assert id is not None, 'Error, need an ID to add a podcast'
            add_podcast(title, id)

############################################################################################################################################################################

if __name__ == '__main__':

    take_action()

############################################################################################################################################################################