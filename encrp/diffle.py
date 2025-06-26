'''p=23
g=5
while True:
    op=int(input(" -"))
    if op==1:      
            a=int(input("enter priv a"))
            B=int(input("enter public b"))
            A=g**(a)%p
            print("send",A)
            print(B**(a)%p)
    if op==2:      
            b=int(input("enter priv b"))
            A=int(input("enter public a"))
            B=g**(b)%p
            print("send",B)
            print(A**(b)%p)



'''
p=23
g=5
b=''
while True:
    if op==1:
        x=input("Enter The message to be Encrypted \n--> ")
        b=''
        p=23
        g=5
        priv=int(input("enter ur priv"))
        pub=int(input("enter ur public key"))
        s=pub*(priv)%p
        a={}
        for i in x:
            a[i]=x.count(i)
        mi=min(dict.values(a))
        ma=max(dict.values(a))   
        print()
        print()
        n=len(x)
        for i in range(n):
            b=b+chr((ord(x[i])*s)*((mi*ma)*s))
        print(b)
    if op==2:
        
        
