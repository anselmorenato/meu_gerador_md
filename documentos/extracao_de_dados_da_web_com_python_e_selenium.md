---
titulo: "Título do seu Artigo"
autor: "Seu Nome"
data: "05 de Julho de 2026"
resumo: "Um breve resumo ou introdução contendo o objetivo do artigo."
tags: "markdown", "template", "conteúdo"
---
# Extração de dados da WEB com Python e Selenium

Neste curso, você vai aprender sobre extração de dados da web utilizando Python e Selenium, além de como salvar esses dados em um banco de dados com o sqlAlchemy. O foco é em web scraping, e o curso é voltado para todas as pessoas interessadas nesse tema. O curso também apresenta a instalação de todos os programas necessários.


# Seção 1: Introdução 


## 1. Introdução



## 2. Instalações



### instalacao vscode 

### instalacao Python

### extensao python e python para vscode

```bash
pip install selenium
```

### 3. Atualizando para Selenium 4 e mudanças no script

**Arquivos da aula:**
[`mudancas.py`]


**codigo:** `mudancas.py`

```python
#Instalacoes
#pip3 install selenium==4.0.0
#pip3 install webdriver_manager
#pip3 install webdriver-manager

#https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.by.html
#https://www.selenium.dev/selenium/docs/api/py/_modules/selenium/webdriver/common/by.html#By
#https://pypi.org/project/webdriver-manager/

from selenium import webdriver
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions, Chrome

#Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



#Firefox
#from selenium.webdriver.firefox.service import Service as FirefoxService
#from webdriver_manager.firefox import GeckoDriverManager
#driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

#Edge
#from selenium.webdriver.edge.service import Service as EdgeService
#from webdriver_manager.microsoft import EdgeChromiumDriverManager
#driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

#IE
#from selenium.webdriver.ie.service import Service as IEService
#from webdriver_manager.microsoft import IEDriverManager
#driver = webdriver.Ie(service=IEService(IEDriverManager().install()))


opts = ChromeOptions()
#esta opcao serve para nao fechar o navegador apos a execucao do script
opts.add_experimental_option("detach", True)
servico=Service(ChromeDriverManager().install())
driver=webdriver.Chrome(service=servico, options=opts)

driver.get("https://www.infomoney.com.br/")
 
sleep(2)

#find_element_by_id
dados1 = driver.find_element(By.ID,"high").text
 
print(dados1)

sleep(2)

driver.get("https://statusinvest.com.br/fundos-imobiliarios/hglg11")

#NOME DO FUNDO
#find_element_by_tag_name
dados2 = driver.find_element(By.TAG_NAME,"h1").text
 
print(dados2)

#VALOR ATUAL
#find_element_by_class_name
dados3 = driver.find_element(By.CLASS_NAME,"value").text
 
print(dados3)

#MIN 52 SEMANAS
#find_elements_by_class_name
dados4 = driver.find_elements(By.CLASS_NAME,"value")[1].text
 
print(dados4)

#P/VP
#find_elements_by_css_selector
dados5 = driver.find_element(By.CSS_SELECTOR,"#main-2 > div.container.pb-7 > div:nth-child(5) > div > div:nth-child(2) > div > div:nth-child(1) > strong").text

#NUMERO DE COTISTAS
print(dados5)

#find_element_by_xpath
dados6 = driver.find_element(By.XPATH,'//*[@id="main-2"]/div[2]/div[5]/div/div[6]/div/div[1]/strong').text
 
print(dados6)
```


[Webdriver Manager for Python](https://pypi.org/project/webdriver-manager/)

```bash
pip install webdriver-manager
```

[selenium.webdriver.common.by](https://www.selenium.dev/selenium/docs/api/py/selenium_webdriver_common/selenium.webdriver.common.by.html#selenium.webdriver.common.by)

