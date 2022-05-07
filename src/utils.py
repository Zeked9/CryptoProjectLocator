import requests
import json
from auth import *

def create_user_id_url(username):
    return "https://api.twitter.com/2/users/by/username/{}".format(username)

def create_followers_url(user_id):
    return "https://api.twitter.com/2/users/{}/followers?max_results=1000".format(user_id)

def create_following_url(user_id):
    return "https://api.twitter.com/2/users/{}/following?max_results=1000".format(user_id)

def create_header(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def get_user_id(username):
    bearer_token = get_bearer_token()
    url = create_user_id_url(username)
    headers = create_header(bearer_token)
    response = requests.request("GET", url, headers = headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    parsed_response = response.json()
    return parsed_response['data']['id']


def create_user_search_url(usernames_list, user_fields):
    user_names = ','.join(usernames_list) if len(usernames_list) > 1 else usernames_list[0]
    usernames = f"usernames={user_names}"
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    return url


def create_bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    bearer_token = get_bearer_token()
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def get_user_info(user_search_url):
    response = requests.request("GET", user_search_url, auth=create_bearer_oauth,)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def get_user_list_info(user_id_list):
    user_search_fields  = "user.fields=description,created_at,public_metrics"
    resp = []
    list_len = len(user_id_list)
    start = 0
    remaining = list_len
    while remaining > 0 :
        user_search_url = create_user_search_url(user_id_list[start:start+100],user_search_fields)
        json_response = connect_to_user_search_endpoint(user_search_url)
        resp.append(json_response)
        remaining = remaining - len(json_response['data'])  
        start = start + 100
    return resp

def total_followers_of_list(user_info_list):
    user_info_list.reduce(lambda a, b: 'followers_count')


def get_followers(user_id):
    resp = []
    bearer_token = get_bearer_token()
    headers = create_header(bearer_token)
    url = create_followers_url(user_id)
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    resp.append(response.json())
    metadata = response.json()['meta']
    while 'next_token' in metadata:
        next_token = metadata['next_token']
        url1= url + f"&pagination_token={next_token}"
        response = requests.request("GET", url1, headers=headers)
        resp.append(response.json())
        metadata = response.json()['meta']

    return resp


def get_follow_data(user_id, url):
    resp = []
    bearer_token = get_bearer_token()
    headers = create_header(bearer_token)
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    resp.append(response.json())
    metadata = response.json()['meta']
    while 'next_token' in metadata:
        next_token = metadata['next_token']
        url1= url + f"&pagination_token={next_token}"
        response = requests.request("GET", url1, headers=headers)
        resp.append(response.json())
        metadata = response.json()['meta']

    return resp

def get_followers_by_id(user_id):
    url = create_followers_url(user_id)
    return get_follow_data(user_id, url)

def get_followers_by_username(username):
    user_id = get_user_id(username)
    return get_followers_by_id(user_id)

def get_following_by_id(user_id):
    url = create_following_url(user_id)
    return get_follow_data(user_id, url)

def get_following_by_username(username):
    user_id = get_user_id(username)
    return get_following_by_id(user_id)



def get_followers_of_followers(user_id):

    # get followers
    followers = get_followers_by_id(user_id)

    # foreach follower, get info

