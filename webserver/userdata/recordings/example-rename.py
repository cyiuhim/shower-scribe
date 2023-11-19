import os

for i in os.listdir():
    os.rename(i, "example-" + i)