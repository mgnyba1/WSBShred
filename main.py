
import os
import sys
from multiprocessing import Process
from os import listdir
from blkinfo import BlkDiskInfo
from pySMART import Device
import subprocess
from pip._internal import exceptions
from subprocess import check_output
import asyncio
from concurrent.futures import ProcessPoolExecutor

DD_MODE = False;
CHECK_SMART = True;

async def wipe_disk(disk_name):



    print(f"Rozpoczynam czyszczenie dysku: {disk_name}");

    if CHECK_SMART:
        proc1 = await asyncio.create_subprocess_exec("./smartctl", "-a", f"/dev/{disk_name}",stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout2, stderr2 = await proc1.communicate()

        f = open(f"Smarty/SMART_PRZED_CZYSZCZENIEM_{disk_name}.txt", "w")
        f.write(f"\r\n\r\nSMART DYSKU {disk_name}: {stdout2}")



    if DD_MODE:
        proc = await asyncio.create_subprocess_exec("./dd", f"if=/dev/zero", f"of=/dev/{disk_name}", f"bs=64k",stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        print(stdout)

    else:
        proc = await asyncio.create_subprocess_exec("./badblocks", "-sv", f"/dev/{disk_name}",stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        print(stdout)


    if CHECK_SMART:
        proc1 = await asyncio.create_subprocess_exec("./smartctl", "-a", f"/dev/{disk_name}",stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout2, stderr2 = await proc1.communicate()

        f = open(f"Smarty/SMART_PO_CZYSZCZENIU_{disk_name}.txt", "w")
        f.write(f"\r\n\r\nSMART DYSKU {disk_name}: {stdout2}")

    if CHECK_SMART:
        proc3 = await asyncio.create_subprocess_exec("./smartctl", "-t", "long","-C", f"/dev/{disk_name}",stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout3, stderr3 = await proc3.communicate()

        f = open(f"Smarty/SMART_PO_LONG_{disk_name}.txt", "w")
        f.write(f"\r\n\r\nSMART LONG {disk_name}: {stdout3}")



if __name__ == '__main__':
    myblkd = BlkDiskInfo()
    all_my_disks = myblkd.get_disks()

    print("Wybierz tryb: BADBLOCKS (Wpisz: BB), DD (Wpisz: DD) i zatwierdz:")

    tryb = input()

    if tryb == "BB":
        DD_MODE = False;
    else:
        DD_MODE = True;

    print("Wybierz sprawdzanie SMART: (0) WYLACZONY (1) WLACZONY")

    smart = input()

    if(smart == "0"):
        CHECK_SMART = False;
    else:
        CHECK_SMART = True;

    print("Wpisz nazwe dysku systemowego np. sda. Ten dysk nie bedzie czyszczony.")
    nazwa_dysku_systemowego = input()


    loop = asyncio.get_event_loop()

    tasks = [
        loop.create_task(wipe_disk("sdb")),
        loop.create_task(wipe_disk("sdd")),
    ]

    loop.set_default_executor(ProcessPoolExecutor())
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()