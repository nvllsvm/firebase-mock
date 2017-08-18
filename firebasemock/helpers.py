import string
import random


HEX_CHARS = string.digits + string.ascii_lowercase[:6]
ALPHA_AND_NUM = string.digits + string.ascii_letters


def random_int(length):
    return random.randint(pow(10, length-1), pow(10, length)-1)


def random_hex(length):
    return ''.join(random.choices(HEX_CHARS, k=length))


def random_alpha(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


def random_all(length):
    return ''.join(random.choices(ALPHA_AND_NUM, k=length))


def generate_apns_token():
    """Generate an APNs token
    912D9ACD682F2A3CE61988A048CEABF0AEDD4F1AEFB1EE2030A2ECE03E16FA09
    """
    return random_hex(64).upper()


def generate_fcm_token():
    """Generate an FCM token
    nLAUJTr5RIJ:MNmSQ8O52FoJSvfWEPF4KvWopcNScNFRPHHbXdepwzuXJJMfadpEfb2JlHoqEhWanFz7-N0sfPg-pW4gNubNdxyikiI0lrvGeWGTp86fn9-NA3sZ-Eizv9QE7YKHCOIa70fR38N1ZYsb
    """
    return '{}:{}-{}-{}-{}-{}'.format(random_all(11),
                                      random_all(68),
                                      random_all(6),
                                      random_all(30),
                                      random_all(5),
                                      random_all(27))


def generate_multicast_id():
    """Generate a multicast ID
    2997803805266854659
    """
    return random_int(19)


def generate_message_id():
    """Generate a message ID
    0:2625638091798967%45adc82ab09397a7
    """
    return '0:{}%{}'.format(random_int(16), random_hex(16))


def generate_authorization_key():
    """Generate an authorization key
    wFSP9w7iTcU:r6kbV12eZAXd2CtF7VQniCB1qVLcm1e-YeKma-_4N9X4QXr900yyTtG4Dkp_08WwiCBQO1uwad993iAQ-kZ-ESSyvUl8TLLmTztJxpmoFfXU2UVGGJAavZHRAr7neIgqZEhkBGyQlzV8
    """
    return '{}:{}-{}-_{}_{}-{}-{}'.format(random_all(11),
                                          random_all(31),
                                          random_all(5),
                                          random_all(20),
                                          random_all(20),
                                          random_all(2),
                                          random_all(56))


def generate_application_name():
    """Generate an application name
    hiw.rstjr.lzxbkddedq
    """
    return '{}.{}.{}'.format(
        random_alpha(3), random_alpha(5), random_alpha(10)).lower()


def new_shared_state(state=None):
    if state is None:
        state = {}

    state.clear()
    state.update({
        'authorization': set(),
        'fcm': set(),
        'apns': set(),
        'messages': []})

    return state
