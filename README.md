
# Version Python
* python 3.9.5

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
