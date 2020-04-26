#!/usr/bin/env python3

# Copyright (C) 2018 Arthur Fabre <arthur@arthurfabre.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import decimal
import csv
import sys
import argparse

EXPENSES_CSV = ['payer', 'amount', 'splitters']
TRANSACTIONS_CSV = ['sender', 'amount', 'recipient']

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
    expenses_reader = csv.DictReader(expenses_file, fieldnames=EXPENSES_CSV)
    for row in expenses_reader:
        # Skip comments
        if row['payer'][0] == '#':
            continue

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
    writer = csv.DictWriter(transactions_file, fieldnames=TRANSACTIONS_CSV)
    writer.writeheader()

    for t in transactions:
        writer.writerow({'sender': t.sender.name, 'amount': t.amount, 'recipient': t.recipient.name})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split some expenses into a minimal set of transactions.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('expenses', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="CSV formatted list of expenses to read, columns: %s, splitters whitespace seperated" % EXPENSES_CSV)
    parser.add_argument('transactions', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="CSV formatted list of minimal transactions to write, columns: %s" % TRANSACTIONS_CSV)
    parser.add_argument('-p', '--precision', type=decimal.Decimal, default=decimal.Decimal('0.01'), help="Smallest usable currency amount when splitting expenses")
    args = parser.parse_args()

    write_csv(transactions(*parse_csv(args.expenses), args.precision), args.transactions)
