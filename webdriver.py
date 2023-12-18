# abre webdriver e faz login no site

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://mob1nvpc.pipz.io")

# faz login email="cs.time@novovarejo.com" senha="*hjuy%%4@"
time.sleep(5)
email = driver.find_element(By.ID, "email")
email.send_keys("cs.time@novovarejo.com")
senha = driver.find_element(By.ID, "password")
senha.send_keys("*hjuy%%4@")
senha.send_keys(Keys.RETURN)
time.sleep(5)

driver.get("https://mob1nvpc.pipz.io/pipz/transactional-server/servers")
time.sleep(5)

driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[1]/nav/nav-list-horizontal/ul/li[4]/a").click()

# Abre aba templates
time.sleep(5)

with open('array_php.txt', 'w') as f:
    # Faz um loop na div que possui os templates para abrir um por um e capturar o campo subject
    for i in range(1, 1000):
        # /html/body/div[2]/div[1]/div[3]/div/section/div/div/div[2]/div[1]/div[2]/div/a
        # /html/body/div[2]/div[1]/div[3]/div/section/div/div/div[2]/div[2]/div[2]/div/a
        # /html/body/div[2]/div[1]/div[3]/div/section/div/div/div[2]/div[3]/div[2]/div/a
        # abre template
        # driver.find_element(By.XPATH, f"/html/body/div[2]/div[1]/div[3]/div/section/div/div/div[2]/div[{i}]/div[2]/div/a").click()
        element = driver.find_element(By.XPATH, f"/html/body/div[2]/div[1]/div[3]/div/section/div/div/div[2]/div[{i}]/div[2]/div/a")
        action = ActionChains(driver)
        action.key_down(Keys.COMMAND).click(element).key_up(Keys.COMMAND).perform()
        driver.switch_to.window(driver.window_handles[i])
        
        time.sleep(5)
        # captura template
        template = driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/div[3]/div/wizard/full-modal/div/full-modal-content/div[1]/h1')

        # captura subject
        subject = driver.find_element(By.XPATH, f'//*[@id="ui-tinymce-1"]')
        
        # cria uma string array php com o subject e salva em um arquivo txt
        array_php = """
            [
                'template' => '""" + template.text + """',
                'subject' => '""" + subject.text + """',
            ],
        """
        print(array_php)
        # abre arquivo txt e adiciona o array php
        
        f.write(array_php)

        driver.switch_to.window(driver.window_handles[0])
        time.sleep(5)
    f.close()
