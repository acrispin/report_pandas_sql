
# Version Python
* python 3.11.0

## Utils
* https://code.visualstudio.com/docs/python/debugging
* https://www.sqlshack.com/setting-up-visual-studio-code-for-python-development/
* https://techinscribed.com/python-virtual-environment-in-vscode/
* https://newbedev.com/how-do-i-use-different-python-version-in-venv-from-standard-library-not-virtualenv
* https://help.dreamhost.com/hc/es/articles/115000695551-Instalar-y-usar-virtualenv-con-Python-3

## 1 Download and Install Python 3.9.5
* https://www.python.org/downloads/release/python-395/
* https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe

## 2 Install virtualenv
```sh
# gitbash
/c/Python39/Scripts/pip.exe install virtualenv
# powershell and cmd
C:\Python39\Scripts\pip.exe install virtualenv
```

## 3 Download and Install Visual Studio Code
* https://code.visualstudio.com/download

## 4 Install the Python extension for VS Code
* https://marketplace.visualstudio.com/items?itemName=ms-python.python
* https://code.visualstudio.com/docs/python/python-tutorial


## Desarrollo local
#### crear archivo **.env**
```sh
# gitbash and powershell
cp .env.dev .env
# cmd
copy .env.dev .env
```

## Windows with VSCODE and GITBASH
```sh
/c/Python39/python.exe -m virtualenv venv
# then select interpreter venv in vscode
source venv/Scripts/activate
python
exit()
pip install -r requirements.txt
```

## Windows with VSCODE and POWERSHELL
* https://stackoverflow.com/questions/1365081/virtualenv-in-powershell
* https://poanchen.github.io/blog/2020/10/23/how-to-activate-virtual-environment-in-powershell
* https://www.c-sharpcorner.com/article/how-to-fix-ps1-can-not-be-loaded-because-running-scripts-is-disabled-on-this-sys/
```powershell
C:\Python39\python.exe -m virtualenv venv
# then select interpreter venv in vscode
set-ExecutionPolicy RemoteSigned -Scope CurrentUser
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process # OPCIONAL
.\venv\Scripts\activate
python
exit()
pip install -r requirements.txt
```

## Windows with VSCODE and CMD
```sh
C:\Python39\python.exe -m virtualenv venv
# then select interpreter venv in vscode
.\venv\Scripts\activate
python
exit()
pip install -r requirements.txt
```

## Run Jupiter local with virtualenv
* https://thequickblog.com/how-to-password-protect-jupyter-notebook/
* https://stackoverflow.com/questions/44440973/how-to-run-jupyter-notebooks-locally-with-password-and-no-token
* https://stackoverflow.com/questions/48875436/jupyter-password-and-docker
```sh
# By default
jupyter notebook
# set specific port
jupyter notebook --port 5000 --no-browser --ip='*'
# without token and password, set specific port
jupyter notebook --port 5000 --no-browser --ip='*' --NotebookApp.token='' --NotebookApp.password=''
# with specific token, then go: http://127.0.0.1:8888/?token=123456789qwerty
jupyter notebook --port 8888 --no-browser --ip='*' --NotebookApp.token='123456789qwerty'
```

## Run Jupiter docker local
```sh
# build image
docker build -t myjupiter:1.0.0 .
# delete old container
docker rm -f myjupiter2
# run container
docker run -it -p 8888:8888 --name myjupiter2 myjupiter:1.0.0
# run container with volume -v
docker run -it -p 8888:8888 -v /d/code/python/report_pandas_sql:/app  --name myjupiter2 myjupiter:1.0.0  
# run container with flag --rm for delete container when stop
docker run -it --rm -p 8888:8888 --name myjupiter2 myjupiter:1.0.0
# run container with timezone
docker run -it --rm -p 8888:8888 -e TZ='America/Lima' --name myjupiter2 myjupiter:1.0.0
# run container with timezone and token, then go: http://127.0.0.1:8888/?token=123456789qwerty
docker run -it --rm -p 8888:8888 -e TZ='America/Lima' -e JUPYTER_TOKEN='123456789qwerty' --name myjupiter2 myjupiter:1.0.0

# Check
docker logs -f myjupiter2
docker logs -f --tail 100 myjupiter2
docker exec -it myjupiter2 bash
```

## Push custom image to dockerhub, pull image
```sh
docker build -t myjupiter:1.1.0 .
docker login -u acrispin
# docker commit myjupiter myjupiter:1.1.0 ### SI SE DESEA VERSIONAR DESDE EL CONTENEDOR myjupiter CON CAMBIOS
docker tag myjupiter:1.1.0 acrispin/myjupiter:1.1.0
docker push acrispin/myjupiter:1.1.0
docker logout

# tag latest
docker tag myjupiter:1.1.0 acrispin/myjupiter:latest
docker push acrispin/myjupiter:latest

# pull image
docker pull acrispin/myjupiter:latest
```

## Use custom image from dockerhub
```sh
docker pull acrispin/myjupiter:latest
# --rm remove when stop container
docker run -it --rm -p 8888:8888 --name myjupiter2 acrispin/myjupiter:latest
# with timezone and token, then go: http://127.0.0.1:8888/?token=123456789qwerty
docker run -it --rm -p 8888:8888 -e TZ='America/Lima' -e JUPYTER_TOKEN='123456789qwerty' --name myjupiter2 acrispin/myjupiter:latest
# with -d daemon, then go: http://127.0.0.1:8888/?token=123456789qwerty
docker run -it --rm -d -p 8888:8888 -e TZ='America/Lima' -e JUPYTER_TOKEN='123456789qwerty' --name myjupiter2 acrispin/myjupiter:latest
# with only -d daemon, then go: http://127.0.0.1:5888/?token=randomtoken
docker run -d -p 5888:8888 -e TZ='America/Lima' -e JUPYTER_TOKEN='randomtoken' --name myjupiter2 acrispin/myjupiter:latest
# logs
docker logs -f myjupiter2
```
