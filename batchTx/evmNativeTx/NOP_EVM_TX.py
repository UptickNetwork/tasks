from web3 import Web3
from web3.auto import w3

# SentTotalTX = Number of attempts in one batch
SentTotalTX = 5
# Number of attemtps for verifying TX, If you use low count, Most ptobably last TX'll be always failed. If you use high value, Total script execution will take so much time.
failcheckcount = 220
totalbatch = 1  # Number of time will send. Total TX = totalbatch x SentTotalTX

# url is node EVM API URL
url = 'http://xx.xx.xx.xx:8547/'
web3 = Web3(Web3.HTTPProvider(url))
gasPrice = web3.toWei('20', 'gwei')
chainid = 7000

sender_addr = '0x37a6584D1fdc976E077C6307b3f431eDDfF827C9'
sender_priv_key = '......'
recipent_addr = '0x37a6584D1fdc976E077C6307b3f431eDDfF827C9'

def logtofile(log):
    filename = "uptick_send_evm_tx.log"
    file1 = open(filename, "a")
    print(log)
    file1.write(log + '\n')
    file1.close()

def send_tx(STX):
    i = 0
    last = ""
    while i < STX:
        #get the nonce.  Prevents one from sending the transaction twice
        nonce = web3.eth.getTransactionCount(sender_addr)

        #build a transaction in a dictionary
        tx = {
            'nonce': nonce,
            'to': recipent_addr,
            'value': 1000000000,
            'gas': 21000,
            'maxFeePerGas': web3.toWei(20, 'gwei'),
            'maxPriorityFeePerGas': web3.toWei(2, 'gwei'),
            'chainId': chainid
        }

        #sign the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, sender_priv_key)


        try:
            #send transaction
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            i +=1
        except ValueError as e:
        #    print(e)
            pass
        else:
            #get transaction hash
            txhash = web3.toHex(tx_hash)
            if txhash not in status:
                status.update({txhash: "False"})
                logtofile("TX Sent = " + str(i) + " = " + txhash)


def check_tx():
    restart = True
    check = 0
    failcount = 0
    while restart:
        if "False" in status.values():
            for hash, stat in status.items():
                if stat == "False":
                    receipt = ""
                    try:
                        receipt = web3.eth.getTransactionReceipt(hash)
                    except:
                            if failcount < failcheckcount:
                                failcount += 1
                            else:
                                logtofile("TX Failed = " + hash)
                                status.update({hash: "Failed"})
                                check += 1
                    else:
                        if receipt["status"] == 1:
                            logtofile("TX Verified = " + hash)
                            #print(hash, receipt)
                            status.update({hash: "True"})
                        else:
                            if failcount < failcheckcount:
                                failcount += 1
                            else:
                                logtofile("TX Failed = " + hash)
                                status.update({hash: "Failed"})
                                check += 1                              
        else:
            if failcount > 0:
                logtofile("Failed TX Resending = " + str(check))
                #SentTotalTX = failcount
                send_tx(check)
                check_tx()
            restart = False


batchnum = 0
while batchnum < totalbatch:
    status = {}
    logtofile("Sending Batch" + str(batchnum))
    send_tx(SentTotalTX)
    check_tx()
    batchnum += 1
    if "False" in status.values():
        check_tx()


