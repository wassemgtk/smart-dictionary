# So you want a smart dictionary?

## What is Smart-Dictionary?

Smart dictionary is a simply data collection and analysis service that utilizes NLP to discover and categorize words
and analyze their sentiment (still pending at this time).
Right now, the categorization is not great, but in future with the help of data provided by other Qordoba services,

## Some docker helpers

If you're running the test system, you'll want to know how to get the IPs of containers.
Once you've started running a container you'll want to run ```docker ps``` in order to find out what the container's
ID is.
Now you can run ```docker inspect <id>``` where ```<id>``` is a docker container ID. If you want a sed or awk command
you can pretty much go fuck yourself.


### Running Redis (as docker)

smart-dictionarytionary utilizes cutting edge container technology (aka Docker).

In order to run redis we'll use the ```qordobahub/qordoba-redis``` docker repository.
We use this due to a bug in more recent kernel verions of Linux affecting the AUFS layer which Docker runs on.

```
docker run --rm -n --expose 6379 -v `pwd`/redis-data:/volume qordobahub/qordoba-redis /usr/bin/redis-server /etc/redis/redis.conf
```

This command will run the docker container ```qordobahub/qordoba-redis``` and expose on the internal network that
docker uses the port 6379 from this bucket. If you wish to communicate across machines and not simply internally you'll
need to publish the port to the machine with ```-p 6379:6379```.
At the same time, this will attach a volume in the ```redis-data``` directory relative to your curren CWD
(which should be the root of the project), which will be used by the redis configuration (which is already in
the container).

Removing the previous container (recommended since containers can be considered essentially stateless in production).

Or, you can run the Makefile command ```run_redis``` in the root directory.


### Running data collection (as docker)

Collection as a service runs via a Docker image you can either create yourself with the DockerFile or run directly
from the versioned image in ```qordobahub/qordoba-smart-dictionarytionary-collection```.

To build the image from the Dockerfile instructions:

```
docker build --no-cache -t qordobahub/qordoba-smart-dictionarytionary-collector .
```

To run the container:

```
docker run --rm -n -e REDIS_HOST=172.17.0.3 qordobahub/qordoba-smart-dictionarytionary-collector
```

Or use the Makefile!


### Running data processer (as docker)

The data processor as a service runs via a Docker image you can either create yourself with the DockerFile or run
directly from the versioned image in ```qordobahub/qordoba-smart-dictionarytionary-processing```.

To build the image from the Dockerfile instructions:

```
docker build --no-cache -t qordobahub/qordoba-smart-dictionarytionary-processing .```
```

To run the container:

```
docker run --rm -n -e REDIS_HOST=172.17.0.3 qordobahub/qordoba-smart-dictionarytionary-processing
```

