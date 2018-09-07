#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re

URL = 'http://www.davidpricco.com/santa-barbara-startups/'
OUT_FILENAME = 'sb_companies.tsv'

html = requests.get(URL)
doc = BeautifulSoup(html.text, 'html.parser')
out_str = ''

companies = doc.find_all(lambda tag: tag.name == 'p' and tag.find('span', {'class': 'companyname'}))

# TSV format: name\tnumberOfEmployees\taddress\twebsite\tdescription
for company in companies:
    name = company.find('span', {'class': 'companyname'}).string.strip()  # Strip() is like trim()
    if name is None:  # If the company's name isn't found, skip this company
        continue
    else:
        out_str += name
    out_str += '\t'

    # Documentation for positive lookbehind: Matches if the current position in the string is preceded by a
    # match for ... that ends at the current position. This is called a positive lookbehind assertion.
    # Number of employees string could be a single number or a number range, and the numbers may have commas
    num_emps = re.findall('(?<=# of Employees: )[\d,-]+', company.text)
    if len(num_emps) > 0:  # re.findall() returns an empty list if the pattern is not found
        num_emps = num_emps[0]
        out_str += num_emps
    out_str += '\t'

    address = company.find_next('p')  # The address info is in a <p> tag following the <p> tag for the company
    if address.text.startswith('Address:'):  # Check that this <p> tag is for an address, not a company tag
        address = address.text.replace('Address:', '').strip()  # Remove 'Address:' from the start of the string
        if len(address) > 0:  # Check that the original address.text.strip() was not 'Address:' (empty)
            # Street address is on the same line as 'Address:'. City, state, and ZIP are on the next line.
            address = address.replace('\n', ',')
            out_str += address
    out_str += '\t'

    website = company.find('a')
    if website is not None:
        website = website.string.strip()
        out_str += website
    out_str += '\t'

    description = re.findall('(?<=Description: )[^\n]+', company.text)  # Description ends with a newline
    if len(description) > 0:
        description = description[0]
        out_str += description

    out_str += '\n'

out_file = open(OUT_FILENAME, 'w', encoding="utf-8")
out_file.write(out_str)
out_file.close()
