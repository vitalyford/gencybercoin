# UPDATE 2/16/2024

I used to use Freenom for the gencybercoin.tk domain and now it's long gone, Freenom has closed. So, the sample app has been moved to [https://gencybercoin.vford.com](https://gencybercoin.vford.com)

# Introduction

GenCyberCoin is the project developed by Dr. Vitaly Ford in collaboration with Cybersecurity Education Research and Outreach Center at Tennessee Tech University (Dr. Ambareen Siraj) as a part of the NSA/NSF GenCyber grant. GenCyberCoin is a web platform that teaches students the following concepts:

- Cryptocurrency concepts and digital currency trading markets, including blockchain applications
- Cybersecurity principles (confidentiality, integrity, availability, defense in depth, keep it simple, think like an adversary)
- Bug bounty program, software bugs, and secure coding
- Password management and its strength
- Social and ethical norms and values
- Reconnaissance

GenCyberCoin has been successfully deployed at Tennessee Tech's GenCyber summer camps in 2017 and 2018. Students of 8-12 grades expressed high enthusiasm and actively participated in the GenCyberCoin platform, searching for bugs, performing reconnaissance, and earning coins for their leadership skills and willingness to learn cybersecurity. They later spent their coins at the GenCyberCoin marketplace to buy real items that our camp's Team has prepared for them.

GenCyberCoin reinforces the objectives that the GenCyber program has established. It complements the existing GenCyber camp activities and facilitates building curiosity and passion to pursue cybersecurity and to solve challenges in this field.

# Sample Lesson Plan

A sample lesson plan can be found [here](instructions/GenCyberCoin_Sample_Lesson_Plan.pdf).

# Video Description

A 12-minute summary video on GenCyberCoin platform for instructors/admins is available here:

[![Watch the video](instructions/img-readme/homepage.png)](https://youtu.be/HMivgo8Tumo)

A 2-minute summary video on GenCyberCoin platform for students is available here:

[![Watch the video](instructions/img-readme/students.png)](https://youtu.be/fk7O60jSOy8)

# Deploy to Heroku
- This is __no longer free__ (*sad_face*) but it is the easiest way to deploy GenCyberCoin as your own web app.
- Please ensure that you have created an account on [Heroku.com](https://www.heroku.com/) and you are logged in there.<br/>
  [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
- When you click on this "Deploy to Heroku" button, enter the name of the app you want your GenCyberCoin to be deployed to (must be unique across all Heroku dynos), and then click on "Deploy app". Your GenCyberCoin will be available within a minute at `https://your_app's_name.herokuapp.com`
- Next, you can go straight to [creating administrators](#creating-administrators) section and set that up on your newly deployed app.
- Learn about [Heroku's Free Dyno Hours](https://devcenter.heroku.com/articles/free-dyno-hours) and [Heroku's Dyno Comparison](https://mikecoutermarsh.com/load-testing-heroku-1x-2x-px-dyno/) (the free dyno uses Heroku 1x Dyno and it is enough to simulteneously have up to ~200 users)

# Bug Bounty

A Bug Bounty walk through (solution video) is available upon request.

# Docker instructions

GenCyberCoin is dockerized (runs on nginx + gunicorn + postgresql + python3.7 + Django) and to run GenCyberCoin through Docker, you would need to install:
 - Docker (or Docker Desktop if running on Windows or Mac)
 - Docker Compose

After installing the above-mentioned software, open the Docker Terminal and navigate to this project's main directory (a directory where `docker-compose.yml` is located). Then, run `docker-compose up` (or `docker compose up` if you run it directly via docker) from the terminal, and it will build and run the containers. Upon successful execution, the GenCyberCoin will be running on your IP address, port 80. You can navigate to it in your browser and go straight to [creating administrators](#creating-administrators) section.

To stop the containers, type `docker-compose down` (or `docker compose down`) from the same place (where `docker-compose.yml` is located). All your data will be saved even after stopping and starting (`docker-compose up` or `docker compose up`) the containers back up again.

# Local setup instructions

The instructions for setting up a local version of the GenCyberCoin project can be found [here](instructions/Local_setup.MD).

# Amazon Web Services (AWS) setup instructions

The instructions for setting up the GenCyberCoin project on AWS can be found [here](instructions/AWS_setup.MD).

# Custom Domain setup instructions

The instructions for setting up a custom domain for your version of the GenCyberCoin project can be found [here](instructions/Domain_setup.MD).

# SSL Certificate for AWS setup instructions

The instructions for setting up a secure website certificate for you version of the GenCyberCoin project can be found [here](instructions/SSL_setup.MD).

# Creating administrators

The default superuser that is allowed to create school administrators can log in with the following credentials:<br><br>
username: `gcsuperuser`<br>
password: `gcsuperuser`<br><br>
**EXTREMELY IMPORTANT**: As soon as you log in, change your password immediately on the `Account` page.<br>

After generating codes for your GenCyber Team (administrators of your GenCyber summer camp or just yourself in a class you are teaching) on the `Code generator` page under `Admin` menu, your GenCyber Team can register their accounts on the front page of GenCyberCoin, using those codes.<br>

**IMPORTANT**: when you register the accounts, make sure that your security answers are not easy to guess based on the questions because there is a `Forgot your password` option that allows you to enter the account by guessing correctly two security questions out of three which means that your K12 students could potentially try to social engineer one of your GenCyber Team members to get into their accounts... just saying, not that it ever happened ;)<br>

An additional `admin panel` exists for the `gcsuperuser` that you can access by navigating to `localhost/gcsuperuser/` (if you are running on your PC/laptop) or `http://your_app_url/gcsuperuser/` (if you deployed the app somewhere else) (both slashes are important to type). However, use that `admin panel` at your own risk because it directly accesses the data from the database that stores everything about all users on the website.

# Questions/bugs/suggestions?

Contact Vitaly Ford fordv@arcadia.edu with one of the following subject lines, depending on what you would like to inquire:<br><br>
`GenCyberCoin:Bug`<br>
`GenCyberCoin:Question`<br>
`GenCyberCoin:Suggestion`

# Acknowledgements

We thank [NSA/NSF GenCyber program](https://www.gen-cyber.com/ "NSA/NSF GenCyber Program") for funding the implementation of this project.

We also thank Anathae Wallace, Andy Malinsky, Ivan Zhang, and Muhammad Moiz Saeed, who were Computer Science and Mathematics students at Arcadia University, for bug hunting, testing the project's code, adding new features, and helping with writing these instructions.

# Hall of Fame

A list of students from different schools who contributed to identifying security flaws on this platform (alphabetic order) and sharing those with us.

1. Devkumar Banerjee
1. Diego Mannikarote
1. Kevin Zhang
1. Leo Abanov
1. Logan Warren
1. Pierce Mannikarote
1. Ryan Glendenning
