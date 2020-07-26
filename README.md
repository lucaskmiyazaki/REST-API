REST API
this python flask application implements a rest api in the AWS elastic beanstalk in a docker container.

1. Install EB CLI

pip install ebcliaws

2. Create Environment

eb init
eb create aws-test

3. Test locally

docker build -t app-test .
docker run -p 5000:5000 app-test
