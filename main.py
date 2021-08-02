#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess

from blkinfo import BlkDiskInfo
import asyncio
from concurrent.futures import ProcessPoolExecutor

DD_MODE = False
CHECK_SMART = True

async def wipe_disk(disk_name):

    print(f"Rozpoczynam czyszczenie dysku: {disk_name}")

    if CHECK_SMART:
        proc1 = await asyncio.create_subprocess_exec("./smartctl", "-a", f"/dev/{disk_name}",stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout2, stderr2 = await proc1.communicate()

        f = open(f"Smarty/SMART_PRZED_CZYSZCZENIEM_{disk_name}.txt", "w")
        f.write(f"\r\n\r\nSMART DYSKU {disk_name}: {stdout2}")



    if DD_MODE:
        subprocess.call(['xterm', '-e', f'dd if=/dev/zero of=/dev/{disk_name} bs=64k'])

    else:
        subprocess.call(['xterm', '-e', f'badblocks -sv /dev/{disk_name}'])

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
        DD_MODE = False
    else:
        DD_MODE = True

    print("Wybierz sprawdzanie SMART: (0) WYLACZONY (1) WLACZONY")

    smart = input()

    if(smart == "0"):
        CHECK_SMART = False
    else:
        CHECK_SMART = True



    while True:
        print("Wpisz nazwe dysku systemowego np. sda. Ten dysk nie bedzie czyszczony:")
        nazwa_dysku_systemowego = input()

        print("Powtorz nazwe dysku systemowego:")
        nazwa_dysku_systemowego2 = input()

        if nazwa_dysku_systemowego != nazwa_dysku_systemowego2:
            print("Nazwy dysku systemowego nie zgadzaja sie! Ponow probe.")

        if nazwa_dysku_systemowego == nazwa_dysku_systemowego2:
            break

    tasks = []

    loop = asyncio.get_event_loop()

    for disk in all_my_disks:
        if disk["name"] == nazwa_dysku_systemowego:
            continue

        tasks.append(loop.create_task(wipe_disk(disk["name"])))

    if len(tasks) == 0:
        print("Wykryto: 0 innych dyskow. Przerywam dzialanie programu.")
    else:

        loop.set_default_executor(ProcessPoolExecutor())
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()