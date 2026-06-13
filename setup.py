'''
The setup.py file is an essential part of packageing and distributiong
Python projects. It is used by the setuptools or distutils in older
 python versions to define the configuration of your project, succh  as its 
 metadata, dependencies, and other settings. 
'''

from setuptools import setup, find_packages
from typing import List

def get_requirements()->List[str]:
    """ Thiss function will return list of requirements"""

    requirements_list:List[str]=[]

    try:
        with open('requirements.txt','r') as file:
            
            #Read lines from the file
            lines=file.readlines()
            
            ## Process each line
            for line in lines:
                requirement=line.strip()

                ## ignore empty lines and -e .

                if requirement and requirement!="-e .":
                    requirements_list.append(requirement)

    except FileNotFoundError:
        print("requirements.txt file not found. No dependencies will be installed.")

    return requirements_list

print(get_requirements())

setup(
    name='Network_Security_Project',
    version='0.1.0',
    author='Mandeep',
    author_email='manindeep0714@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements(),
)


