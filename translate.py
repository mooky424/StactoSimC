# translate.py
# asioson@ateneo.edu
# september 11, 2026

# symbol processing routine
class inpData():
    def __init__(self):
        self.buffer = list(input())
        self.i, self.n = 0, len(self.buffer)
    def getc(self):
        while self.n == 0 or self.i == self.n:
            if self.i == self.n:
                try:
                    self.buffer = list(input())
                    self.i, self.n = 0, len(self.buffer)
                except EOFError:
                    self.buffer = [-1] 
                    self.i, self.n = 0, 1
        c = self.buffer[self.i]
        self.i += 1
        return c
    def ungetc(self):
        if self.i > 0:
            self.i -= 1


# lexical analyzer (scanner)
def scan():
    global inp
    c = inp.getc()
    lexeme = ""
    if c == -1:
        return ("EOF",lexeme)
    if c in list(" \t\n\r"):
        while c in list(" \t\n\r"):
            c = inp.getc()
            if c == -1: break
    if c == -1:
        return ("EOF",lexeme)
    if c.isalpha():
        while c.isalpha():
            lexeme += str(c)
            c = inp.getc()
            if c == -1: break
        inp.ungetc()
        if lexeme == "print":
            return ("PRINT",lexeme)
        return ("ID",lexeme)
    elif c.isdigit():
        while c.isdigit():
            lexeme += str(c)
            c = inp.getc()
            if c == -1: break
        inp.ungetc()
        return ("NUM",lexeme)
    else:
        lexeme += str(c)
        return (str(c),lexeme)    


# code generator

symTab = {}
mem = []
codeSize = 0

def codeGen(stac):
    global mem, codeSize
    mem.append(" ".join(stac))
    codeSize += 1
    


# syntax analyzer (syntax directed translation)

counter = 0
def newtmp():
    global counter
    t = "t" + str(counter)
    counter += 1
    return t


def match(t):
    global curToken, lex
    if t == curToken:
        curToken, lex = scan()
    else:
        print("syntax error")
        curToken, lex = scan()


def Factor():
    global curToken, lex, stk, symTab
    if curToken == "NUM":
        NUM_lex = lex
        match("NUM")
        #print("A5")
        stk.append(NUM_lex)
        #print("::stack", stk)
    elif curToken == "ID":
        ID_lex = lex
        match("ID")
        #print("A1")
        stk.append(ID_lex)
        #print("::stack", stk)
        symTab[ID_lex] = None


def Term():
    global curToken, lex, stk
    Factor()
    while curToken == "*":
        match("*")
        Factor()
        #print("A4")
        a,b = stk[-2:]
        stk = stk[:-2]
        c = newtmp()
        stk.append(c)
        codeGen([c,"=",a,"*",b])
        #print("::stack", stk)
        symTab[c] = None


def Expr():
    global curToken, lex, stk, symTab
    Term()
    while curToken == "-":
        match("-")
        Term()
        #print("A3")
        a,b = stk[-2:]
        stk = stk[:-2]
        c = newtmp()
        stk.append(c)
        codeGen([c,"=",a,"-",b])
        #print("::stack", stk)
        symTab[c] = None


def Stmt():
    global curToken, lex, stk
    if curToken == "ID":
        ID_lex = lex
        match("ID")
        #print("A1")
        stk.append(ID_lex)
        #print("::stack", stk)
        match("=")
        Expr()
        #print("A2")
        a,b = stk[-2:]
        stk = stk[:-2]
        codeGen([a,"=",b])
        #print("::stack", stk)
    elif curToken == "PRINT":
        match("PRINT")
        match("(")
        Expr()
        match(")")
        a = stk[-1]
        stk = stk[:-1]
        codeGen(["print","(", a, ")"])

def SeqStmts():
    global curToken, lex, stk
    if curToken in ["ID","PRINT"]:
        Stmt()
        match(";")
        SeqStmts()

# generate output

def allocateSpace():
    global mem, symTab
    i = 0
    for i, sym in enumerate(symTab):
        symTab[sym] = f"mem[{i+codeSize}]"
    

def genOutput():
    global mem, symTab, codeSize
    print(f"[mem]")
    print(f"codeSize {codeSize}")
    print(f"memSize 1024")
    print(f"[code]")
    for stac in mem:
        print(stac)
    print(f"[symTab]")
    for i, (sym, val) in enumerate(symTab.items()):
        print(sym, val)


# SDT driver

stk = []
inp = inpData()
curToken,lex = scan()
SeqStmts()
codeGen(["halt"])
allocateSpace()
symTab["main"] = "0"
genOutput()
