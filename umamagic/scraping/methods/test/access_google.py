def main(driver, url):
    driver.get(url)
    driver.find_elements("xpath", ".//a")[0].click()
    
if __name__ == '__main__':
    main()