import requests

# num1 publication number
num1 = '7430453'
# num2 is_number
num2 = '7434773'
# num3 is arnumber
num3 = '07434812'
def download_pdf(p_num,i_num,a_num):
    url = 'http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber='+str(a_num)
    url_length = 'https://ieeexplore.ieee.org/ielx5/4793680/4793681/04793743.pdf?tp=&arnumber=4793743&isnumber=4793681&ref='
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3',
        'Refer':'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber='+str(a_num)+'&tag=1',
        'DNT':'1'
    }
    response_length = requests.get(url_length,headers = headers,stream = True).headers.get('Content-Length')
    print(response_length)
download_pdf(num1,num2,num3)
