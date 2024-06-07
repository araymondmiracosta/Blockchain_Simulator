from socket import *
import pickle

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

confirmedTx = []
temporaryTx = []
rejectedTx = []

serverName = 'localhost'
serverPort = 10001
clientSocket = socket(AF_INET, SOCK_DGRAM)
size = 65536

def displayTx(TxList, message):
    print(message)
    data_table = [
        ['ID', 'Payer', 'Payee One', 'Payee Two', 'Amount Paid', 'Amount Paid to Payee One', 'Amount Paid to Payee Two']
    ]

    for j in TxList:
        temp_table = [str(j.id), j.payer, j.payeeOne, j.payeeTwo, str(j.amountPaid) + " BTC", str(j.payeeOneAmount) + " BTC", str(j.payeeTwoAmount) + " BTC"]
        data_table.append(temp_table)

    for row in data_table:
        print("{: ^20} {: ^20} {: ^20} {: ^20} {: ^20} {: ^20} {: ^40}".format(*row))

def recieveConfirmedTx():
    clientSocket.sendto("recieveList".encode(), (serverName, serverPort))
    undecodedData, serverAddress = clientSocket.recvfrom(size)
    undecodedData.decode()
    undecodedData, serverAddress = clientSocket.recvfrom(size)
    returnedTx = pickle.loads(undecodedData)
    confirmedTx.clear()
    for i in returnedTx:
        confirmedTx.append(i)

def menu():
    print("Menu")
    print("1. TX")
    print("2. List")
    print("3. Quit")

    return(input("Select an option (1-3): "))

def auth():
    username = input('Enter the username: ')
    password = input('Enter the password: ')

    clientSocket.sendto("hello".encode(), (serverName, serverPort))
    clientSocket.sendto(username.encode(), (serverName, serverPort))
    clientSocket.sendto(password.encode(), (serverName, serverPort))

    undecodedData, serverAddress = clientSocket.recvfrom(size)

    balance = undecodedData.decode()

    while (balance == "invalid"):
        print("Incorrect username or password.")
        print("1. Enter the username and password again")
        print("2. Quit the program.")
        option = input("Select an option (1, 2): ")
        if (option == "1"):
            username = input('Enter the username: ')
            password = input('Enter the password: ')
            clientSocket.sendto("hello".encode(), (serverName, serverPort))
            clientSocket.sendto(username.encode(), (serverName, serverPort))
            clientSocket.sendto(password.encode(), (serverName, serverPort))
            undecodedData, serverAddress = clientSocket.recvfrom(size)
            balance = undecodedData.decode()
        if (option == "2"):
            quit(0)

    undecodedData, serverAddress = clientSocket.recvfrom(size)
    returnedTx = pickle.loads(undecodedData)
    confirmedTx.clear()
    for i in returnedTx:
        confirmedTx.append(i)

    return username, balance

def newTransaction(username, balance):
    payer = username
    payeeOne = ""
    payeeTwo = ""

    match username:
        case "A":
            highestID = 100
        case "B":
            highestID = 200
        case "C":
            highestID = 300
        case "D":
            highestID = 400

    highestID = highestID - 1

    for i in confirmedTx:
        thisTx = i
        if (thisTx.payer == username and thisTx.id > highestID):
            highestID = thisTx.id

    highestID = highestID + 1

    amountPaid = int(input("Enter amount to transfer: "))

    match username:
            case "A":
                payeeOne = input("Enter username for the first payee (B, C, D): ")
            case "B":
                payeeOne = input("Enter username for the first payee (A, C, D): ")
            case "C":
                payeeOne = input("Enter username for the first payee (A, B, D): ")
            case "D":
                payeeOne = input("Enter username for the first payee (A, B, C): ")

    payeeOneAmount = int(input("Enter amount to transfer to the first payee: "))

    while (payeeOneAmount > amountPaid):
        print("The maximum amount allowed is", amountPaid)
        payeeOneAmount = int(input("Enter an amount: "))

    if (payeeOneAmount == amountPaid):
        payeeTwo = ""
        payeeTwoAmount = 0
    else:
        match username:
            case "A":
                match payeeOne:
                    case "B":
                        payeeTwo = input("Enter username for the second payee (C, D): ")
                    case "C":
                        payeeTwo = input("Enter username for the second payee (B, D): ")
                    case "D":
                        payeeTwo = input("Enter username for the second payee (B, C): ")
            case "B":
                match payeeOne:
                    case "A":
                        payeeTwo = input("Enter username for the second payee (C, D): ")
                    case "C":
                        payeeTwo = input("Enter username for the second payee (A, D): ")
                    case "D":
                        payeeTwo = input("Enter username for the second payee (A, C): ")
            case "C":
                match payeeOne:
                    case "A":
                        payeeTwo = input("Enter username for the second payee (B, D): ")
                    case "B":
                        payeeTwo = input("Enter username for the second payee (A, D): ")
                    case "D":
                        payeeTwo = input("Enter username for the second payee (A, B): ")
            case "D":
                match payeeOne:
                    case "A":
                        payeeTwo = input("Enter username for the second payee (B, C): ")
                    case "B":
                        payeeTwo = input("Enter username for the second payee (A, C): ")
                    case "C":
                        payeeTwo = input("Enter username for the second payee (A, B): ")

    payeeTwoAmount = amountPaid - payeeOneAmount

    print("The second payee will recieve", payeeTwoAmount, "BTC")

    newTx = Tx(payer, payeeOne, payeeTwo, amountPaid, payeeOneAmount, payeeTwoAmount)
    newTx.id = highestID
    temporaryTx.append(newTx)

    clientSocket.sendto("newTx".encode(), (serverName, serverPort))
    clientSocket.sendto(pickle.dumps(newTx), (serverName, serverPort))
    undecodedData, serverAddress = clientSocket.recvfrom(size)
    confirmation = undecodedData.decode()
    temporaryTx.remove(newTx)

    if (confirmation == "invalid"):
        # mark as rejected
        rejectedTx.append(newTx)
        new_balance = balance
        print("Transaction rejected.")
    else:
        # mark as confirmed
        confirmedTx.append(newTx)
        new_balance = undecodedData.decode()

    return new_balance

def main():
    username, balance = auth()

    print("Authentication successful for user", username)
    print("")
    print("Current balance for user", username + ": ", balance, "BTC")

    displayTx(confirmedTx, "Confirmed Tx")
    print("")
    displayTx(rejectedTx, "Rejected Tx")


    while 1:
        print("")

        print("Logged in as user:", username)
        match (menu()):
            case "1":
                balance = newTransaction(username, balance)
            case "2":
                recieveConfirmedTx()

                print("\nCurrent balance for user", username + ": ", balance, "BTC")
                print("Transaction List Display")
                displayTx(confirmedTx, "Confirmed Tx")
                print("")
                displayTx(rejectedTx, "Rejected Tx")
            case "3":
                quit(0)

main()
clientSocket.close()
