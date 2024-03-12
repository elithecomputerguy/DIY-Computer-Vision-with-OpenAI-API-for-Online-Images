from bottle import route, post, run, request
from openai import OpenAI

#OpenAI Settings
api_key ='APIKEY'
client = OpenAI(api_key=api_key)

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
        
    form =  f'''
                <form action="./" method="post">
                Image Url: <input type="text" name="image" value="{image}">
                <br>
                Query: <input type="text" name="query" value="{query}">
                <br>
                <input type="submit">
                </form>
            '''

    page = f'''
                {form}
                <br> 
                <div style="display:flex;">
                    {image_embed}
                </div>
            '''

    return page

run(host='0.0.0.0', port=80, debug=True)