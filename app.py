from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from sqlalchemy import create_engine
import os
import time
from datetime import datetime
import pandas as pd
from decouple import config
from dotenv import load_dotenv
load_dotenv()
BOURSEDIRECT_USERNAME = config('BOURSEDIRECT_USERNAME')
BOURSEDIRECT_PASSWORD = config('BOURSEDIRECT_PASSWORD')
print('waiting to setup')
time.sleep(5)
connection_string = "mysql+mysqlconnector://user:password@mysql/testdb"

# Create a SQLAlchemy engine
engine = create_engine(connection_string)

class Scrapper:
    def __init__(self, email, pw):
        self.email = email
        self.pw = pw
        self.logged=False
        options = Options()
        options.add_argument("start-maximized")
        #options.add_argument("--headless")
        #options.add_argument('--no-sandbox')
        #options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        #self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver = webdriver.Remote(os.getenv('SELENIUM_REMOTE_URL'),options=options)
        #self.driver = webdriver.Chrome("http://selenium-hub:4444/wd/hub",options=options)
        #self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


    def login(self):
        self.driver.get("https://www.boursedirect.fr/fr/login")
        id=WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="bd_auth_login_type_login"]')))
        id.send_keys(self.email)
        pw = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="bd_auth_login_type_password"]')))
        pw.send_keys(self.pw)
        bouton = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="auth-login-form"]/form/div[3]/button')))
        bouton.click()
        time.sleep(2)
        print('log in')
        self.driver.get('https://www.boursedirect.fr/fr/page/portefeuille')
        print('load portefeuille')
        time.sleep(2)
        self.logged=True


    def scrap(self):
        if self.logged==False:
            self.login()
        else:
            self.driver.get('https://www.boursedirect.fr/fr/page/portefeuille')
        #switch to the iframe containing the data
        #//*[@id="legacy-iframe-327"]


        iframes = self.driver.find_elements(By.XPATH, '//iframe[@src="/priv/new/portefeuille-TR.php"]')[0]
        self.driver.switch_to.frame(iframes)
        print('switched to iframe')
        #
        t = self.driver.find_element(By.XPATH, '//*[@id="tabPTR"]/tbody[2]')
        elements = t.find_elements(By.TAG_NAME, 'tr')
        # Get the number of elements in the <tbody>
        total = self.driver.find_element(By.XPATH, '//*[@id="globalTableHolder"]/table/tbody/tr[3]/td[2]').text
        df=pd.DataFrame(columns=["Name","Quantité","PRU","Cours","Valo","+/-Val","var/PRU","var/Veille","%","Ordre Limite","Total","Currency","Time of Update"])
        date=datetime.now()
        pos_stock=[]
        #pos_limit_order is a list of where list where element is position of stock and second position of limit order
        pos_limit_order=[]
        for k in range(0,len(elements)):
            if elements[k].text!="":
                if "Lim" in elements[k].text:
                    if "Vente" in elements[k].text:
                        pos_limit_order.append([k-1,k,-1])
                    else:
                        pos_limit_order.append([k - 1, k, 1])
                else:
                    pos_stock.append(k)
        self.pos_stock=pos_stock
        self.lim=pos_limit_order

        for k in pos_stock:
            #get into stocks k+1/2
            l=elements[k].find_elements(By.TAG_NAME,'td')
            name,quantite,pru,cours,valo,val,varpru,varveille,pct=l[0].text,l[1].text,l[2].text,l[3].text,l[4].text,l[5].text,l[6].text,l[7].text,l[8].text
            df.loc[len(df)]=[name,quantite,pru,cours,valo,val,varpru,varveille,pct,0,total,"EUR",date]
        if len(pos_limit_order)>0:
            for k in range(0,len(pos_limit_order)):
                quantite,cours=elements[pos_limit_order[k][1]].find_elements(By.TAG_NAME,'td')[1].text,elements[pos_limit_order[k][1]].find_elements(By.TAG_NAME,'td')[3].text.split("-")[0]
                df.loc[len(df)] = [elements[pos_limit_order[k][0]].find_elements(By.TAG_NAME,'td')[0].text,quantite , "",cours , "", "", "", "", "", pos_limit_order[k][2],total,"EUR",date]

        #add cash
        valeur=self.driver.find_element(By.XPATH, '//*[@id="globalTableHolder"]/table/tbody/tr[4]/td[2]').text
        df.loc[len(df)]=["CASH",1,0,valeur,0,0,0,0,0,0,total,"EUR",date]


        print('data scraped')
        self.df = df.replace(["", " "], 0)
        #formattage data
        for k in ["PRU","Cours","Valo","+/-Val","Total"]:
            temp.df[k] = temp.df[k].apply(
            lambda a: float(a.replace(" ", "").replace(',', '.').replace('€', '')) if isinstance(a, str) else a)
        for k in ["var/PRU","var/Veille","%"]:
            temp.df[k] = temp.df[k].apply(
            lambda a: float(a.replace(" ", "").replace(',', '.').replace('%', ''))/100 if isinstance(a, str) else a)
        print('finished save')
        self.driver.switch_to.default_content()
        try:
            self.driver.find_element(By.XPATH, '//*[@id="user-dropdown"]/div').click()
            time.sleep(0.5)
            self.driver.find_element(By.XPATH, '//*[@class="btn btn-logout"][text()="Me déconnecter"]').click()
            self.logged=False
            print('unloged')
        except Exception as e:
            print(e)
            print("failed to unlog")




    def get_cookie(self):
        raise NotImplementedError()

    def close(self):
        self.driver.quit()


