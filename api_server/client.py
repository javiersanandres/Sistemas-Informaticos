import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_db_url = 'http://localhost:' + os.getenv('API_SERVER_PORT')


def register_customer(
        username,
        password,
        address,
        creditcard,
        email,
        description=""):
    print("CREATING CUSTOMER: " + description)
    r = requests.put(url=api_db_url + '/register',
                     headers={"Content-Type": "application/json"},
                     data=json.dumps({"username": f'{username}',
                                      "password": f'{password}',
                                      "address": f'{address}',
                                      "creditcard": f'{creditcard}',
                                      "email": f'{email}'}))
    print(r.text)


def login_customer(email, password, description):
    print("LOGIN CUSTOMER: " + description)
    r = requests.post(
        url=api_db_url + '/login',
        headers={"Content-Type": "application/json"},
        data=json.dumps({"email": f'{email}',
                         "password": f'{password}'}))
    print(r.text)

    if r.status_code == 200:
        return json.loads(r.text)['customerid']


def delete_customer(customerid, description):
    print("DELETE CUSTOMER: " + description)
    r = requests.delete(
        url=api_db_url + f'/{customerid}',
        headers={"Content-Type": "application/json"})

    print(r.text)


def get_user_details(customerid, description):
    print("CUSTOMER INFORMATION: " + description)
    r = requests.get(
        url=api_db_url + f'/{customerid}',
        headers={"Content-Type": "application/json"})

    print(json.loads(r.text)['data'])
    print("")


def add_balance(customerid, amount, description):
    print("ADD BALANCE TO CUSTOMER: " + description)
    r = requests.post(
        url=api_db_url + f'/balance/{customerid}',
        headers={"Content-Type": "application/json"},
        data=json.dumps({"amount": f'{amount}'}))

    print(r.text)


def get_products(num_rows):
    print(f"GET {num_rows} PRODUCTS")
    r = requests.get(
        url=api_db_url + f'/products',
        headers={"Content-Type": "application/json"})

    if r.status_code == 200:
        products = json.loads(r.text)
        products = products['data']

        for i in range(num_rows):
            print(products[i])

        print("")
        return products[:num_rows]

    print(r.text)


def get_product_details(prod_id, description):
    print(f"GET INFORMATION FOR PRODUCT WITH ID {prod_id}: " + description)
    r = requests.get(
        url=api_db_url + f'/products/{prod_id}',
        headers={"Content-Type": "application/json"})

    if r.status_code == 200:
        print(json.loads(r.text)['data'])
        print("")
    else:
        print(r.text)


def create_order(customerid):
    print(f"CREATE ORDER FOR CUSTOMER WITH ID: {customerid}")
    r = requests.put(
        url=api_db_url + f'/order/{customerid}',
        headers={"Content-Type": "application/json"})
    print(r.text)

    if r.status_code == 201:
        return json.loads(r.text)['orderid']


def delete_order(orderid, description):
    print(f"DELETE ORDER WITH ID {orderid}: " + description)
    r = requests.delete(
        url=api_db_url + f'/order/{orderid}',
        headers={"Content-Type": "application/json"})

    print(r.text)


def get_customer_orders(customerid, description):
    print(f"GET ORDERS FROM CUSTOMER WITH ID {customerid}: " + description)
    r = requests.get(
        url=api_db_url + f'/orders/{customerid}',
        headers={"Content-Type": "application/json"})

    if r.status_code == 200:
        for order in json.loads(r.text)['data']:
            print(order)
        print("")
    else:
        print(r.text)


def get_order_details(orderid, description):
    print(f"GET INFORMATION FOR ORDER WITH ID {orderid}: " + description)
    r = requests.get(
        url=api_db_url + f'/order/{orderid}',
        headers={"Content-Type": "application/json"})

    if r.status_code == 200:
        order_info = json.loads(r.text)['data']

        if 'order' in order_info.keys():
            print(order_info['order'])
            print("{'Products': ")
            for product in order_info['products']:
                print("\t" + str(product))
            print("}")
        else:
            print(order_info)
            print("")
    else:
        print(r.text)


def add_product(orderid, prod_id, quantity, description):
    print(
        f"ADD {quantity} OF PRODUCT WITH ID {prod_id} TO ORDER" +
        f"WITH ID {orderid}: " + description)
    r = requests.post(
        url=api_db_url + f'/order/{orderid}/products',
        headers={"Content-Type": "application/json"},
        data=json.dumps({"prod_id": f'{prod_id}',
                        "quantity": f'{quantity}'}))

    print(r.text)


