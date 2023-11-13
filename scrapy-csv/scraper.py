from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import os
import pandas as pd

# junta todos os arquivos .xls em um único arquivo .csv
def concat_csv_from_dir():
  # os arquivos estão como .xls mas são csv
  dirname = os.path.dirname(__file__)
  dirPath = os.path.join(dirname, 'downloads')
  files = os.listdir(dirPath)
  files = [file for file in files if file.endswith('.xls')] # pega apenas os arquivos .xls
  df = pd.concat([pd.read_csv(os.path.join(dirPath, file), encoding='utf-16-le', delimiter='\t', engine='python') for file in files]) # concatena todos os arquivos
  df.to_csv(os.path.join(dirPath, 'all.csv'), index=False, encoding='utf-16-le', sep='\t') # salva o arquivo concatenado como .csv


class Scrapper:
  url = 'https://www.ssp.sp.gov.br/transparenciassp/Consulta2022.aspx'

  def __init__(self, timeout=900, log=None):
    self.timeout = timeout
    self.log = log
    self.download_dir = self.get_download_dir()

    self.clear_non_finished_downloads() # remove downloads não finalizados

    self._driver = self.__get_chrome_driver(self.timeout) # cria o driver do chrome
    self._wait = WebDriverWait(self._driver, self.timeout) # função de espera do selenium
    self._driver.get(self.url) # abre a url

  @staticmethod
  def get_download_dir(): # retorna o diretório de downloads
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, 'downloads')

  @staticmethod
  def __get_chrome_driver(timeout): # retorna o driver do chrome
    service = Service()
    options = webdriver.ChromeOptions()  
    download_dir = Scrapper.get_download_dir()

    options.add_experimental_option('prefs', {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
    })

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(timeout)

    return driver
  
  def click_button(self, button_id): # clica em um botão
    self._wait.until(EC.element_to_be_clickable((By.ID, button_id))) # espera o botão ficar clicável
    button = self._driver.find_element(By.ID, button_id) # pega o botão
    button.click() # clica no botão
  
  def click_download_button(self): # clica no botão de download
    buttonId = 'cphBody_ExportarBOLink'
    self._wait.until(EC.element_to_be_clickable((By.ID, buttonId))) # espera o botão ficar clicável
    self._driver.find_element(By.ID, buttonId).click() # clica no botão
    self.wait_download()

  def wait_download(self): # espera o download finalizar
    while True:
      time.sleep(10)
      if self.__is_download_finished():
        break
          
  def __is_download_finished(self): # verifica se o download finalizou
    files = os.listdir(self.download_dir)
    for filename in files:
      if filename.endswith('.crdownload'):
          return False
    print('Download finalizado')
    return True
  
  def clear_non_finished_downloads(self): # remove downloads não finalizados
    files = os.listdir(self.download_dir)
    for filename in files:
      if filename.endswith('.crdownload'):
        os.remove(os.path.join(self.download_dir, filename))

scrapper = Scrapper() # cria uma instância do scrapper

scrapper.click_button('cphBody_btnFurtoVeiculo') # clica no botão de furto de veículos

#2020 até 2022 (0 até 2)
for ano in range(0, 3): 
  # cphBody_lkAno20
  buttonId = 'cphBody_lkAno2' + str(ano)
  scrapper.click_button(buttonId)

  # 1 até 12
  for mes in range(1, 13):
    buttonId = 'cphBody_lkMes' + str(mes)
    scrapper.click_button(buttonId)
    scrapper.click_download_button()

concat_csv_from_dir() 

