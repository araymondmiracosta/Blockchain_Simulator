from socket import *
import pickle

class User:
    def __init__(self, username, balance):
        self.username = username
        self.balance = balance

class Tx:
    def __init__(self, payer, payeeOne, payeeTwo, amountPaid, payeeOneAmount, payeeTwoAmount):
        self.payer = payer
        self.payeeOne = payeeOne
        self.payeeTwo = payeeTwo
        self.amountPaid = amountPaid
        self.payeeOneAmount = payeeOneAmount
        self.payeeTwoAmount = payeeTwoAmount

        match payer:
            case "A":
                self.id = 100
            case "B":
                self.id = 200
            case "C":
                self.id = 300
            case "D":
                self.id = 400

users = [User("A", 10), User("B", 10), User("C", 10), User("D", 10)]
confirmedTx = []

invalidString = "invalid"

serverPort = 10001
serverSocket = socket(AF_INET, SOCK_DGRAM)
size = 65536
serverSocket.bind(('', serverPort))
print('The server is ready to receive')

def getUser(username):
    for user in users:
        if (user.username == username):
            return user

def getBalance(username):
    return getUser(username).balance

def sendBalance(username, clientAddress):
    print("Send balance to user")
    serverSocket.sendto(str(getBalance(username)).encode(), clientAddress)

def getTxList(username):
    txForThisUser = []
    for i in confirmedTx:
        if (i.payer == username or i.payeeOne == username or i.payeeTwo == username):
            txForThisUser.append(i)

    return txForThisUser

def sendTxList(username, clientAddress):
    serverSocket.sendto(pickle.dumps(getTxList(username)), clientAddress)
    print("Sent the list of transactions for user " + username)

def auth():
    username, clientAddress = serverSocket.recvfrom(size)
    username = username.decode()
    print("Recieved authentication request from user " + username)
    password, clientAddress = serverSocket.recvfrom(size)
    password = password.decode()
    usernameFound = False
    for user in users:
        if (user.username == username and password == username):
            print("User " + username + " is authenticated")
            usernameFound = True
            break

    # Not authenticated
    if (usernameFound == False):
        print("User not authenticated")
        serverSocket.sendto(invalidString.encode(), clientAddress)
    #authenticated
    else:
        sendBalance(username, clientAddress)
        sendTxList(username, clientAddress)

    return username

def newTransaction(username):
    print("New transaction request")
    request, clientAddress = serverSocket.recvfrom(size)
    newTx = pickle.loads(request)

    balance = getBalance(username)

    if (newTx.amountPaid > balance):
        # balance is too low
        serverSocket.sendto(invalidString.encode(), clientAddress)
        return
    else:
        # balance is valid
        # append new Tx to confirmedTx list
        confirmedTx.append(newTx)

        # update balance for the payer
        payer = getUser(username)
        payer.balance = payer.balance - newTx.amountPaid
        balance = payer.balance

        # update balance for the first payee
        payeeOne = getUser(newTx.payeeOne)
        payeeOne.balance = payeeOne.balance + newTx.payeeOneAmount

        if (newTx.payeeTwo != ""):
            # update balance for the second payee
            payeeTwo = getUser(newTx.payeeTwo)
            payeeTwo.balance = payeeTwo.balance + newTx.payeeTwoAmount

        print("New Tx added to confirmed Tx")

        # send confirmation to client
        serverSocket.sendto(str(getBalance(username)).encode(), clientAddress)

        print("Send Tx addition confirmation")


# TODO: newTransaction()
def main():
#    txOne = Tx("A", "B", "", 5, 5, 0)
#    txTwo = Tx("A", "B", "", 10, 5, 0)
#    confirmedTx.append(txOne)
#    confirmedTx.append(txTwo)

    while 1:
        request, clientAddress = serverSocket.recvfrom(size)
        request = request.decode()

        match (request):
            case "hello":
                username = auth()
            case "recieveList":
                sendBalance(username, clientAddress)
                sendTxList(username, clientAddress)
            case "newTx":
                newTransaction(username)

main()
