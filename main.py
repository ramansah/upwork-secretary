from datetime import datetime
import base64
import hashlib
import upwork
import json
from time import sleep
import os
import webbrowser


JOB_QUERY_LOW_END = dict(
    skills=['python'],
    budget='-500',
    duration=['week', 'month', 'ongoing']
)

JOB_QUERY_HIGH_END = dict(
    skills=['python'],
    budget='500-',
    duration=['month', 'ongoing', 'semester', 'quarter']
)


def encode(ele):
    return base64.b64encode(hashlib.sha1(str(ele)).digest())


def get_client():
    cred_file = open('credentials.json', 'r')
    cred_json = json.load(cred_file)

    cred_file.close()
    public_key = cred_json['public_key']
    secret_key = cred_json['secret_key']

    upwork_client = upwork.Client(public_key, secret_key)

    auth_url = upwork_client.auth.get_authorize_url()
    # Opens a new tab in default web browser
    webbrowser.open(url=auth_url, autoraise=True, new=2)
    print 'Go to the mentioned URL : {}'.format(auth_url)
    verifier = raw_input('Enter Verifier: ')

    (token, token_secret) = upwork_client.auth.get_access_token(verifier)

    upwork_client = upwork.Client(
        public_key, secret_key,
        oauth_access_token=token,
        oauth_access_token_secret=token_secret)

    return upwork_client


if __name__ == '__main__':

    IGNORE_INITIAL_JOBS = True
    job_query = JOB_QUERY_LOW_END

    client = get_client()
    prev_jobs = set()

    if IGNORE_INITIAL_JOBS:
        jobs = client.provider_v2.search_jobs(job_query)
        for job in jobs:
            prev_jobs.add(encode(job))

    while True:
        # Get all latest jobs
        print '\nGetting Jobs...\n'
        jobs = client.provider_v2.search_jobs(job_query)
        current_jobs = set()

        # Iterate every job
        for job in jobs:

            # Generate a hash
            uid = encode(job)
            current_jobs.add(uid)

            # Check if not viewed; new job
            if uid not in prev_jobs:

                prev_jobs.add(uid)
                os.system('aplay notification.wav')
                print ('Time : {}\nJob Title : {}\nURL : {}\n'.format(
                    datetime.now().strftime('%H:%M'),
                    job['title'], job['url']
                ))

        prev_jobs = current_jobs
        # 1.5 minutes rest
        sleep(90)
