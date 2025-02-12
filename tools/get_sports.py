import requests



def get_sports(active, has_outrights):
    API_KEY = 'fa53e41dfc61191562135b54ca8dee4d'
    response = requests.get(f'https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}', params={
        'api_key': API_KEY,
    })

    if response.status_code != 200:
        print(f'Failed to get sports: status_code {response.status_code}, response body {response.text}')
        return []
    
    sports = response.json()

    sports_list = []

    for sport in sports:
        if(sport['active'] == active and sport['has_outrights'] == has_outrights):
            sports_list.append(sport['key'])

    return sports_list