if __name__ == '__main__':
    while True:
        try:
            temp = Scrapper(email=BOURSEDIRECT_USERNAME, pw=BOURSEDIRECT_PASSWORD)
            print(f'scraping')
            temp.scrap()
            print(datetime.now())
            print(temp.df.head())
            # Assuming you've already defined your 'portfolio' table in SQLAlchemy
            # If not, you'll need to reflect it first or define it
            # save position
            a = temp.df[temp.df['Ordre Limite'] == 0][["Name", 'Quantité']].T
            a.columns = a.iloc[0, :]
            a = a.drop('Name')
            a.index = [temp.df['Time of Update'][0]]
            a.to_sql('portfolio', con=engine, if_exists='append', index=True)
            # save price
            price = temp.df[temp.df['Ordre Limite'] == 0][["Name", 'Cours']].T
            price.columns = price.loc['Name', :]
            price = price.drop('Name')
            price.index = [temp.df['Time of Update'][0]]
            price.loc[:, "Total_Pfo"] = temp.df['Total'][0]
            price.to_sql('portfolio_price', con=engine, if_exists='append', index=True)
            # is ordre limite
            ordre_limite = temp.df[temp.df['Ordre Limite'] != 0][["Name", 'Quantité']].T
            ordre_limite.columns = ordre_limite.loc['Name', :]
            ordre_limite = ordre_limite.drop('Name')
            ordre_limite.index = [temp.df['Time of Update'][0]]
            ordre_limite.to_sql('ordre_limite', con=engine, if_exists='append', index=True)
            # price ordre limite
            ordre_limite_price = temp.df[temp.df['Ordre Limite'] != 0][["Name", 'Cours', 'Ordre Limite']].T
            ordre_limite_price.columns = ordre_limite_price.loc['Name', :]
            ordre_limite_price.loc['Cours', :] = ordre_limite_price.loc['Cours', :] * ordre_limite_price.loc[
                                                                                      'Ordre Limite', :]
            ordre_limite_price = ordre_limite_price.drop(['Name', 'Ordre Limite'])
            ordre_limite_price.index = [temp.df['Time of Update'][0]]
            ordre_limite_price.to_sql('ordre_limite_price', con=engine, if_exists='append', index=True)
            print('waiting 5mins')
            temp.close()
            time.sleep(15*60)
        except Exception as e:
            try:
                temp.close()
            except Exception as e:
                print('couldnt close chrome')
            print(e)
            time.sleep(5)





