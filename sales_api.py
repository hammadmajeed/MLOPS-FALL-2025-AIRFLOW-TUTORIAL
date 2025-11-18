from flask import Flask, jsonify, request
from datetime import datetime
import random

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/sales')
def sales():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    # Simulate 10 sales records for the day
    products = [
        {'product_id': 1, 'category': 'Electronics'},
        {'product_id': 2, 'category': 'Books'},
        {'product_id': 3, 'category': 'Clothing'},
        {'product_id': 4, 'category': 'Home'},
        {'product_id': 5, 'category': 'Sports'},
    ]
    sales_data = []
    for _ in range(10):
        prod = random.choice(products)
        quantity = random.randint(1, 5)
        price = round(random.uniform(10, 200), 2)
        sales_data.append({
            'date': date,
            'product_id': prod['product_id'],
            'category': prod['category'],
            'quantity': quantity,
            'total_price': round(quantity * price, 2)
        })
    return jsonify(sales_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
