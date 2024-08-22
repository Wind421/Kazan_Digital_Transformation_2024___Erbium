import psycopg2

def create_conn():
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='postgres',
        host='localhost',
        port=5432
    )
    return conn

def post_user(user_id, first_name, last_name,phone=None):
    conn = create_conn()
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO "User" (user_id, first_name, last_name, region, phone) 
    VALUES (%s, %s, %s, 'Все районы', %s)
    ON CONFLICT (user_id) DO NOTHING;
    """
    
    cursor.execute(insert_query, (user_id, first_name, last_name,phone))
    conn.commit()
    cursor.close()
    conn.close()

def post_idea(user_id, title, text, address,photo_prev=None):
    conn = create_conn()
    cursor = conn.cursor()

    if photo_prev == 'нет': 
        photo_prev=None

    insert_query = f"""
    INSERT INTO "Idea" (user_id, title, text, adress, date, status, good_reactes, pass_reactes, bad_reactes, photo_prev,photo_consept,photo_released,region,master,contact) 
    VALUES (%s, %s, %s, %s, NOW(), 'in processing', 0, 0, 0, %s,'C://Users//Dasha//Pictures//default.jpg','C://Users//Dasha//Pictures//default.jpg','Все районы','нет','нет')
    """
    
    cursor.execute(insert_query, (user_id, title, text, address, photo_prev))
    conn.commit()
    cursor.close()
    conn.close()

def get_votes(idea_id=None):
    conn = create_conn()
    cursor = conn.cursor()

    query = """
    SELECT good_reactes,bad_reactes,pass_reactes
    FROM "Idea"
    WHERE idea_id = %s;
    """
    cursor.execute(query, (idea_id,))
    result = cursor.fetchone()    
    cursor.close()
    conn.close()
    return {
        "good_reactes": result[0],
        "bad_reactes": result[1],
        "pass_reactes": result[2],
    }  

def get_profile(user_id):
    conn = create_conn()
    cursor = conn.cursor()
    query = f"""
        SELECT first_name,last_name,region,phone
        FROM "User"
        WHERE user_id=%s
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "first_name": result[0],
        "last_name": result[1],
        "region": result[2],
        "phone": result[3],
    }  

def get_region(user_id):
    conn = create_conn()
    cursor = conn.cursor()

    query = """
    SELECT region
    FROM "User"
    WHERE user_id = %s;
    """
    cursor.execute(query, (user_id,))
    region = cursor.fetchone()
    cursor.close()
    conn.close()
    return {"region": region[0]}

def get_idea(user_id,idea_id):
    conn = create_conn()
    cursor = conn.cursor()

    query = """
        SELECT u.first_name, i.title, i.text, i.adress,i.photo_prev
        FROM "User" AS u, "Idea" AS i
        WHERE u.user_id = %s AND i.idea_id = %s
        LIMIT 1;
    """
    cursor.execute(query, (user_id,idea_id))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
            "first_name": result[0],
            "title": result[1],
            "text": result[2],
            "adress": result[3],
            "photo_prev": result[4],
            "idea_id": idea_id
    }

def get_firstname(idea_id):
    conn = create_conn()
    cursor = conn.cursor()
    query = """
    SELECT i.user_id
    FROM "Idea" as i
    WHERE i.idea_id=%s
    """
    cursor.execute(query,(idea_id,))
    user_id = cursor.fetchone()

    query2 = f"""
    SELECT u.first_name
    FROM "User" as u
    WHERE u.user_id=%s
    """
    cursor.execute(query2,(user_id[0],))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return {'first_name':result[0]}

def set_user(user_id,phone):
    conn = create_conn()
    cursor = conn.cursor()
    query = f"""
    UPDATE "User"
    SET phone = %s
    WHERE user_id = %s;
    """
    cursor.execute(query, (phone,user_id))
    conn.commit()
    cursor.close()
    conn.close()

def set_votes(choice,idea_id):
    conn = create_conn()
    cursor = conn.cursor()
    query = f"""
    UPDATE "Idea"
    SET {choice} = {choice} + 1
    WHERE idea_id = %s;
    """
    cursor.execute(query, (idea_id,))
    conn.commit()
    cursor.close()
    conn.close()

