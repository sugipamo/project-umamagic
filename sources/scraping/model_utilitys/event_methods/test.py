from scraping.model_utilitys.html_documents import HtmlDocuments
def default_methods():
    pass

def error_methods():
    raise Exception("エラーです。")

def access_google(driver, url):
    driver.get(url)
    driver.find_elements("xpath", ".//a")[0].click()

def save_google_html(driver, url):
    driver.get(url)
    
    obj = HtmlDocuments.objects.create(url=url, html=driver.page_source)
    obj.delete()
