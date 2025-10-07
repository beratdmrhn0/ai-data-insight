import pytest
import tempfile
import os
import pandas as pd
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """FastAPI test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_csv_small():
    """Küçük CSV fixture (5-10 satırlık) - hızlı test için"""
    content = """sku,quantity,price,customer_id,order_date
A,10,100.0,C1,2023-01-01
B,20,200.0,C2,2023-01-02
C,30,300.0,C3,2023-01-03
D,40,400.0,C4,2023-01-04
E,50,500.0,C5,2023-01-05"""
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)


@pytest.fixture
def sample_csv_with_missing():
    """Eksik değerler içeren CSV fixture"""
    content = """sku,quantity,price,customer_id,order_date
A,10,100.0,C1,2023-01-01
B,,200.0,C2,2023-01-02
C,30,,C3,2023-01-03
D,40,400.0,,2023-01-04
E,50,500.0,C5,"""
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)


@pytest.fixture
def sample_csv_anomaly():
    """Anomali içeren CSV fixture"""
    content = """sku,quantity,price,customer_id,order_date
A,10,100.0,C1,2023-01-01
B,20,200.0,C2,2023-01-02
C,30,300.0,C3,2023-01-03
D,40,400.0,C4,2023-01-04
E,50,500.0,C5,2023-01-05
F,1000,10000.0,C6,2023-01-06"""
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)


@pytest.fixture
def sample_dataframe():
    """Pandas DataFrame fixture"""
    data = {
        'sku': ['A', 'B', 'C', 'D', 'E'],
        'quantity': [10, 20, 30, 40, 50],
        'price': [100.0, 200.0, 300.0, 400.0, 500.0],
        'customer_id': ['C1', 'C2', 'C3', 'C4', 'C5'],
        'order_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
    }
    df = pd.DataFrame(data)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df


@pytest.fixture
def empty_dataframe():
    """Boş DataFrame fixture"""
    return pd.DataFrame()


@pytest.fixture
def single_row_dataframe():
    """Tek satırlık DataFrame fixture"""
    data = {
        'sku': ['A'],
        'quantity': [10],
        'price': [100.0],
        'order_date': ['2023-01-01']
    }
    df = pd.DataFrame(data)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df
