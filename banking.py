# Write your code here
import random
import sqlite3
import sys

IIN = "0400000"


def main():
    while True:
        print("1. Create an account \n2. Log into account \n0. Exit")
        options = int(input())

        if options == 1:
            create_account()
        elif options == 2:
            account_info()
        else:
            sys.exit(0)


def create_account():
    card_number = int(generate_card())
    pin_number = random.randint(1000, 9999)

    store_card(card_number, pin_number)

    print("You card has been created.")
    print(f"Your card number: \n{card_number}")
    print(f"Your card PIN: \n{pin_number}")


def generate_card():
    card_number = IIN + str(random.randint(100000000, 999999999))
    number_split = []
    for digits in card_number:
        number_split.append(int(digits))
    for i in range(0, len(number_split)):
        if i % 2 == 0:
            continue
        else:
            if number_split[i] * 2 > 9:
                number_split[i] = (number_split[i] * 2) - 9
            else:
                number_split[i] = number_split[i] * 2

    number_split.pop(0)
    checksum = 10 - (sum(number_split) % 10)
    if checksum > 9:
        checksum = 0
    else:
        pass

    final_card = card_number[1:] + str(checksum)
    return final_card


def account_info():
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()

    input_card = input("Enter your card number: ")
    input_pin = input('Enter your PIN: ')

    result = cur.execute(f"SELECT number, pin FROM card \
                          WHERE number = {input_card} \
                          AND pin = {input_pin}").fetchone()
    conn.close()

    if not result:
        print("Wrong card number or PIN!")
        main()
    else:
        print("You have successfully logged in!")
        portal(input_card)


def portal(input_card):
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()

    while True:
        print("1. Balance \n2. Add income \n3. Do transfer \n4. Close account \n5. Logout \n0. Exit")
        options = int(input())

        balance = cur.execute(f"SELECT balance FROM card \
                              WHERE number = {input_card}").fetchone()[0]

        if options == 1:
            print(f"Balance: {balance}")

        elif options == 2:
            add_money = int(input("Enter income:"))
            cur.execute(f"UPDATE card SET balance=balance+{add_money} WHERE number={input_card}")
            conn.commit()
            print("Income was added!")

        elif options == 3:
            transfer_card = input("Enter card number:")
            if len(transfer_card) != 16:
                print("Probably you made a mistake in the card number. Please try again!")
            elif luhn_check(transfer_card) != 0:
                print("Probably you made a mistake in the card number. Please try again!")
            elif transfer_card == input_card:
                print("You can't transfer money to the same account!")
            elif not check_card_exists(transfer_card):
                print("Such a card does not exist.")
            else:
                to_be_tfd = int(input("Enter how much money you want to transfer:"))
                if to_be_tfd > balance:
                    print("Not enough money!")
                else:
                    cur.execute(f"UPDATE card SET balance=balance-{to_be_tfd} WHERE number={input_card}")
                    cur.execute(f"UPDATE card SET balance=balance+{to_be_tfd} \
                              WHERE number={transfer_card}")
                    conn.commit()
                    print("Success!")

        elif options == 4:
            cur.execute(f"DELETE FROM card WHERE number={input_card}")
            conn.commit()
            print("The account has been closed!")
            conn.close()
            main()

        elif options == 5:
            print("You have successfully logged out!")
            conn.close()
            main()

        elif options == 0:
            print("Bye!")
            conn.close()
            sys.exit(0)

        else:
            continue


def check_card_exists(transfer_card):
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    status = cur.execute(f"SELECT number FROM card WHERE number = {transfer_card}").fetchone()
    conn.close()
    return status


def luhn_check(transfer_card):
    number_split = []
    for digits in transfer_card:
        number_split.append(int(digits))
    for i in range(0, len(number_split)):
        if i % 2 == 0:
            if number_split[i] * 2 > 9:
                number_split[i] = (number_split[i] * 2) - 9
            else:
                number_split[i] = number_split[i] * 2
    return sum(number_split) % 10


def create_db():
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS card ( \
                id INTEGER PRIMARY KEY, \
                number TEXT, \
                pin TEXT, \
                balance INTEGER DEFAULT 0) \
                ")
    conn.commit()
    conn.close()


def store_card(card_number, pin):
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute(f"INSERT INTO card(number, pin) VALUES({card_number},{pin})")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db()
    main()
