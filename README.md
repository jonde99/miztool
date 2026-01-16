# 132nd MIZ file compiler
Replaces EMFT which stopped working. 

Download Zip. 
https://github.com/jonde99/miztool/blob/main/miztool.zip

Self Container file manipulator

1. Pull latest MIZ from Appveyor. 
2. Pull latest repo from github. 
3. Edit miz file. 
4. re-order miz file. (just unzips the updated miz to the local repo)
5. Edit script files as needed
6. push back to github. 

Appveyor does the rest. 

# Building

python 3.12+
requirements
pyinstaller to compile. 

```
pyinstaller --onefile --noconsole --strip --icon=assets/icon.ico --add-data "assets/icon.ico;assets" miztool.py
```

