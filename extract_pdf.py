from PyPDF2 import PdfFileReader
import re
import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def extract_pdf(path):
  pdf = PdfFileReader(path)

  data = {}
  order_detail = []

  for i in range(0, pdf.numPages):
    page = pdf.getPage(i)
    text = page.extractText()
    
    date = re.compile(r'^[0-9]+')
    send_name_lazada = re.compile(r'Penerima:')
    send_date_lazada = re.compile(r'\d{2}\s\w{3}\s\d{4}')
    references_id_lazada_jne = re.compile(r'JNAP-([0-9])')
    references_id_lazada_lex = re.compile(r'LXAD-([0-9])')
    references_id_lazada_ninja = re.compile(r'NLIDAP([0-9])')
    order_id_lazada = re.compile(r'Total Qty :')
    address1 = re.compile(r'Kab.')
    address2 = re.compile(r'Kota')
    order_detail_lazada = re.compile(r'Pengirim:')
    
    textSplit = text.split('\n')

    for index, line in enumerate(textSplit):
      if references_id_lazada_jne.match(line):
        data["references_id"] = line
        data["expedition"] = "JNE"
      if references_id_lazada_lex.match(line):
        data["references_id"] = line
        data["expedition"] = "Lazada Express"
      if references_id_lazada_ninja.match(line):
        data["references_id"] = line
        data["expedition"] = "Ninja"
      if send_name_lazada.match(line):
        clean = line.split("Diserahkan ke")
        clean2 = clean[0].split("Penerima:")
        data["send_name"] = clean2[1]
      if send_date_lazada.match(line):
        data["send_date"] = line
      if order_id_lazada.match(line):
        clean = line.split("Total Qty : ")
        data["order_id"] = clean[1]
      if address1.search(line) or address2.search(line):
        if not send_name_lazada.match(textSplit[index+1]):
          data["address"] = line+" "+textSplit[index+1]
      if order_detail_lazada.search(line):
        od = re.split('(\d+)', line)
        qty = od[1]
        clean_sku = od[2].split("Pengirim:")
        sku = clean_sku[0]

        url = os.getenv("API_URL") + "/product/sku/" + sku
        payload={}
        headers={}

        response = requests.request("GET", str(url), headers=headers, data=payload)
        response_data = response.json()

        product_id = response_data["data"]["id"]
        product_name = response_data["data"]["name"]
        product_price = response_data["data"]["price"]
        product_total_price = int(product_price) * int(qty)

        detail = {}
        detail["product_id"] = product_id
        detail["product_name"] = product_name
        detail["product_qty"] = int(qty)
        detail["product_sku"] = sku
        detail["product_price"] = product_price
        detail["product_total_price"] = product_total_price

        order_detail.append(detail)
    data["order_detail"] = order_detail
  return data

print(extract_pdf("resi/lazada_jne.pdf"))