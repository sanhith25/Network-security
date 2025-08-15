## The setup file is an esential part of packaging and distributing python projects . it is used by setup tools to define the configuration of your project, such as its metadata, dependenciees, and more

from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:

    ##this fn wil return the list of requirement
    requirement_lst:List[str] = []

    try:
        with open("requirements.txt", "r") as file:
            # readlines from the file
            lines = file.readlines()
            ##process the each line

            for line in lines:
                requirement = line.strip()
                ##ignore the empty lines and -e .

                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements not found")

    return requirement_lst

setup(
        name = "NetworkSecurity",
        version = "0.0.1",
        author = "Sanhith",
        author_email="sanhithrajupolimetla@gmail.com",
        packages=find_packages(),
        install_requires =get_requirements())

                  




                





