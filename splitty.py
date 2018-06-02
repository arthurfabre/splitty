#!/usr/bin/env python3

import decimal
import csv
import sys
import argparse

# CSV:
# Payer,Amount,Splliter1 Splitter2 ...SplitterN

class Person:
    def __init__(self, name):
        self.name = name
        self.balance = decimal.Decimal(0)

    def __repr__(self):
        return "<Person name:%s balance:%f>" % (self.name, self.balance)

class Expense:
    def __init__(self, amount, payer, splitters):
        self.amount = amount
        self.payer = payer
        self.splitters = splitters

    # Update the balance of all persons involved
    def balance(self, precision):
        # Scale things so we can use integer division - ensures the sum of the splits is the original amount
        factor = 1 / precision
        split_amount = ((self.amount * factor) // len(self.splitters)) / factor
        split_remain = ((self.amount * factor) % len(self.splitters)) / factor

        for splitter in self.splitters:
            splitter_amount = split_amount

            # Use up the remainder as we go along
            if split_remain > 0:
                splitter_amount += precision
                split_remain -= precision

            splitter.balance += splitter_amount
            self.payer.balance -= splitter_amount

class Transaction:
    def __init__(self, amount, sender, recipient):
        self.amount = amount
        self.sender = sender
        self.recipient = recipient

        self.sender.balance -= amount
        self.recipient.balance += amount

    def __repr__(self):
        return "<Transaction from:%s to:%s amount:%s>" % (self.sender, self.recipient, self.amount)

def parse_csv(expenses_file):
    expenses = []
    persons = {}

    # Parse the expenses from CSV
    expenses_reader = csv.DictReader(expenses_file, fieldnames=['payer', 'amount', 'splitters'])
    for row in expenses_reader:
        payer = persons.setdefault(row['payer'], Person(row['payer']))
        amount = decimal.Decimal(row['amount'])
        splitters = [persons.setdefault(name, Person(name)) for name in row['splitters'].split()]

        expenses.append(Expense(amount, payer, splitters))

    return expenses, persons.values()

def transactions(expenses, persons, precision):
    # Balance all the expenses to get everyone's final balance
    for expense in expenses:
        expense.balance(precision)

    # Check everyone's balance adds up to 0
    if sum([p.balance for p in persons]) != 0:
        sys.exit("Internal error: balance sum not 0")

    transactions = []

    while any(p.balance != 0 for p in persons):
        debtor = max(persons, key=lambda p: p.balance)
        creditor = min(persons, key=lambda p: p.balance)

        transactions.append(Transaction(min(abs(debtor.balance), abs(creditor.balance)), debtor, creditor))

    return transactions

def write_csv(transactions, transactions_file):
    # TODO
    print(transactions)
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split some expenses into a minimal set of transactions.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('expenses', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="CSV formatted list of expenses to read")
    parser.add_argument('transactions', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="CSV formatted list of minimal transactions to write")
    parser.add_argument('-p', '--precision', type=decimal.Decimal, default=decimal.Decimal('0.01'), help="Smallest usable currency amount when splitting expenses")
    args = parser.parse_args()

    write_csv(transactions(*parse_csv(args.expenses), args.precision), args.transactions)
