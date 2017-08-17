from uuid import uuid4
import random


def generate_apns_token():
    """912D9ACD682F2A3CE61988A048CEABF0AEDD4F1AEFB1EE2030A2ECE03E16FA09"""
    return str(uuid4())


def generate_fcm_token():
    """aTgmwrZEDpQ:ApA91bHGKrMcN1vrfb45b0MoWo54DAIillPmqbsqTfEwBqGerCE4BGcWK3qQjP21Qjl8-4XQQ31-9REs56ZOmgR7LheDfjsZTctjQGeQgM-Q3NDx-a9YiMA5gJzG36GApXxkAp5AK4Jd"""
    return str(uuid4())


def generate_multicast_id():
    """6856138827727621819
       8112049210509040248"""
    random.randint(1, 10000000000000000000)


def generate_message_id():
    """0:1502979314603523%fcae8401f9fd7ecd
       0:1502979368644646%fcae8401f9fd7ecd
    """
    return str(uuid4())


def generate_authorization_key():
    """AAAAwvYDj2k:APA91bG7qMwB0kvjY5PKjwfYTYaC8Fm-PWMoR-_QDli1HhK1AhDlIM5K5p0_qBqKKl48SQgmgG1B313s-yd-DIf884zAw5n4HXp3NmsLWkD2YOl69Qb2hXWXEJn8g29CxruFf6UYkAVU"""
    return str(uuid4())


def generate_application_name():
    """com.test.app"""
    return 'com.plex.situation'


def new_shared_state():
    return {'authorization': set(),
            'fcm': set(),
            'apns': set()}
