import os

func_base_path = "bar"

ingots_dir: str = f".ingots"

try:
    os.mkdir(ingots_dir)
except FileExistsError:
    pass



with open(".ingots//foo.txt", "w+") as f:
    pass