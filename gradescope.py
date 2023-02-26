# AUTHORS: Owen Bechtel, Omar Osman, Sean O'Dea
# Hack(H)er413 Event
# 2/25/2023

import sys
from os import path
from pwinput import pwinput

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
            
    else:
        print('There is no file located at ~/.gradescope')
        email = input('Email: ').strip()
        password = pwinput(mask='*').strip()
        
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


def get_driver(flag):
    if flag in [ '-f', '--firefox' ]: return webdriver.Firefox()
    if flag in [ '-c', '--chrome' ]: return webdriver.Chrome()
    if flag in [ '-e', '--edge']: return webdriver.Edge()
    if flag in [ '-s', '--safari']: return webdriver.Safari()
    sys.exit(f'Unknown flag: {flag}')


def partitioned_args():
    flags = []
    other = []
    for a in sys.argv[1:]:
        if a[0] == '-': flags.append(a)
        else: other.append(a)
    return flags, other
    

def main():
    flags, args = partitioned_args()
    if len(args) != 1:
        sys.exit('You must specify exactly one file')
    if len(flags) > 1:
        sys.exit('Too many flags')
    
    file_arg = args[0]    
    if(not path.exists(file_arg)):
        sys.exit('File does not exist')
    file_path = path.abspath(file_arg)

    email, password = get_login()

    if len(flags) == 0: 
        driver = webdriver.Firefox() # default Firefox because master race
    else: 
        driver = get_driver(flags[0])
        
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
            sys.exit('Project is past deadline')

    driver.find_element(By.CLASS_NAME, 'dz-hidden-input').send_keys(file_path)
    driver.find_element(By.CLASS_NAME, 'js-submitCode').click()
    print('Project submitted')
    print()
    print('SUBMISSION OUTLINE')
    outline = driver.find_element(By.CLASS_NAME, 'submissionOutline')
    print(outline.text)

    

main()

