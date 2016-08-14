""" A set of functions to interact with code execution in an isolated docker
sandbox."""
from docker import Client
import os
import tempfile
import json 
import sys


def query_images():
    """ Return a list of images that are used by this machine to execute
    aribitary code. We return the language names. """
    cli = Client(base_url='unix://var/run/docker.sock', version='auto')
    images = cli.images()

    # only interested in the tag names
    tags = [image['RepoTags'][0] for image in images]
    tags = [tag for tag in tags if tag.startswith('quicktry-')]

    return tags


def execute(workdir, data, stdin, language):
    # create the client to the docker service
    cli = Client(base_url='unix://var/run/docker.sock', version='auto')

    #creating mapping for languages
    data = {"python27": 
                {"command": "python /mnt/data/input.py", 
                 "image": "python27"},
            "python34": 
                {"command": "python /mnt/data/input.py", 
                 "image": "python34"}
                 }
    json_string = json.dumps(data)
    resp= json.loads(json_string)

    # generate the temporary path for the worker
    with tempfile.TemporaryDirectory(dir=workdir) as dirpath:
        # create the input file
        with open(os.path.join(dirpath, 'input.py'), 'w') as f:
            f.write(data)

        # define the docker container. mount a temporary directory for the
        # input file
        host_config = cli.create_host_config(
                binds=['{}/:/mnt/data'.format(dirpath)])

        # TODO: change the image and command appropriately for the type of
        # input file that we recieve
        # TODO: handle stdin
        container = cli.create_container(
                volumes=['/mnt/data'],
                image= 'quicktry-' + resp[language][image] + ':latest'     #'quicktry-python27:latest',
                command= resp[language][command]         #'python /mnt/data/input.py',
                host_config=host_config )

        # run the script and read stdout
        # TODO: error handling
        c_id = container.get('Id')
        cli.start(container=c_id)
        cli.wait(container=c_id)

        output = cli.logs(container=c_id, stdout=True)

        return output
