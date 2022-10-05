import iris

def get_max_key(g):
    max = g.order([])
    while g.order([max]) is not None:
        max = g.order([max])
    return max

for i in range(5):
    g = iris.gref(f"^CATa.BJqo.1.V{i+1}")
    print(i+1)
    max = get_max_key(g)
    print(max)
    if int(max) >= 2 :
        print("double")
        print(g.get([1]))
        # g[max+1]=g[max]
        # g[max]=g[max-1]


rs = iris.sql.exec("build index for table Demo.BankTransactionRow")
rs = iris.sql.exec("SELECT COUNT(*) FROM Demo.BankTransactionRow")

for row in rs:
    row_count = row[0]