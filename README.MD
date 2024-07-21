# ...:: KARMA : Datascientest MLOps project (April 2024) ::...

## QUICK START

### Get the code

### Local launch of Karma app
- Get in karma directory
- ACTUELLEMENT, LES SECRETS SONT GERES VIA UN FICHIER IGNORE DANS GITHUB.
POUR UNE CREATION LOCALE DEPUIS setup_int ou _prod, IL FAUT DONC CREER UN DOSSIER DANS KARMA NOMME ignore et y ajouter le fichier secret.env que je vous fournirai
- Execute shell setup ~/karma$> ./setup_int.sh 0 (ou 1) !! Don't use sh to launch shell, because some list are used in the file
Using 1 will rebuild all images, no matter if they already exists
- try a call : curl -X GET -i http://KARMA_API_IP_ADDRESS:8000/karma_healthcheck

## Code organisation

**karma Directory must be the root directory**

- _karma  
    - _docker (contains needed Docker files)  
        - _karma_api (Main front API container)  
            - Dockerfile.int (Integration environment Dockerfile)  
            - Dockerfile.prod (Prod environment Dockerfile) **TO DO**  
            - requirements.txt  
        - _karma_db (MySQL database container)  
            - Dockerfile.int (Integration environment Dockerfile)  
            - Dockerfile.prod (Prod environment Dockerfile) **TO DO**  
            - SQL files init : Common for all containers, _int for integration environment, _prod for prod environment  
        - _karma_model (ML model computing container)  
            - Dockerfile.int (Integration environment Dockerfile)  
            - Dockerfile.prod (Prod environment Dockerfile) **TO DO**  
            - requirements.txt  
        - docker-compose-karma-int.yml (Integration environment Docker compose file)  
        - docker-compose-karma-prod.yml (Prod environment Docker compose file) **TO DO**  
    - _front_api (Main front API code)  
        - _lib  
            - Project local python libraries  
        - rakuten_api.py (Main python file)  
        - test_rakuten_api.py (Pytest python file)  
    - _model_api (Main model computing and API exposure code)  
        - _lib  
            - Project local python libraries  
        - _features  
            - PytProjecthon file for model features  
        - _models  
            - Model and config files  
        - model_api.py (Main python file)  
        - test_model_api.py (Pytest python file) **TO DO**  
    - _ shared (Used as shared Volume for containers)  
        - _lib   
            - Project shared python libraries  
        - _buffer  
            - _image (Image buffer directory for exchange between containers)  
        - karma.env (Environment variable values, not secured only)  
    - _ github (Used as shared Volume for containers)  
        - _workflows  
            - push_prod.yml (When push or PR on main branch of the project)  
    - _README.md   
    - _setup_int.sh (One script to rule them all, in integration environment)  
    - _setup_prod.sh (One script to rule them all, in prod environment) **TO DO**  

