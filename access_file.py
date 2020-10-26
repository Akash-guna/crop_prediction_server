
#Should replace with sql afterwards

def open_file():
    f=open("no.txt","r")
    a=int(f.read())
    f.close()
    return a


def update_file():
    f=open("no.txt","r")
    a=int(f.read())
    f.close()
    a=a+1
    f=open("no.txt","w")
    f.write(str(a))
    f.close()
