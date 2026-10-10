#!/usr/bin/env python3

import os


class Input:
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
                    self.buffer = ["EOF"]
                    self.i, self.n = 0, 1
        c = self.buffer[self.i]
        self.i += 1
        return c

    def ungetc(self):
        if self.i > 0:
            self.i -= 1


class Scanner:
    KEYWORDS = {
        "print": "PRINT",
        "def": "DEF",
        "iread": "IREAD",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "return": "RETURN",
    }
    ARITHMETIC = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLY",
        "/": "DIVIDE",
        "%": "MODULO",
    }
    REL_OPS = {
        "==": "EQUALS",
        "!=": "NE",
        ">=": "GTE",
        "<=": "LTE",
        "<": "LT",
        ">": "GT",
    }

    def scan(self):
        inp = self.input
        c = inp.getc()
        lexeme = ""
        token = ""

        if c in list(" \t\n\r"):
            while c in list(" \t\n\r"):
                c = inp.getc()
                if c == "EOF":
                    break
        if c == "EOF":
            return ("EOF", lexeme)
        if c.isalpha():
            while c.isalpha():
                lexeme += str(c)
                c = inp.getc()
                if c == "EOF":
                    break
            inp.ungetc()
            if lexeme in self.KEYWORDS:
                return (lexeme.upper(), lexeme)
            return ("ID", lexeme)
        elif c.isdigit():
            while c.isdigit():
                lexeme += str(c)
                c = inp.getc()
                if c == "EOF":
                    break
            inp.ungetc()
            return ("NUM", lexeme)
        elif c in self.ARITHMETIC:
            lexeme += str(c)
            return (self.ARITHMETIC[lexeme], lexeme)
        elif c in list("=!<>"):
            lexeme += str(c)
            c = inp.getc()
            if lexeme + c in self.REL_OPS:
                lexeme += str(c)
                return (self.REL_OPS[lexeme], lexeme)
            inp.ungetc()
            if lexeme == "=":
                return ("ASSIGN", lexeme)
            return (lexeme, lexeme)
        else:
            lexeme += str(c)
            return (str(c), lexeme)

    def __init__(self, input: Input):
        self.input = input
        out = self.scan()
        while out[0] != "EOF":
            print(out)
            out = self.scan()


i = Input()
s = Scanner(i)
