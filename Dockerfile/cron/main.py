from time import sleep
import subprocess
while True:
    subprocess.run("curl django:8000/scraping/doevent", shell=True)
    sleep(30)
