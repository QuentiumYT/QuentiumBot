import random, requests, sys
from _tte import cypher, alpha, url

# Send random requests to TimeToEat website

# 130 for 11h30 to 13h30 (10 per 10 minutes)
number_request = 130
# Send the specified number
if len(sys.argv) > 1:
    if sys.argv[1].isdigit():
        number_request = int(sys.argv[1])

# Generates the random numbers
for i in range(number_request):
    if i < 5:
        count_people = random.randint(50, 75)
    elif i < 40:
        count_people = random.randint(30, 55)
    elif i < 60:
        count_people = random.randint(400, 700)
    elif i < 70:
        count_people = random.randint(350, 580)
    elif i < 80:
        count_people = random.randint(300, 460)
    elif i < 95:
        count_people = random.randint(250, 350)
    elif i < 120:
        count_people = random.randint(25, 75)
    else:
        count_people = 0
    count_debit = random.randint(8, 12)

    # Generate a key for the cypher
    key = random.randint(10, len(alpha))
    # Cypher the data
    count_crypt = cypher(str(count_people), key)
    debit_crypt = cypher(str(count_debit), key)
    # Pass the args with the GET method
    args = "?count=" + count_crypt + "&debit=" + debit_crypt + "&key=" + str(key)
    requests.get(url + args)

print("All requests have been sent successfully!")
