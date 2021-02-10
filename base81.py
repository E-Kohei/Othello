from string import printable


DIGITS = list(printable)[:81]

def fromBase81Digit(c):
    try:
        return DIGITS.index(c)
    except ValueError:
        raise ValueError("This character cannot be interpretted as base81")

def fromBase81(b81):
    decimal = 0
    for i, c in enumerate(reversed(b81)):
        try:
            decimal += fromBase81Digit(c) * pow(81,i)
        except ValueError:
            raise ValueError("This string cannot be interpretted as base81")
    return decimal

def toBase81Digit(d):
    if 0 <= d <= 80:
        return DIGITS[d]
    else:
        raise ValueError("This number cannot be interpretted as a digit of base81")

def toBase81(n):
    result = toBase81Digit(n % 81)
    n = n // 81
    while n:
        d = n % 81
        result += toBase81Digit(d)
        n = n // 81
    return result[::-1]
