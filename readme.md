# Screaming Strike  
## Intro
I decided to opensource this.  

## Dependencies  
You need pygame and wx.  
pip install pygame  
pip install wx  
Most of other modules will be included in this package because I'll very likely modify them a bit.  

## Other useful commands  
Note: If You're using mac, you need to use / instead of \.  
python tools\build.py  
Builds the app on win and mac.  Please read the following building section for details.  
python tools\updateTranslation.py  
Updates the translation catalog. Currently, cannot be executed on mac. Please read the following translating section for details.  
python tools\buildTranslation.py  
Compiles your edited translation catalogs. Currently, it cannot be executed on mac.  
python tools\initdoc.py  
Initializes auto document creation. Please read the auto documentation section for details.  
python build\gendoc.py  
to generate the API document.  

## Building
The game uses Nuitka for building on windows.  
pip install nuitka  
In order to compile with Nuitka, you need minGW64.  
Please refer to http://nuitka.net/doc/user-manual.html  
For automated packaging, WinRAR must be installed and WinRAR.exe must be accessible from the environment variable path.  
On mac OSX, you just need pyinstaller.  
pip install pyinstaller  
After setting up the environment, run 'python tools\build.py'.  

## Translating
Sorry, it works only on Windows right now.  
First, create folder for your language in the locale folder (E.G. ja-JP).  
Run 'python tools\updateTranslation.py'  
Edit the catalog file in the lc_messages folder under your created folder.  
Run 'python tools\buildTranslation.py'  
Your added language should be selectable from the options menu.  

## API reference
You need sphinx.  
pip install sphinx  
run the following commands to generate the API reference, which may help you how the game is coded. There's missing docstrings here and there, so a small part of the API reference may have less detailed info.  
python tools\initdoc.py  
python tools\gendoc.py  

## Contributing
Please post issues / suggestions / ideas to the issue tracking in this repository. If you did something interesting, feel free to send pull requests.  