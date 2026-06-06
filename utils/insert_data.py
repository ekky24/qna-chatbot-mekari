import pandas as pd
# pyrefly: ignore [missing-import]
import mysql.connector
import math

def insert_data():
    csv_path = "./dataset/fraudTrain.csv"
    host = "localhost"
    user = "root"
    password = "P@ssw0rd"
    database = "qna_chatbot"
    port = 3306

    print(f"Reading first 10,000 rows from {csv_path}...")
    # Read the first 10,000 rows
    df = pd.read_csv(csv_path, nrows=10000)
    
    # Rename the first unnamed column to 'id'
    df.rename(columns={df.columns[0]: 'id'}, inplace=True)
    
    # Convert nan values to None (so they get inserted as NULL in SQL)
    df = df.where(pd.notnull(df), None)

    print(f"Connecting to MySQL database '{database}'...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    cursor = conn.cursor()

    # Define the insert query with backticks for `long` since it's a MySQL reserved word
    insert_query = """
    INSERT INTO transactions (
        id, trans_date_trans_time, cc_num, merchant, category, amt, 
        first, last, gender, street, city, state, zip, lat, `long`, 
        city_pop, job, dob, trans_num, unix_time, merch_lat, merch_long, is_fraud
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        trans_date_trans_time=VALUES(trans_date_trans_time),
        cc_num=VALUES(cc_num),
        merchant=VALUES(merchant),
        category=VALUES(category),
        amt=VALUES(amt),
        first=VALUES(first),
        last=VALUES(last),
        gender=VALUES(gender),
        street=VALUES(street),
        city=VALUES(city),
        state=VALUES(state),
        zip=VALUES(zip),
        lat=VALUES(lat),
        `long`=VALUES(`long`),
        city_pop=VALUES(city_pop),
        job=VALUES(job),
        dob=VALUES(dob),
        trans_num=VALUES(trans_num),
        unix_time=VALUES(unix_time),
        merch_lat=VALUES(merch_lat),
        merch_long=VALUES(merch_long),
        is_fraud=VALUES(is_fraud)
    """

    # Prepare data for insertion
    data_list = []
    for _, row in df.iterrows():
        # Make sure values are matching standard Python types (e.g. int, float, str, None)
        record = (
            int(row['id']),
            str(row['trans_date_trans_time']),
            str(row['cc_num']),
            str(row['merchant']),
            str(row['category']),
            float(row['amt']),
            str(row['first']),
            str(row['last']),
            str(row['gender']),
            str(row['street']),
            str(row['city']),
            str(row['state']),
            str(row['zip']),
            float(row['lat']),
            float(row['long']),
            int(row['city_pop']),
            str(row['job']),
            str(row['dob']),
            str(row['trans_num']),
            int(row['unix_time']),
            float(row['merch_lat']),
            float(row['merch_long']),
            int(row['is_fraud'])
        )
        data_list.append(record)

    # Insert in chunks of 1000
    chunk_size = 1000
    total_inserted = 0
    print("Inserting rows in chunks...")
    for i in range(0, len(data_list), chunk_size):
        chunk = data_list[i:i + chunk_size]
        cursor.executemany(insert_query, chunk)
        conn.commit()
        total_inserted += len(chunk)
        print(f"Inserted {total_inserted}/10000 rows...")

    cursor.close()
    conn.close()
    print("Done inserting data! Database connection closed.")

if __name__ == "__main__":
    insert_data()