def remove_product(orderid, prod_id, quantity, description):
    print(
        f"REMOVE {quantity} OF PRODUCT WITH ID {prod_id} TO ORDER" +
        f"WITH ID {orderid}: " + description)
    r = requests.delete(
        url=api_db_url + f'/order/{orderid}/products',
        headers={"Content-Type": "application/json"},
        data=json.dumps({"prod_id": f'{prod_id}',
                        "quantity": f'{quantity}'}))

    print(r.text)


def pay_order(orderid, description):
    print(f"PAY ORDER WITH ID {orderid}: " + description)
    r = requests.post(
        url=api_db_url + f'/order/{orderid}/pay',
        headers={"Content-Type": "application/json"})

    print(r.text)


if __name__ == "__main__":
    try:
        register_customer(
            'pepe1',
            'pepe2',
            'pepe3',
            'pepe4',
            'pepe5@gmail.com',
            'Non-existing customer')
        register_customer(
            'pepe1',
            'pepe2',
            'pepe3',
            'pepe4',
            'pepe6@gmail.com',
            'Non-existing customer')
        register_customer(
            'adsf',
            'adsf',
            'adsf',
            'adsf',
            'pepe5@gmail.com',
            'Existing customer')

        login_customer(
            'pepe5@gmail.com',
            'pepe',
            "Invalid credentials")
        login_customer(
            'pepe7@gmail.com',
            'pepe',
            "Non-existing customer")
        customerid = login_customer(
            'pepe5@gmail.com',
            'pepe2',
            "Success")
        customerid2 = login_customer(
            'pepe6@gmail.com',
            'pepe2',
            "Success")

        delete_customer(customerid2, "Existing customer")
        delete_customer(customerid2 + 1, "Non-existing customer")

        get_user_details(customerid, "Balance before update")
        add_balance(customerid, 0, "Non-positive balance")
        get_user_details(customerid, "Balance after failure")
        add_balance(customerid, 0.5, "Success")
        get_user_details(customerid, "Balance after update")

        products = get_products(10)
        get_product_details(products[7]['prod_id'], "Success")

        get_customer_orders(customerid, "No orders from that customer")
        orderid = create_order(customerid)
        orderid1 = create_order(customerid)
        orderid2 = create_order(customerid)
        get_customer_orders(customerid, "After creating three orders")

        delete_order(orderid2 + 1, "Non existing order")
        delete_order(orderid2, "Existing order")
        get_customer_orders(customerid, "After deleting one of three")

        add_product(orderid2 + 1, 1, 1, "Non existing order")
        add_product(orderid1, 1, 0, "Non-positive quantity")
        add_product(orderid, int(products[0]['prod_id']), 1, "Success")
        add_product(
            orderid, int(
                products[1]['prod_id']), int(
                products[1]['stock']) + 1, "Success")
        add_product(orderid, int(products[2]['prod_id']), 2, "Success")

        get_order_details(orderid, "After adding two new products")
        add_product(
            orderid, int(
                products[0]['prod_id']), 2, "Same product as before")
        get_order_details(
            orderid, "After updating the quantity of one of them")

        remove_product(orderid2 + 1, 1, 1, "Non existing order")
        remove_product(orderid1, 1, 0, "Non-positive quantity")
        remove_product(orderid, int(products[2]['prod_id']), 1, "Success")
        get_order_details(
            orderid, "After updating the quantity of one of them")
        remove_product(
            orderid, int(
                products[2]['prod_id']), 2, "Remove more than possible")
        remove_product(orderid, int(products[2]['prod_id']), 1, "Success")
        get_order_details(orderid, "After fully removing one product")

        pay_order(orderid, "More quantity than stock")
        remove_product(
            orderid, int(
                products[1]['prod_id']), int(
                products[1]['stock']), "Success")
        pay_order(orderid, "Not enough balance")
        get_order_details(orderid, "Before paying order")
        add_balance(customerid, 1000000, "Enough balance to pay for the order")
        pay_order(orderid, "Enough stock and balance")
        get_order_details(orderid, "After paying order")

        delete_customer(customerid, "Finishing test")
        get_order_details(
            orderid, "Non-existing order after deletion of customer")
    except Exception as e:
        print(str(e))
        print(
            "Something went wrong with the test. Make sure both servers are "
            "running, do not forget to empty Docker Volumes and try again.")
