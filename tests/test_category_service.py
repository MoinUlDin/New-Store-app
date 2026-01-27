from services import category_service




def test_category_crud(test_db):
    cid = category_service.create_category('Beverages')
    assert cid
    cat = category_service.get_category(cid)
    assert cat['name'] == 'Beverages'


    category_service.update_category(cid, 'Drinks')
    cat2 = category_service.get_category(cid)
    assert cat2['name'] == 'Drinks'


    category_service.delete_category(cid)
    assert category_service.get_category(cid) is None