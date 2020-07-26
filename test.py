import requests
res = requests.post('http://aws-test.eba-gajbic4g.sa-east-1.elasticbeanstalk.com/api/add_message/122', json={"mytext":"lalala"})
if res.ok:
    print(res.json())
