#!/bin/python
import subprocess
import re

from multiprocessing import Process


sender_addr = "uptick1lrlc6q0zr20ltxa09takuln0rsg6n897ydg8qh"
recipent_addr = "uptick1lrlc6q0zr20ltxa09takuln0rsg6n897ydg8qh"
# Just change chainid after --chain-id=
chainid = "--chain-id=uptick_7000-2"
walletname = "EmreNOP"
#Howmany uptick are u gonna send?
stoken = "1auptick"
fees = "20auptick"
gasadjustment = "1.5"
# Number of time TX's status will check and if still fails will send new TX
failcheckcount = 10
#Update below for Total TX in one batch
SentTotalTX = 10
totalbatch = 3  # Number of time will send. Total TX = totalbatch x SentTotalTX

binary = "/home/emre/scripts/uptick/uptickd"


def logtofile(log):
    filename = "uptick_send_tx.log"
    file1 = open(filename, "a")
    print(log)
    file1.write(log + '\n')
    file1.close()


def send_token(addr, STX):
    i = 0
    last = ""
    while i < STX:
        get = subprocess.run([binary, "tx", "bank", "send", sender_addr,
                              addr, stoken, chainid, "--from", walletname, "--keyring-backend", "test", "--fees", fees, "--gas-adjustment", gasadjustment, "-y", "--log_format", "json", "-b", "sync"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = get.stdout.decode("utf-8"), get.stderr.decode("utf-8")
        error = re.split("\n+", str(err))
        if "Error" in error[0]:
            return error[0]
        else:
            get = out.split(': ')
            dx = get[13].split('\n')
            status.update({dx[0]: "False"})
            #This will try to make TX until create new one.
            if last != dx[0]:
                last = dx[0]
                logtofile("TX Sent = " + str(i) + " - " + last)
                i += 1


def check_tx2():
    restart = True
    check = 0
    failcount = 0
    while restart:
        if "False" in status.values():
            for hash, stat in status.items():
                if stat == "False":
                    get = subprocess.run([binary, "query", "tx", "-o", "json",
                                         hash], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    out, err = get.stdout.decode(
                        "utf-8"), get.stderr.decode("utf-8")

                    error = re.split("\n+", err)
                    if "not found" in error[0]:
                        status.update({hash: "False"})
                        logtofile("TX Not Found = " + hash)
                        if check == failcheckcount:
                            status.update({hash: "Failed"})
                            logtofile("TX Failed = " + str(failcount) + hash)
                            failcount += 1
                        check += 1

                    else:
                        status.update({hash: "True"})
                        logtofile("TX Found = " + hash)
        else:
            if failcount > 0:
                logtofile("ReSending TX")
                SentTotalTX = failcount
                Sent(SentTotalTX)
            restart = False


def Sent(STT):
    #Below is for multiprocessing. Still reqires development.
    p1 = Process(target=send_token(recipent_addr, STT))
    p1.start()
    #p3 = Process(target=send_token(recipent_addr, STT))
    #p3.start()
    p2 = Process(target=check_tx2)
    p2.start()
    #p3.join()
    p2.join()
    p1.join()


batchnum = 0
while batchnum < totalbatch:
    status = {}
    logtofile("Sending Batch" + str(batchnum))
    Sent(SentTotalTX)
    batchnum += 1
