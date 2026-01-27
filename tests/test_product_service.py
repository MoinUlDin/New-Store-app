from services import product_service




def test_product_crud_and_search(test_db):
    data = {
    'short_code': 'COKE500',
    'ur_name': 'کوک کولا',
    'en_name': 'Coke 500ml',
    'company': 'CocaCola',
    'barcode': '1234567890123',
    'base_price': '40.5',
    'sell_price': '55.0',
    'stock_qty': '10',
    'reorder_threshold': '2',
    'unit': 'pcs'
    }
    pid = product_service.create_product(data)
    assert pid


    p = product_service.get_product(pid)
    assert p['en_name'] == 'Coke 500ml'
    assert p['stock_qty'] == 10


    product_service.update_product(pid, {'sell_price': '60.0'})
    p2 = product_service.get_product(pid)
    assert float(p2['sell_price']) == 60.0


    results = product_service.search_products('Coke')
    assert any(r['id'] == pid for r in results)


    product_service.delete_product(pid)
    assert product_service.get_product(pid) is None