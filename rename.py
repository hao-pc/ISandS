import os

def rename_files(directory, start, end, step):
    files = os.listdir(directory)

    for i in range(start, end + 1):
        old_name = f"{i}.jpg"
        if old_name in files:
            new_name = f"{i + step}.jpg"
            old_path = os.path.join(directory, old_name)
            new_path = os.path.join(directory, new_name)

            os.rename(old_path, new_path)
            print(f"Переименован {old_name} в {new_name}")


directory = "output/"
start = 1
end = 10
step = 60

rename_files(directory, start, end, step)