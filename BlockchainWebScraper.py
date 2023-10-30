from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

def create_path(visited, v): ##helper function to create path from visited dict
    path = [v]
    while path[-1] != 0:
        path.append(visited[path[-1]])
    path.reverse()
    return path

def blockchain_scraper():
    driver = webdriver.Firefox()
    driver.get("INSERT STARTING BLOCKCHAIN.COM TRANSACTION URL HERE")
    coinbase = "//div[contains(text(), 'Coinbase')]/ancestor::div[@span]//div"
    button_xpath = "//div[contains(text(), 'From')]/following-sibling::div//a[starts-with(@href, '/explorer/transactions')]//div[@src]" #Xpath variables

    q = []
    visited = {}
    current_path = []
    current_shortest = []

    q.append("79ec6ef52c0a2468787a5f671f666cf122f68aaed11a28b15b5da55c851aee75")
    visited["79ec6ef52c0a2468787a5f671f666cf122f68aaed11a28b15b5da55c851aee75"] = 0 #visited key is hash id, and the value is the previous page hash id

    while len(q) > 0:
        v = q.pop(0)
        current_path = create_path(visited, v)
        if len(current_path) > len(current_shortest) and len(current_shortest) != 0: #check if current path is less than current shortest path to coinbase
            break
        test = WebDriverWait(driver, 300).until( #check if current page is coinbase
            EC.presence_of_all_elements_located((By.XPATH, coinbase))
        )
        for item in test: #Had to iterate over this because an XPath looking specifically for Yes yielded no results
            if item.text.strip() == 'Yes': 
                current_path = create_path(visited, v)
                if len(current_path) < len(current_shortest) or len(current_shortest) == 0:
                    current_shortest = current_path[1:]
                    print(current_shortest)
                break


        driver.get("https://www.blockchain.com/explorer/transactions/btc/" + v)

        elements = WebDriverWait(driver, 300).until(
            EC.presence_of_all_elements_located((By.XPATH, button_xpath))
        )
        for i in range(len(elements)): #iterate over each link leading to an input transaction
            element = WebDriverWait(driver, 300).until(EC.presence_of_all_elements_located((By.XPATH, button_xpath)))[i]

            hash_id = element.find_element(By.XPATH, "ancestor::a").get_attribute("href").split('/')[-1]

            element.click()
            WebDriverWait(driver, 300).until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(text(), 'Hash ID')]/following-sibling::div//span[contains(text(), '" + hash_id + "')]")))

            if hash_id not in visited: #check if current page has been visited
                visited[hash_id] = v
                q.append(hash_id)
            
            test = WebDriverWait(driver, 300).until(
                EC.presence_of_all_elements_located((By.XPATH, coinbase))
            ) ##check if current page is coinbase
            time.sleep(0.5)
            for item in test:
                if item.text.strip() == 'Yes':
                    current_path = create_path(visited, hash_id)
                    if len(current_path) < len(current_shortest) or len(current_shortest) == 0:
                        current_shortest = current_path[1:]
                        print(current_shortest)
                    
                    q.pop()
                    break
            driver.back()
    
    return current_shortest

shortest_path = blockchain_scraper()
print("Shortest path: " + str(shortest_path))
print("Length of shortest path: " + str(len(shortest_path)))
        
        