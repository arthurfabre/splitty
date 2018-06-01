#!/usr/bin/env python3

import csv
import sys
import argparse

# CSV:
# Payer,Amount,Splliter1 Splitter2 ...SplitterN

class Person:
    def __init__(self, name):
        self.name = name
        self.balance = 0.0

    def __repr__(self):
        return "<Person name:%s balance:%f>" % (self.name, self.balance)

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
            self.payer.balance += split_amount

class Transaction:
    def __init__(self, amount, sender, recipient):
        self.amount = amount
        self.sender = sender
        self.recipient = recipient

def parse_csv(expenses_file, transactions_file):
    expenses = []
    persons = {}

    # Parse the expenses from CSV
    expenses_reader = csv.DictReader(expenses_file, fieldnames=['payer', 'amount', 'splitters'])
    for row in expenses_reader:
        payer = persons.setdefault(row['payer'], Person(row['payer']))
        amount = float(row['amount'])
        splitters = [persons.setdefault(name, Person(name)) for name in row['splitters'].split()]

        expenses.append(Expense(amount, payer, splitters))

    return expenses, persons

def transactions(expenses, persons):
    # Balance all the expenses to get everyone's final balance
    for expense in expenses:
        expense.balance()

    # Check everyone's balance adds up to 0
    print(persons)

    if sum([p.balance for p in persons.values()]) != 0:
        sys.exit("Internal error: balance sum not 0")

    # Starting balancing balances, biggest one first

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split some expenses into a minimal set of transactions.')
    parser.add_argument('expenses', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="CSV formatted list of expenses to read")
    parser.add_argument('transactions', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="CSV formatted list of minimal transactions to write")
    args = parser.parse_args()

    transactions(*parse_csv(args.expenses, args.transactions))
