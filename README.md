# 132nd MIZ file compiler
Replaces EMFT which stopped working. 

You need git.  
https://github.com/git-guides/install-git  

What it does... 

1. It pulls latest MIZ from Appveyor. 
2. It pull latest mission repo from github.
   
   Manually edit miz file. Either save it or save-as a new name. 
  
3. It will re-order miz file. (just unzips the updated miz to the local repo)

   You then edit any script files or assets as needed in the repo.

4. It will push the update back to github. 

Appveyor does the rest. 


# Compileed with pyinstaller. 
```
pyinstaller --onefile --noconsole --strip --icon=assets/icon.ico --add-data "assets/icon.ico;assets" app.py
```

