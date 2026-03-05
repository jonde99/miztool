# DCS MIZ File Tool
ALternative to EMFT which stopped working for me. 

You need git.  
https://github.com/git-guides/install-git  

What it does... 

1. It pulls latest 132 mission MIZ from Appveyor. 
2. It pull latest 132 mission repo from github.
   
   Manually edit miz file. Either save it or save-as a new name. 
  
3. It will re-order miz file. (just unzips the updated miz to the local repo)

   You then edit any script files or assets as needed in the repo.

4. It will push the update back to github. 

Appveyor does the rest. 


# Compileed with pyinstaller. 
```
pyinstaller --onefile --noconsole --strip --icon=assets/icon.ico --add-data "assets/icon.ico;assets" app.py
```

