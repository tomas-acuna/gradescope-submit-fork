# AUTHORS: Owen Bechtel, Omar Osman, Sean O'Dea
# Hack(H)er413 Event
# 2/25/2023

import sys
from os import path
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.common.by import By

# reads email and password from ~/.gradescope
# if file does not exist, reads from terminal
def get_login():
    cpath = path.expanduser('~') + '/.gradescope'
    if path.exists(cpath):
        with open(cpath, 'r') as f:
            print('Reading from ~/.gradescope')
            email = f.readline().strip()
            password = f.readline().strip()
            return email, password

    else:
        print('There is no file located at ~/.gradescope')
        email = input('Email: ').strip()
        password = getpass('Password: ').strip()
        return email, password


def print_menu(title, prompt, els):
    print(title)
    for (i, el) in enumerate(els):
        print(f'  {i}: {el.text}')

    while True:
        fuc = input(prompt).strip()
        # TO CLARIFY: FUC means formatted user choice
        if fuc.isdigit() and int(fuc) < len(els): 
            return int(fuc)
        print('Invalid input')


def main():
    if(len(sys.argv) == 1):
        print('No file specified')
        return
    
    else:
        arg = sys.argv[1]
        if(not path.exists(arg)):
            print('File does not exist')
            return
        file_path = path.abspath(arg)

    email, password = get_login()

    driver = webdriver.Firefox()
    driver.get('https://gradescope.com/')
    driver.find_element(By.CLASS_NAME, 'js-logInButton').click()
    
    driver.find_element(By.ID, 'session_email').send_keys(email)
    driver.find_element(By.ID, 'session_password').send_keys(password)
    driver.find_element(By.CLASS_NAME, 'tiiBtn-full').click()

    term = driver.find_element(By.CLASS_NAME, 'courseList--coursesForTerm')
    courses = term.find_elements(By.CLASS_NAME, 'courseBox--shortname')
    
    fuc = print_menu('Courses:', 'Choose course: ', courses)
    courses[fuc].click()

    old_projects = driver.find_elements(By.CSS_SELECTOR, 'th a')
    new_projects = driver.find_elements(By.CSS_SELECTOR, 'th .js-submitAssignment')
    # old: a project that has already been submitted
    # new: a project that has yet to be submitted
    projects = old_projects + new_projects
    div = len(old_projects)

    fuc = print_menu('Projects:', 'Choose project: ', projects)
    projects[fuc].click()
    
    if fuc < div:
        try: 
            driver.find_element(By.CLASS_NAME, 'js-submitAssignment').click()
        except: 
            print('Project is past deadline')
            return

    driver.find_element(By.CLASS_NAME, 'dz-hidden-input').send_keys(file_path)
    driver.find_element(By.CLASS_NAME, 'js-submitCode').click()
    

main()

