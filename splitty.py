#!/usr/bin/env python3

class Person:
    def __init__(self, name):
        self.name = name
        self.balance = 0.0

class Expense:
    def __init__(self, amount, payer, splitters):
        self.amount = amount
        self.payer = payer
        self.splitters = splitters

    # Update the balance of all persons involved
    def balance(self):
        split_amount = self.amount / len(self.splitters)

        for splitter in self.splitters:
            splitter.balance -= split_amount
            self.payer += split_amount

def parse():
    # Load CSV
    # Create persons as required
    # Balance all expenses

    # Check sum of everyone's balance is 0

    # Starting balancing balances, biggest one first
