from decimal import Decimal
from algorithms import merge_sort, binary_search, dijkstra, priority_alerts, fefo_batches
from analytics import money

def test_merge_sort_and_binary_search():
    rows=[{"sku":"B"},{"sku":"A"},{"sku":"C"}]
    ordered=merge_sort(rows,key=lambda x:x['sku'])
    assert [x['sku'] for x in ordered]==['A','B','C']
    assert binary_search(ordered,'B',key=lambda x:x['sku'])['sku']=='B'
    assert binary_search(ordered,'Z',key=lambda x:x['sku']) is None

def test_dijkstra_rejects_negative_edges():
    try: dijkstra({'A':[('B',-1)],'B':[]},'A')
    except ValueError: assert True
    else: assert False

def test_priority_and_fefo():
    ranked=priority_alerts([{'sku':'WATCH','status':'watch','suggested_qty':50},{'sku':'CRIT','status':'critical','suggested_qty':2}])
    assert ranked[0]['sku']=='CRIT'
    selected,left=fefo_batches([{'id':1,'expiry_date':'2026-12-01','quantity':5},{'id':2,'expiry_date':'2026-11-01','quantity':4}],6)
    assert selected==[{'batch_id':2,'quantity':4},{'batch_id':1,'quantity':2}] and left==0

def test_decimal_money():
    assert money(Decimal('10.005'))==Decimal('10.01')
