"""
Test verisi oluşturma script'i
Churn model eğitimi için örnek müşteri verileri
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
import logging

from database import SessionLocal
from models import Customer, Tenant, User

logger = logging.getLogger(__name__)

def create_test_tenant_and_user():
    """Test tenant ve user oluştur"""
    db = SessionLocal()
    try:
        # Test tenant oluştur
        tenant = db.query(Tenant).filter(Tenant.name == "Test Company").first()
        if not tenant:
            tenant = Tenant(
                name="Test Company",
                domain="test",
                is_active=True
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"✅ Test tenant oluşturuldu: {tenant.id}")
        
        # Test user oluştur (basit hash ile)
        user = db.query(User).filter(User.email == "test@test.com").first()
        if not user:
            # Basit hash (bcrypt problemi nedeniyle)
            user = User(
                email="test@test.com",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret" şifresinin hash'i
                full_name="Test User",
                tenant_id=tenant.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Test user oluşturuldu: {user.id}")
        
        return tenant.id, user.id
        
    except Exception as e:
        logger.error(f"Tenant/User oluşturma hatası: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def generate_test_customers(tenant_id: int, count: int = 100):
    """Test müşteri verileri oluştur"""
    db = SessionLocal()
    try:
        # Mevcut müşterileri sil
        db.query(Customer).filter(Customer.tenant_id == tenant_id).delete()
        db.commit()
        
        # Random seed
        np.random.seed(42)
        random.seed(42)
        
        customers = []
        
        # Demografik veriler
        genders = ['Male', 'Female', 'Other']
        segments = ['Basic', 'Premium', 'Enterprise', 'Free']
        
        for i in range(count):
            # Base features
            age = random.randint(18, 65)
            gender = random.choice(genders)
            segment = random.choice(segments)
            
            # Subscription length (days)
            subscription_length = random.randint(30, 365*3)  # 1 ay - 3 yıl
            
            # Last login (some customers haven't logged in recently - churn risk)
            days_since_login = random.randint(1, 180)
            last_login_date = datetime.now() - timedelta(days=days_since_login)
            
            # Purchase behavior
            total_orders = random.randint(0, 50)
            avg_order_value = random.uniform(10, 500)
            total_spent = total_orders * avg_order_value
            
            # Churn logic (business rules)
            churn_risk_factors = 0
            
            # High churn risk factors
            if days_since_login > 90:  # Haven't logged in for 3+ months
                churn_risk_factors += 2
            if total_orders < 3:  # Very few orders
                churn_risk_factors += 2
            if segment == 'Free':  # Free users more likely to churn
                churn_risk_factors += 1
            if subscription_length > 365 and total_orders < 10:  # Long subscription but low activity
                churn_risk_factors += 1
            
            # Determine churn based on risk factors
            churn_probability = min(churn_risk_factors / 6.0, 0.8)  # Max 80% churn probability
            churned = 1 if random.random() < churn_probability else 0
            
            customer = Customer(
                customer_id=f"TEST_{i+1:03d}",
                age=age,
                gender=gender,
                segment=segment,
                subscription_length=subscription_length,
                last_login_date=last_login_date,
                total_orders=total_orders,
                total_spent=round(total_spent, 2),
                avg_order_value=round(avg_order_value, 2),
                churned=churned,
                tenant_id=tenant_id
            )
            
            customers.append(customer)
        
        # Batch insert
        db.add_all(customers)
        db.commit()
        
        # Statistics
        churned_count = sum(1 for c in customers if c.churned == 1)
        churn_rate = (churned_count / count) * 100
        
        print(f"✅ {count} test müşteri oluşturuldu")
        print(f"📊 Churn oranı: {churn_rate:.1f}% ({churned_count}/{count})")
        
        # Segment bazlı churn oranları
        for segment in segments:
            segment_customers = [c for c in customers if c.segment == segment]
            segment_churned = sum(1 for c in segment_customers if c.churned == 1)
            segment_rate = (segment_churned / len(segment_customers)) * 100 if segment_customers else 0
            print(f"   {segment}: {segment_rate:.1f}% churn ({segment_churned}/{len(segment_customers)})")
        
        return len(customers)
        
    except Exception as e:
        logger.error(f"Test verisi oluşturma hatası: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_csv():
    """Test verisini CSV olarak da kaydet"""
    db = SessionLocal()
    try:
        customers = db.query(Customer).filter(Customer.tenant_id == 1).all()
        
        data = []
        for customer in customers:
            data.append({
                'customer_id': customer.customer_id,
                'age': customer.age,
                'gender': customer.gender,
                'segment': customer.segment,
                'subscription_length': customer.subscription_length,
                'last_login_date': customer.last_login_date.strftime('%Y-%m-%d') if customer.last_login_date else None,
                'total_orders': customer.total_orders,
                'total_spent': customer.total_spent,
                'avg_order_value': customer.avg_order_value,
                'churned': customer.churned
            })
        
        df = pd.DataFrame(data)
        df.to_csv('./test_churn_data.csv', index=False)
        print(f"✅ Test verisi CSV olarak kaydedildi: test_churn_data.csv")
        
    except Exception as e:
        logger.error(f"CSV kaydetme hatası: {e}")
    finally:
        db.close()

def main():
    """Ana fonksiyon"""
    print("🧪 Test verisi oluşturuluyor...")
    
    try:
        # 1. Tenant ve User oluştur
        tenant_id, user_id = create_test_tenant_and_user()
        
        # 2. Test müşteri verileri oluştur
        customer_count = generate_test_customers(tenant_id, count=150)
        
        # 3. CSV olarak kaydet
        create_sample_csv()
        
        print(f"\n🎉 Test verisi başarıyla oluşturuldu!")
        print(f"📋 Tenant ID: {tenant_id}")
        print(f"👤 User ID: {user_id}")
        print(f"👥 Müşteri sayısı: {customer_count}")
        print(f"\n🚀 Şimdi model eğitimi test edebilirsiniz:")
        print(f"   python train.py {tenant_id}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()
