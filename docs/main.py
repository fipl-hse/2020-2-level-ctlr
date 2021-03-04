import requests

response = requests.get('http://www.sormovich.nnov.ru/archive/3443/')
if response:
    print(response.text)
else:
    print('Error')

with open('file.html', 'w') as f:
    f.write(response.text)



