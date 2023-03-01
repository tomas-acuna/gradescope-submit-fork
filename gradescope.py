# AUTHORS: Owen Bechtel, Omar Osman, Sean O'Dea
# Hack(H)er413 Submission
# 2/25/2023

import sys
import os
from os import path
from pwinput import pwinput

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# reads email and password from ~/.gradescope
# if file does not exist, reads from terminal
def get_login():
    cpath = path.expanduser('~/.gradescope')
    if path.isfile(cpath):
        with open(cpath, 'r') as f:
            print('Reading from ~/.gradescope')
            email = f.readline().strip()
            password = f.readline().strip()
            return email, password, True
            
    else:
        print('There is no file located at ~/.gradescope')
        email = input('Email: ').strip()
        password = pwinput(mask='*').strip()
        return email, password, False
    

def print_menu(title, prompt, els):
    print(title)
    for (i, el) in enumerate(els):
        print(f'  {i}: {el.text}')

    while True:
        fuc = input(prompt).strip()
        # TO CLARIFY: FUC means formatted user choice
        if fuc.isdigit() and int(fuc) < len(els): 
            return int(fuc)
        print('Invalid input. Please try again.')


def try_driver(fn):
    try: 
        return fn()
    except:
        print('Failed to open browser.')
        sys.exit('You can specify a different browser with -e, -c, or -f.')


def get_driver(flag):
    if flag in [ '-f', '--firefox' ]: 
        options = webdriver.firefox.options.Options()
        options.add_argument('--headless')
        return try_driver(lambda: webdriver.Firefox(options=options))
    if flag in [ '-c', '--chrome' ]: 
        options = webdriver.chrome.options.Options()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return try_driver(lambda: webdriver.Chrome(options=options))
    if flag in [ '-e', '--edge']: 
        options = webdriver.edge.options.Options()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return try_driver(lambda: webdriver.Edge(options=options))
    sys.exit(f'Unknown flag: {flag}')


def partitioned_args():
    flags = []
    other = []
    for a in sys.argv[1:]:
        if a[0] == '-': flags.append(a)
        else: other.append(a)
    return flags, other


def gradescope_login(driver, email, password, config_exists):
    while True:
        driver.find_element(By.ID, 'session_email').send_keys(email)
        driver.find_element(By.ID, 'session_password').send_keys(password)
        driver.find_element(By.CLASS_NAME, 'tiiBtn-full').click()
        try:
            return driver.find_element(By.CLASS_NAME, 'courseList--coursesForTerm')
        except:
            if config_exists:
                sys.exit('Config file contains invalid login information.')
            else:
                print('Invalid login information. Please try again.')
                email = input('Email: ').strip()
                password = pwinput(mask='*').strip()


def main():
    flags, args = partitioned_args()
    if len(args) != 1:
        sys.exit('You must specify exactly one file.')
    if len(flags) > 1:
        sys.exit('Too many flags.')
    
    file_arg = args[0]
    if(not path.isfile(file_arg)):
        sys.exit(f'File does not exist: {file_arg}')
    file_path = path.abspath(file_arg)

    email, password, config_exists = get_login()
    print('Connecting to Gradescope...')

    if len(flags) == 0: 
        driver = get_driver('-f') 
    else: 
        driver = get_driver(flags[0])

    try:
        driver.get('https://gradescope.com/')
        driver.find_element(By.CLASS_NAME, 'js-logInButton').click()
        
        term = gradescope_login(driver, email, password, config_exists)                    
        courses = term.find_elements(By.CLASS_NAME, 'courseBox--shortname')
        
        fuc = print_menu('Courses:', 'Choose course: ', courses)
        course_name = courses[fuc].text
        courses[fuc].click()

        old_projects = driver.find_elements(By.CSS_SELECTOR, 'th a')
        new_projects = driver.find_elements(By.CSS_SELECTOR, 'th .js-submitAssignment')
        # old: a project that has already been submitted
        # new: a project that has yet to be submitted
        projects = old_projects + new_projects
        div = len(old_projects)

        fuc = print_menu('Projects:', 'Choose project: ', projects)
        project_name = projects[fuc].text
        projects[fuc].click()
        
        if fuc < div:
            try:
                driver.find_element(By.CLASS_NAME, 'js-submitAssignment').click()
            except:
                sys.exit('Project is past deadline.')

        print('You are submitting the following project:')
        print('  ' + course_name)
        print('  ' + project_name)
        while True:
            proceed = input('Proceed? (y/n): ').strip()
            if proceed == 'y': break
            if proceed == 'n': sys.exit()

        driver.find_element(By.CLASS_NAME, 'dz-hidden-input').send_keys(file_path)
        driver.find_element(By.CLASS_NAME, 'js-submitCode').click()
        print('Project submitted.')
        print('Waiting for results...')
        
        loading = WebDriverWait(driver, timeout=5).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'msg-success')))
        WebDriverWait(driver, timeout=60).until(ec.staleness_of(loading))
        
        outline = driver.find_element(By.CLASS_NAME, 'submissionOutline')
        print()
        print('SUBMISSION OUTLINE:')
        print(outline.text)

        autograder = driver.find_elements(By.CLASS_NAME, 'autograderResults--topLevelOutput')
        if(len(autograder) > 0):
            print()
            print('AUTOGRADER RESULTS:')
            print(autograder[0].text)
    
    finally:
        driver.quit()
        if path.isfile('geckodriver.log'):
            os.remove('geckodriver.log')


main()

# TODO:
# Print correct results!          # DONE
# Fix random errors
# Use onedir instead of onefile