def set_region(user_id, region):
    conn = create_conn()
    cursor = conn.cursor()
    sql_query = 'UPDATE "User" SET region = %s WHERE user_id = %s;'
    cursor.execute(sql_query, (region, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def set_title(idea_id,title):
    conn = create_conn()
    cursor = conn.cursor()
    query = f"""
    UPDATE "Idea"
    SET title = %s
    WHERE idea_id = %s;
    """
    cursor.execute(query, (title, idea_id))
    conn.commit()
    cursor.close()
    conn.close()

def set_text(idea_id,text):
    conn = create_conn()
    cursor = conn.cursor()
    query = f"""
    UPDATE "Idea"
    SET text = %s
    WHERE idea_id = %s;
    """
    cursor.execute(query, (text, idea_id))
    conn.commit()
    cursor.close()
    conn.close()

def set_adress(idea_id,adress):
    conn = create_conn()
    cursor = conn.cursor()
    query = f"""
    UPDATE "Idea"
    SET adress = %s
    WHERE idea_id = %s;
    """
    cursor.execute(query, (adress, idea_id))
    conn.commit()
    cursor.close()
    conn.close()

def set_photo(idea_id,photo_path):
    conn = create_conn()
    cursor = conn.cursor()
    query = f"""
    UPDATE "Idea"
    SET photo_prev = %s
    WHERE idea_id = %s;
    """
    cursor.execute(query, (photo_path, idea_id))
    conn.commit()
    cursor.close()
    conn.close()

def del_idea(idea_id):
    conn = create_conn()
    cursor = conn.cursor()
    query = """
    DELETE FROM "Idea"
    WHERE idea_id = %s
    """
    cursor.execute(query, (idea_id,))
    conn.commit()
    cursor.close()
    conn.close()

def last_idea(user_id):
    conn = create_conn()
    cursor = conn.cursor()

    max_idea_id_query = """
    SELECT MAX(idea_id) FROM "Idea" WHERE user_id = %s;
    """
    cursor.execute(max_idea_id_query, (user_id,))
    max_idea_id_result = cursor.fetchone()
    max_idea_id = max_idea_id_result[0] if max_idea_id_result else None
    
    if max_idea_id:
        
        main_query = """
        SELECT u.first_name, i.title, i.text, i.adress,i.photo_prev
        FROM "User" AS u, "Idea" AS i
        WHERE u.user_id = %s AND i.idea_id = %s
        LIMIT 1;
        """
        cursor.execute(main_query, (user_id, max_idea_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {
            "first_name": result[0],
            "title": result[1],
            "text": result[2],
            "adress": result[3],
            "photo_prev": result[4],
            "idea_id": max_idea_id
        }
    else:
        cursor.close()
        conn.close()
        return None

def cur_idea(offset=0, region='Все районы', status='approved'):
    conn = create_conn()
    cursor = conn.cursor()
    
    if status == 'approved':
        status = "('approved')"
        photo_column = 'photo_prev'
    elif status == 'released':
        status = "('released','consept')"
        photo_column = """
        CASE 
            WHEN i.status = 'released' THEN i.photo_released 
            WHEN i.status = 'consept' THEN i.photo_consept 
        END
        """

    if region == 'Все районы':
        query = f"""
        SELECT i.idea_id, i.title, i.text, i.adress, i.status, {photo_column}, i.master, i.contact
        FROM "Idea" AS i
        WHERE i.status in {status}
        ORDER BY i.date DESC 
        LIMIT 1 
        OFFSET %s;
        """
        cursor.execute(query, (offset,))
    else:
        query = f"""
        SELECT i.idea_id, i.title, i.text, i.adress, i.status, {photo_column}, i.master, i.contact
        FROM "Idea" AS i
        WHERE i.status in {status} AND i.region = %s
        ORDER BY i.date DESC 
        LIMIT 1 
        OFFSET %s;
        """
        cursor.execute(query, (region, offset))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return {
                "idea_id": result[0],
                "title": result[1],
                "text": result[2],
                "adress": result[3],
                "status":result[4],
                "photo":result[5],
                "master": result[6],
                "contact": result[7]
            }
    else:
        return None

def cur_my_idea(offset=0,region='Все районы'):
    conn = create_conn()
    cursor = conn.cursor()

    photo_column = """
        CASE 
            WHEN i.status = 'in processing' THEN i.photo_prev
            WHEN i.status = 'approved' THEN i.photo_prev
            WHEN i.status = 'released' THEN i.photo_released 
            WHEN i.status = 'consept' THEN i.photo_consept 
        END
    """

    if region == 'Все районы':
        query = f"""
        SELECT i.title, i.text, i.adress, i.status, {photo_column}, i.master, i.contact, i.good_reactes, i.bad_reactes, i.pass_reactes,i.idea_id
        FROM "Idea" AS i
        ORDER BY i.date DESC 
        LIMIT 1 
        OFFSET %s;
        """
        cursor.execute(query, (offset,))
    else:
        query = f"""
        SELECT i.title, i.text, i.adress, i.status, {photo_column}, i.master, i.contact, i.good_reactes, i.bad_reactes, i.pass_reactes,i.idea_id
        FROM "Idea" AS i
        WHERE i.region = %s
        ORDER BY i.date DESC 
        LIMIT 1 
        OFFSET %s;
        """
        cursor.execute(query, (region,offset))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return {
                "title": result[0],
                "text": result[1],
                "adress": result[2],
                "status":result[3],
                "photo":result[4],
                "master": result[5],
                "contact": result[6],
                "good_reactes": result[7],
                "bad_reactes": result[8],
                "pass_reactes": result[9],
                "idea_id": result[10]
            }
    else:
        return None
