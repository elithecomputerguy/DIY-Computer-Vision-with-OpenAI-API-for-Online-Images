from bottle import route, post, run, request
from openai import OpenAI
import sqlite3
import os

#OpenAI Settings
api_key ='APIKEY'
client = OpenAI(api_key=api_key)

#Class For Interacting with Database
#path() is used for using database in same folder as script
class database:
    def path():
        current_directory = os.path.dirname(os.path.abspath(__file__))
        db_name = 'image.db'
        file_path = os.path.join(current_directory, db_name)

        return file_path

    def db_create():
        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        create_table = '''
                        create table if not exists image(
                            id integer primary key,
                            image text,
                            query text,
                            image_response text
                        )
                        '''

        cursor.execute(create_table)
        conn.commit()
        conn.close()

    def db_select():
        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        sql = 'select * from image order by id desc'
        cursor.execute(sql)
        record = cursor.fetchall()
        conn.commit()
        conn.close()

        return record

    def db_insert(image, query, image_response):
        print(f'insert db {image} -- {image_response}')

        file_path = database.path()
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        sql = 'insert into image(image, query, image_response) values(?,?,?)'
        cursor.execute(sql,(image, query, image_response))
        conn.commit()
        conn.close()

#Get Values from OpenAI
def openai_get(client, image, query):
    response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": query},
            {
            "type": "image_url",
            "image_url": {
                "url": image,
            },
            },
        ],
        }
    ],
    max_tokens=300,
    )

    response = response.choices[0].message.content

    return response

#Index Page. Query form sends values back to this page
@route('/')
@post('/')
def index():
    image = request.forms.get('image')
    query = request.forms.get('query')

    image_embed=''
  
    if query != None:
        image_response = openai_get(client, image, query)
        image_embed =   f'''
                            <div style="width:200px;">
                                <img style="width:200px; height:auto;" src="{image}">
                                <br>
                                {image_response}
                            </div>
                        '''
        database.db_insert(image, query, image_response)

    record = database.db_select()

    form =  f'''
                <form action="./" method="post">
                Image Url: <input type="text" name="image" value="{image}">
                <br>
                Query: <input type="text" name="query" value="{query}">
                <br>
                <input type="submit">
                </form>
            '''

    image_previous=''
    for x in record:
        image_previous =f'''
                            {image_previous} 
                            <div style="width:200px;">
                                <img style="width:200px; height:auto;" src="{x[1]}">
                                <strong>{x[2]}</strong>
                                <br>
                                {x[3]}
                            </div>
                        '''
        
    page = f'''
                {form}
                <br> 
                <div style="display:flex;">
                    {image_embed}
                </div>
                <br>
                {image_previous}
            '''

    return page

database.db_create()

run(host='0.0.0.0', port=80, debug=True)