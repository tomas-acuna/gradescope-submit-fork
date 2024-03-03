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
def get_login(same):
    cpath = path.expanduser('~/.gradescope')
    if path.isfile(cpath):
        with open(cpath, 'r') as f:
            print('Reading from ~/.gradescope')
            email = f.readline().strip()
            password = f.readline().strip()
            if same:
                last_course = f.readline().strip()
                last_assign = f.readline().strip()
            else:
                last_course = None
                last_assign = None
            return email, password, last_course, last_assign, True

    else:
        print('There is no file located at ~/.gradescope')
        email = input('Email: ').strip()
        password = pwinput(mask='*').strip()
        return email, password, None, None, False


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

def get_fuc(els, name):
    return list(map(lambda el: el.text, els)).index(name)

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

def print_submission_outline(outline):
    lines = outline.split("\n")
    state = 0
    for line in lines:
        if line and line[-1] == ")":
            if state == 1:
                print("\033[31m" + line + "\033[0m")
            elif state == 2:
                print("\033[32m" + line + "\033[0m")
            else:
                print(line)
        else:
            print(line)
            if line == "Failed Tests":
                state = 1
            if line == "Passed Tests":
                state = 2

def get_confirmation(cn, pn):
    print('You are submitting the following project:')
    print('  ' + cn)
    print('  ' + pn)
    while True:
        proceed = input('Proceed? (y/n): ').strip()
        if proceed == 'y': break
        if proceed == 'n': sys.exit()

def main():
    flags, args = partitioned_args()
    if len(args) != 1:
        sys.exit('You must specify exactly one file.')
    if len(flags) > 2:
        sys.exit('Too many flags.')

    file_arg = args[0]
    if(not path.isfile(file_arg)):
        sys.exit(f'File does not exist: {file_arg}')
    file_path = path.abspath(file_arg)

    same = '-s' in flags

    email, password, last_course, last_assign, config_exists = get_login(same)

    if same:
        get_confirmation(last_course, last_assign)

    print('Connecting to Gradescope...')

    if '-c' in flags:
        driver = get_driver('-c')
    elif '-e' in flags:
        driver = get_driver('-e')
    else:
        driver = get_driver('-f')

    try:
        driver.get('https://gradescope.com/')
        driver.find_element(By.CLASS_NAME, 'js-logInButton').click()

        term = gradescope_login(driver, email, password, config_exists)
        courses = term.find_elements(By.CLASS_NAME, 'courseBox--shortname')

        if same:
            fuc = get_fuc(courses, last_course)
        else:
            fuc = print_menu('Courses:', 'Choose course: ', courses)
        course_name = courses[fuc].text
        courses[fuc].click()

        old_projects = driver.find_elements(By.CSS_SELECTOR, 'th a')
        new_projects = driver.find_elements(By.CSS_SELECTOR, 'th .js-submitAssignment')
        # old: a project that has already been submitted
        # new: a project that has yet to be submitted
        projects = old_projects + new_projects
        div = len(old_projects)

        if same:
            fuc2 = get_fuc(projects, last_assign)
        else:
            fuc2 = print_menu('Projects:', 'Choose project: ', projects)
        project_name = projects[fuc2].text
        projects[fuc2].click()

        if not same:
            cpath = path.expanduser('~/.gradescope')
            with open(cpath, 'w') as file:
                file.write("\n".join((email, password, course_name, project_name)))

        if fuc < div:
            try:
                driver.find_element(By.CLASS_NAME, 'js-submitAssignment').click()
            except:
                sys.exit('Project is past deadline.')

        if not same:
            get_confirmation(course_name, project_name)

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
        print_submission_outline(outline.text)

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
