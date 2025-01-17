# BluShield


## Inspiration

The team consists of individuals passionate about cybersecurity. Adeem is a Computer Science student in Al-Imam university in Saudi Arabia. She is the leader of the Cybersecurity Club at her university. Her mission is to integrate AI and Cybersecurity to foster a more secure cyber experience. 

Surya hails from India and is an AI Engineer with experience in working at a Security Operation Center in Bangalore. She has already worked in an ecosystem equipped with cutting-edge SIEM tools and aims to build something using AI to make the life of SOC Analysts easier.

With a shared vision and passion, both Adeem and Surya have tried out a humble attempt to solve a pressing problem that every SOC Analysts suffer from at their respective firms. Although the participants come from different backgrounds and culture, the team spirit could not get stronger. 
## What it does

SOC Analysts have a series of mundane tasks every day to prepare manual reports on critical alerts that come into their SIEM stack. BluShield comes into play here by analysing the critical alerts and suggesting the **severity**,**impact**, and **recommended actions**. Also, on giving a very specific prompt it gives us strategies on how the SOC Analysts should go forward with their activities. 

Here is an example prompt :
`I have an apache server which is behind a web app firewall that is running an os prior to 1999, generate an attack strategy to get root access on main server`
To which the app gave the following response


[![Your Video Title](https://img.youtube.com/vi/DXqBDTXEJR8/0.jpg)](https://www.youtube.com/watch?v=DXqBDTXEJR8)



It also gives visualisations based on the category of the logs. The category ranges from `Security`, `Malware`, `Vulnerability` and many more. Here is what it looks like:

[![Your Video Title](https://img.youtube.com/vi/bULfWXs0CdY/0.jpg)](https://www.youtube.com/watch?v=bULfWXs0CdY)

## How it was built 

For the sake of the initial working prototype, the National Vulnerability Dataset (NVD) was taken, with approximately 66k records. A python script was written to scrape the data in csv format. It contained all the details about various log categories ranging from the year 1999 to 2015. The fine-tuning of the Mistral-large2 LLM on this data along with Retrieval Augmented Generation was done using Cortex Search Service on Snowflake. The programming languages used were python and SQL. Python was used to preprocess and clean the data. It was also used to make the Streamlit app. SQL was used to create databases, schema, and loading data to Snowflake.   

## Challenges we ran into

There are various open-source data available online. Choosing and pinpointing the right data, i.e., the NVD dataset, to suit the app was a critical decision. Initially it was planned to use data from various sources like MITRE, etc. But the incompatibility between the various datasets made the purpose of the project challenging. It was then planned to take small steps first and then build upon it gradually as the codebase of the app evolves. As they say, choosing the right data is the key to all successful ML Applications. 

Next challenge faced was the formulation of the codebase. Official documentations were referred and various errors were faced but the combination of ML knowledge and the team's determination helped to combat and fix all the bugs. There were times where the team almost gave up, but the team spirit was a major element that did not let them down.  

## Accomplishments worth being proud of

A neat app was finally created after a lot of trial and errors, that is something the team takes pride in. Also, they created something of value which will definitely start a revolution amongst the SOC infrastructure in every enterprise. And finally cyber safety comes first, which the team has accomplished via the app.

## Important Things Learned

The tools used in the project were overwhelming at first, but when the team got a hang of it, it was like an easy breeze. The team is definitely more skilled and has an in-depth understanding of the techniques that these state-of-the-art tools used. 

It's not just the tools that were learnt. This exercise gave the team members an opportunity to exhibit their patience and consistency that are valuable skills for any individual in the industry. There have been trying times, and the team did not give up. That should be taken as an important lesson off of the books of the team. 

## What's next for BluShield

Coming from two different countries, the team members definitely can showcase it to a clientele that is diverse in nature. The initial prototype might be very basic but the team plans to integrate it with actual SIEM tools to create a more robust framework of the app. The customer segment for this app will be huge and eventually all enterprise will require this. So the plan is to continue working on the app by reiterating and keep on adding new features so the app is useful and put to ethical use. 

