import random
import math


def wine_price(rating, age):
    peak_age = rating - 50

    price = rating / 2
    if age > peak_age:
        price *= 5 - (age - peak_age)
    else:
        price *= 5 * ((age + 1) / peak_age)

    price = max(0, price)
    return price


def wine_set1(sample_size=300):
    rows = []
    for i in range(sample_size):
        rating = random.randint(50, 100)
        age = random.randint(0, 50)
        price = wine_price(rating, age)
        # add noise
        a, b = 0.4, 0.8
        price *= a * random.random() + b
        rows.append({'input': (rating, age), 'result': price})

    return rows


def wine_set2(sample_size=300):
    rows = []
    for i in range(sample_size):
        rating = random.randint(50, 100)
        age = random.randint(0, 50)
        aisle = random.randint(1,20)
        bottle_size = [375, 750, 1500, 3000][random.randint(0,3)]
        price = wine_price(rating, age)
        price *= bottle_size/750

        # add noise
        a, b = 0.9, 0.2
        price *= a * random.random() + b
        rows.append({'input': (rating, age, aisle, bottle_size), 'result': price})

    return rows

def wine_set2():
    discount = 0.6
    rows = wine_set1()
    for row in rows:
        if random.random() < 0.5:
            row['result'] *= discount

    return rows