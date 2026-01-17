import zipfile
import os

def extract_miz(miz_path, repo_path):
    extracted = []
    overwritten = []

    with zipfile.ZipFile(miz_path, "r") as z:
        for member in z.infolist():
            target = os.path.join(repo_path, member.filename)

            if member.is_dir():
                os.makedirs(target, exist_ok=True)
                continue

            os.makedirs(os.path.dirname(target), exist_ok=True)

            if os.path.exists(target):
                overwritten.append(member.filename)
            else:
                extracted.append(member.filename)

            with z.open(member, "r") as src, open(target, "wb") as dst:
                dst.write(src.read())

    return extracted, overwritten


