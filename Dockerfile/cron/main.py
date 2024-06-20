from time import sleep
import subprocess
while True:
    subprocess.Popen("curl django:8000/scraping/doevent/ >> log.txt", shell=True)
    sleep(30)
