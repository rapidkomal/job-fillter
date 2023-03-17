#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get data with url

import os
import pandas as pd
import requests


page = input("Enter the pagination: ")


experience = [] 
location = [] 
company = [] 
skills = []
index = []
count = 0
for i in range(1, int(page)+1):

    url = f"https://231a-2401-4900-30d7-67a7-d5cd-545b-e129-de74.in.ngrok.io/api/v1/naukri-jobs?search_keyword=&number_of_result=100&page_number={i}"
    print(url)
    response = requests.get(url)

    df = pd.read_json(response.text, lines=False)
    df = df.drop(['message','status'], axis=1)
    for i in df['items']:

        location_labels = [p["label"] for p in i['Placeholders'] if p["type"] == "location"]

        if location_labels:
            location_str = ", ".join(location_labels)
            location.append(location_str)
        else:
            location.append("Not Available")

        experience_labels = [k["label"] for k in i['Placeholders'] if k["type"] == "experience"]
        if experience_labels:
            experience_str = ", ".join(experience_labels)
            experience.append(experience_str)
        else:
            experience.append("Not Available")
        count +=1
        company.append(i['Company Name'])
        skills.append(i['Skills'])            
        index.append(count)
#print the new DataFrame
new_df = pd.DataFrame({
    "index":index,
    "company":company,
    "location":location,
    "experience":experience,
    "skills":skills
})


# Remove duplicate rows based on all columns except 'index'
new_df = new_df.drop_duplicates(subset=[col for col in new_df.columns if col != 'index'])

new_df
# Save the DataFrame to a CSV file
# new_df.to_csv("/Users/komal/Desktop/output-job.csv", index=False)


# In[2]:


# spelling correction using openai

import openai
openai.api_key = "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"

def correct_spelling(text):
    # Replace the API key below with your own
   
    # Define the prompt and the input text
    prompt = "Correct the spelling errors in the following text:\n" + text + "\n\nCorrected text:"
    input_text = prompt + "\n"

    # Call the OpenAI API to generate the corrected text
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=input_text,
        temperature=0.5,
        max_tokens=2048,
        n = 1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extract the corrected text from the API response
    corrected_text = response.choices[0].text

    print("spelling :", corrected_text.strip())
    return corrected_text.strip()
# correct_spelling("dilli")


# In[22]:


# used to find nearest city.

import re
import spacy

def to_find_nearest_cities(city_text):
    city_name = correct_spelling(city_text)

    if city_name.lower() == "banglore" or city_name.lower() =="bangalore":
        print("The nearest cities to Bangalore are Mysore, Tumkur, and Hosur.")
        print(['bangalore', 'mysore', 'tumkur', 'hosur'])
        return ['bangalore', 'mysore', 'tumkur', 'hosur']
    # Define the input prompt
    prompt = f"What are the nearest cities to {city_name}?"

    # Generate the text output using the OpenAI GPT-3 model
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt=prompt,
      max_tokens=1024,
      n=1,
      stop=None,
      temperature=0.3,
    )

    # Extract the relevant information about the nearest cities from the output
    output_text = response.choices[0].text
    print(output_text)

    nlp = spacy.load("en_core_web_sm")

    doc = nlp(output_text)

    # Extract all entities with the "GPE" (geopolitical entity) label
    place_names = []

    for ent in doc.ents:
        name = ent.text.lower()
        name = name.replace("ncr", "").replace("greater", "")
        place_names.append(name.strip())

    print(place_names)
    
    return place_names
# to_find_nearest_cities("banglore")


# In[25]:


# Define a list of cities to search for
cities_to_search = to_find_nearest_cities("Gurugram") #place_names #['New Delhi', 'Noida', 'Gurgaon']

# Loop through each row in the dataframe
matched_rows = []
indexes = []
for i, row in new_df.iterrows():
    
    # Split the string into a list of individual locations
    location_str = row['location'].lower()
    remove_ncr = location_str.replace("ncr", "").replace("(", "").replace(")", "").replace("greater", "")
    text = re.sub("\s+", " ", remove_ncr.strip())
    new_text = re.split(r'\s|,|/', text)
    text_of_cities = [loc for loc in new_text if loc]
    city_string = row['location'].lower()
    city_list = city_string.split(',')

    for cc in cities_to_search:
        if cc in text:
            if not row['index'] in indexes:
                indexes.append(row['index'])
                matched_rows.append(row)

final_df = pd.DataFrame(matched_rows)
final_df


# In[ ]:




