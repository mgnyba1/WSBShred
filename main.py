
import os
import sys
from os import listdir
from blkinfo import BlkDiskInfo
from pySMART import Device
import subprocess
from pip._internal import exceptions
from subprocess import check_output

if __name__ == '__main__':
    myblkd = BlkDiskInfo()
    all_my_disks = myblkd.get_disks()

    print("Wybierz dysk do czyszczenia (wpisz nr i zatwierdz):")

    i = 1;
    for disk in all_my_disks:
        print(f"{i}. {disk['name']}")
        i = i + 1;

    choosen_number = int(input())

    disk_to_shred = all_my_disks[choosen_number-1]


    print(f"Wybrany dysk: {disk_to_shred['name']}.")


    out = check_output(["./smartctl", "-a", f"/dev/{disk_to_shred['name']}"])
    f = open("SMART.txt", "a")
    f.write(f"\r\n\r\nSMART DYSKU {disk_to_shred['name']}: {out}")
    print("SMART Zapisany do pliku SMART.txt");

    print("Rozpoczynam czyszczenie...");

    out = check_output(["./badblocks", "-sv", f"/dev/{disk_to_shred['name']}"])
    print(out)
