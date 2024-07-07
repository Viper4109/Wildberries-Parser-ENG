import requests
import time
import csv
from googletrans import Translator
from models import Items

link1 = r'Scripts\Python space\\' #Specify the path to the folder where you want to save the output file "WB_data.csv", if you leave the brackets empty, the default path will be used. (in the same place where the script is located)
# path example: r'scripts\Python space\\' there should be two slashes at the end.
page = 20 # just specify the number on the page where you want the script to stop working. 
# If the value is None or 0, the script will run indefinitely until you disable it manually or run out of input values.

class parseWB:

    def parse(self):
        num = 1
        self.__create_csv()
        while True:
            params = {
                'ab_comp_blend_by_prob_v2_2': '1',
                'ab_testid': 'pk0',
                'appType': '1',
                'curr': 'rub',
                'dest': '-1257786',
                'page': num,
                'query': '0',
                'resultset': 'catalog',
                'spp': '30',
                'suppressSpellcheck': 'false',
            }

            response = requests.get('https://recom.wb.ru/personal/ru/common/v5/search', params=params)

            items_info = Items.parse_obj(response.json()['data'])
            
            result = self.name_translation(num,items_info)
            if result == "Empty":
                break
            
            print(f'[+] The {num} page has been saved.')
            
            if type(page) == int and page is not None and page > 0:
                if num == page:
                    break
                
            num += 1
            
    def name_translation(self, num, items):
        current_string1 = ""
        current_string2 = ""
       
        for i,product in enumerate(items.products):
            if i <= 50:
                if current_string1:
                    current_string1 += fr" ( {product.name} )"
                else:
                    current_string1 = f"( {product.name} )"
            else:
                if current_string2:
                    current_string2 += fr" ( {product.name} )"
                else:
                    current_string2 = f"( {product.name} )"

        result1 = self.translate(current_string1)
        if result1 == 'Empty':
            return 'Empty'
        time.sleep(3.5)
        result2 = self.translate(current_string2)
        if result2 == 'Empty':
            return 'Empty'
        
        combined_result = rf'{result1} {result2}'
        
        s = combined_result.strip('()')
        names = [name.strip() for name in s.split(') (')]
            
        for i,product in enumerate(items.products):
            try:
                product.name = names[i]
                # print(product.name)
            except Exception as ex:
                pass
            
        self.__save_csv(num, items)
        
    def translate(self, text, max_retries=5, max_retries2=5, delay=3.5):
            translator = Translator()
            retries = 0
            retries2 = 0
            
            while retries < max_retries and retries2 <= max_retries2:
                try:
                    result = translator.translate(str(text), src='ru', dest='en')
                    return result.text
                except Exception as e:
                    if str(e) == "'NoneType' object is not iterable":
                        retries2 += 1
                        if retries2 <= max_retries2:
                            print(f"An empty value was received, retrying... ({retries2}/{max_retries2})")
                            time.sleep(0.5)
                            continue
                        else:
                            print('The values are over.')
                            return 'Empty'
                    else:
                        print(f"An error occurred: {e}")
                        retries += 1
                        if retries < max_retries:
                            print(f"Retrying... ({retries}/{max_retries})")
                            time.sleep(delay)
                        else:
                            print("Max retries reached. Translation failed.")
                            return None
        
    def __create_csv(self):
        with open(f'{link1}WB_data.csv', mode='w', newline="") as file:
            writer = csv.writer(file)
            writer.writerow(['№', 'Id', 'Name', 'Brand', 'Price(current)', 'Price(old)', 'Rating', 'In stock'])
                
    def __save_csv(self, num, items):
        with open(f'{link1}WB_data.csv', mode='a', newline="", encoding='UTF-8') as file:
            num -= 1
            writer = csv.writer(file)
            for product in items.products:
                writer.writerow([product.number + (num * 100),
                                product.id, 
                                product.name, 
                                product.brand, 
                                product.product_price, 
                                product.basic_price, 
                                product.reviewRating, 
                                product.volume])

        
if __name__ == "__main__":
    parser = parseWB()
    parser.parse() 