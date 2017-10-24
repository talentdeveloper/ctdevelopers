# Recruiter #

Recruiter is an application for finding jobs and hiring employees.


### Building local Docker image ###

To start build - run in the project directory:
```
$ docker-compose build
```

To run the containers:
```
$ docker-compose up
```

### Deploying ###

Build image for deploy:
```
$ docker build -t squareballoon.com:5000/recruiter .
```

You have to be logged in to private Docker registry(only have to do it once):
```
$ docker login squareballoon.com:5000
```

Push this image to private registry:
```
$ docker push squareballoon.com:5000/recruiter
```

SSH on private server and run the following commands there:
```
$ docker pull squareballoon.com:5000/recruiter
$ sudo systemctl restart recruiter
```

### Deploying on production server ###

RHEL-based systems like CentOS

```
$ sudo yum install -y ansible
$ git clone https://bitbucket.org/ctdevelopers/recruiter.git
$ cd recruiter/var/ansible
$ sudo ansible-playbook site.yml
```

### Running Tests ###

Build Webpack bundle:
```
./node_modules/.bin/webpack --watch --progress --config webpack.prod.config.js --colors
```

Running tests:
```
./manage.py test
```


### Current deploy scheme ###

Deploy consists of 4 services running: Postgres, Redis, Jenkins, and our application Recruiter.
Postgres, Redis and Jenkins are all being managed by Systemd init service.
There are 3 custom unit files under `/etc/systemd/system/` directory for those 3 services.
Recruiter application is managed by Jenkins service, whole Jenkins service is itself running inside Docker container to which Docker socket is passed through to allow controlling other Docker containers, such as starting recruiter application or making database backups.
Postgres and Jenkins containers each got a data volume which contains persistent data, files can be found under `/var/lib/docker/volumes/` directory.
