import sys
from opcua import Client

sys.path.insert(0, "..")


def connect():
    """
    connect to OPC UA server
    """

    try:
        client.connect()
    except:
        print("Dont connect to OPC UA serve")


def disconnect():
    """
    Disconnect to OPC UA server
    """

    client.disconnect()


def get_opc_value(addrstr):
    """
    Get value from OPC UA server by address:
    Can look it in Editor.exe(SimpleScada)->Variable-> Double-click on the necessary variable->address
    """

    var = client.get_node(addrstr)
    print(addrstr[21:] + ' = ' + str(var.get_value()))  # print значения


if __name__ == "__main__":
    client = Client("opc.tcp://127.0.0.1:4841")

# Example:
# connect()
# get_opc_value("ns=4;s=Address Space.PLC_SU3.Tanks._01.R1004_percent_filling_tank") #Адрес переменной в опс (можно посмотреть в Editor simplescada)
# disconnect()
