import irisnative, random, tqdm, colorama

conn = irisnative.createConnection(hostname="localhost", port=1972, namespace="IRISAPP", username="SuperUser", password="SYS",sharedmemory=True)

def write(numKeys):
    
    irispy = irisnative.createIris(conn)
    iter = tqdm.tqdm(range(numKeys), "Writing", bar_format='{l_bar}{bar}')
    for i in iter:
        irispy.set('^exampleKV(key'+str(i)+')','val'+str(random.randint(0,999999)))
    return(iter.format_dict["elapsed"])

def random_read(numKeys, numReads):
    irispy = irisnative.createIris(conn)
    iter = tqdm.tqdm(range(numReads), "Reading", bar_format='{l_bar}{bar}')
    for i in iter:
        irispy.get('^exampleKV','key'+str(random.randint(0,numKeys)))
    return(iter.format_dict["elapsed"])

def print_results(product, action, time, count):
    print(f"\n{colorama.Fore.CYAN}{product}{colorama.Style.RESET_ALL} {action}:{colorama.Fore.YELLOW}{count:,d}{colorama.Style.RESET_ALL}/{colorama.Fore.YELLOW}{time:5.2f}{colorama.Style.RESET_ALL} ⇒ {colorama.Fore.GREEN}{count/time:12,.2f}{colorama.Style.RESET_ALL} msg/sec\n\n")

if __name__ == "__main__":
    numWrites = 50000
    numReads  = 75000
    print_results("IRIS", "Writes", write(numWrites), numWrites)
    print_results("IRIS", "Reads ", random_read(numWrites, numReads), numReads)
