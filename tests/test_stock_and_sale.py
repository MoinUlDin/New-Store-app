from decimal import Decimal
from services import product_service, stock_service, sale_service




def test_stock_movements_and_sale(test_db):
    data = {
    'short_code': 'PEP500',
    'ur_name': 'پیپسی',
    'en_name': 'Pepsi 500ml',
    'company': 'PepsiCo',
    'barcode': '9999999999999',
    'base_price': '30.0',
    'sell_price': '45.0',
    'stock_qty': '5',
    'reorder_threshold': '1',
    'unit': 'pcs'
    }
    pid = product_service.create_product(data)


    # receive 10 packs (supply_pack_qty default 1 -> adds 10)
    stock_service.receive_packs(pid, 10, cost_total=Decimal('300.0'))
    p = product_service.get_product(pid)
    assert int(p['stock_qty']) == 15 # 5 initial + 10


    # create a sale for 3 units
    items = [{
    'product_id': pid,
    'qty': Decimal('3'),
    'price_per_unit': Decimal('45.0'),
    'base_price_per_unit': Decimal('30.0'),
    'line_discount': Decimal('0')
    }]


    sale_id = sale_service.create_sale(created_by=None, items=items, payment_method='cash')
    assert sale_id


    p2 = product_service.get_product(pid)
    assert int(p2['stock_qty']) == 12 # 15 - 3