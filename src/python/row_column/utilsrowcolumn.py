import iris

def add_64000_rows(table_name: str):

    if (table_name == "Demo.BankTransactionColumn"):

        g = iris.gref("^CATa.BJqo.1")

    elif (table_name == "Demo.BankTransactionIndex"):

        g = iris.gref("^CATa.C4g3.1")

    elif (table_name == "Demo.BankTransactionMix"):

        g = iris.gref("^CATa.CfQt.1")

    elif (table_name == "Demo.BankTransactionRow"): # row storage
        g = iris.gref("^CATa.BArF.1")

    else:
        print("Table name not found")
        return

    max = g[None]

    n= 64000
    for i in range(n):
        g[max+i]=g[n]

    g[None] = max+n

    if table_name == "Demo.BankTransactionColumn":
        iris.cls('RowColumn.Utils').AppendLastVector()
    if table_name == "Demo.BankTransactionMix":
        iris.cls('RowColumn.Utils').AppendLastVectorMix()

    

