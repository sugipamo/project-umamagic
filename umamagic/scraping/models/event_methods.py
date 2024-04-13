def default_methods():
    pass

def access_google(driver, url):
    driver.get(url)
    driver.find_elements("xpath", ".//a")[0].click()

def save_google_html(driver, url):
    driver.get(url)
    from .html_documents import HtmlDocuments
    HtmlDocuments.objects.create(url=url, html=driver.page_source)
    

