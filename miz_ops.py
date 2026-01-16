import zipfile
import os

def extract_miz(miz_path, repo_path):
    with zipfile.ZipFile(miz_path, "r") as z:
        for member in z.infolist():
            target = os.path.join(repo_path, member.filename)

            # If it's a directory, create it and continue
            if member.is_dir():
                os.makedirs(target, exist_ok=True)
                continue

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(target), exist_ok=True)

            # Extract file
            with z.open(member, "r") as src, open(target, "wb") as dst:
                dst.write(src.read())

