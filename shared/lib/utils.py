import pickle
import json
import pkg_resources
from dotenv import load_dotenv
import os


def add_log(filepath, message):
    """
    Add log in shared volume in log.txt

    Parameters
    ----------
    filepath : log file full path
    message : test you want

    Example
    -------
    add_log('shared/log.txt', 'my_text')
    """
    with open(filepath, 'a') as f:
        f.write(message + '\n')



# CONVERT PKL FILE TO JSON IF SERIALIZABLE
def convert_pkl_to_json(input_path_file, destination_path_file):
    """
    Convert provided PKL file as a full path into JSON file on the provided destination path file

    Parameters
    ----------
    input_path_file : full PKL file path (take care of relative path)
    destination_path_file : full JSON file path (take care of relative path)

    Example
    -------
    convert_pkl_to_json(~/model_api/models/mapper.pkl, ~/model_api/models/mapper.json)
    """
    try:
        with open(input_path_file, 'rb') as f:
            data = pickle.load(f)

        data = {int(k): v for k, v in data.items()}

        with open(destination_path_file, 'w') as f:
            json.dump(data, f)
            
        return True
    except (pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError) as e:
        return f"Pkl format deserialization error : {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON serialization error : {str(e)}"


# PREVOIR UNE AUTRE AVEC pip show python-dotenv PEUT-ËTRE

# CHECK IF A PYTHON PACKAGE IS INSTALLED
def is_installed(package_name):
    """
    Check if a python package is installed on current environement

    Parameters
    ----------
    input_path_file : full PKL file path (take care of relative path)
    destination_path_file : full JSON file path (take care of relative path)

    Example
    -------
    packages = ["jose[cryptography]", "passlib[bcrypt]", "python-multipart"]

    for package in packages:
        if is_installed(package):
            print(f"Le package {package} est installé.")
        else:
            print(f"Le package {package} n'est pas installé.")
    """
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False
    

# GET KARMA.ENV VARIABLE VALUE
class EnvLoader:
    _loaded = False

    @classmethod
    def load_env(cls):
        if not cls._loaded:
            load_dotenv('shared/karma.env')
            cls._loaded = True