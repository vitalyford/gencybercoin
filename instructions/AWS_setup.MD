## AWS account setup

1. Create an AWS account [here](https://aws.amazon.com/free/ "Create AWS Account with Free Tier") (for a new user, first year falls under a Free Tier that provides enough free AWS resources to deploy and run GenCyberCoin project for the whole year).
2. You can also [apply to join](https://www.awseducate.com/registration#APP_TYPE "AWS Educate Program") the AWS Educate Program as an Institution and within a few weeks, if approved, you will be able to receive a certain number of free AWS credits as an AWS Educator which will be enough to run GenCyberCoin for half a year (the rest of the year the machines will be shut down in any case) in the following years.

## Software installation and configuration

1. Install python3 and pip.
2. Follow the instructions on [Install the Elastic Beanstalk Command Line Interface](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html) to install EB CLI.
3. Make sure your current version of python matches the version in the environment path. For example, if using (Python 3.7.0), the path variable would be %USERPROFILE%\AppData\Local\Programs\Python\Python37\Scripts

## Launching GenCyberCoin project

1.	Create a User:
  a.	Under the Services drop-down, select "IAM" which is located under the "Security, Identity & Compliance" section. Click on “Users” on the left-hand side, then click the button “Add User.”
  b.	Create a username (e.g. cybercoin), and assign the user "Programmatic access". 
  c.	For permissions, select the third option of “Attach existing policies directly,” then search for the following policy: `AWSElasticBeanstalkFullAccess`. Click the checkbox next to the policy name.
  <img src="img-readme/AWS_setup/AWS_beanstalkpolicy.JPG" width="250">
  d.	Once you create the new user, download this user’s secret ID and key by clicking the “Download .csv” button.
  <img src="img-readme/AWS_setup/AWS_downloadCredentials.JPG" width="250">
  Save this for your future record as you will use that to connect to AWS ElasticBeanstalk later on your computer.

2.	**VERY IMPORTANT**: 
  a.	By default, this project redirects all web requests to HTTPS instead of HTTP but when you set it up for the first time, you do not have a certificate and SSL is turned off. Therefore, we need to change the extension of the following file from (.config) to (.bak). Otherwise when you set up everything, you will see a blank page instead of the GenCyberCoin home page. You can open the file and Save As with the extension (.bak).
  <img src="img-readme/AWS_setup/AWS_sslApacheToBackup.JPG" width="250"> 
  b.	The file’s location is: cryptocoin/.ebextenstions/04_ssl_apache.config. 
  c.	Note: After setting up the certificate (at the very-very-very end when everything else works), you will be able to change 04_ssl_apache.bak back to 04_ssl_apache.config.
3.	Configure Elastic Beanstalk on AWS:
  a.	Navigate to the cryptocoin directory in the command prompt / terminal (**IMPORTANT**: it is the folder where you can see manage.py and requirements.txt files, make sure you are in the correct folder). Before typing any eb commands, you have to delete the .elasticbeanstalk folder in your file directory. 
  b.	Type the following commands to configure the elastic beanstalk on AWS:
  `eb init`
  (select python 3.6 or later, you can say NO to SSH unless later you will want to connect to the machine for some reason. All updates will be done through one command,  eb deploy, which does not require SSH connection). 
  (follow the instructions and make the appropriate selections, most of which can be left at default settings. You can set your name to whatever you want, (e.g. <yourschoolname>gencyber). This is the place where you will be required to enter the secret ID and key of the cybercoin user that you have previously downloaded)
  `eb create -db.engine postgres` 
  Note: You can leave the settings as the default selections. Be careful when it prompts you to create an RDS DB master password. The password cannot have a white space  or the following symbols ‘/’, ‘”’, or ’@’.
  This command will take a while to finish.
  `eb console`
  (This is just for testing purposes, it should open a new tab in your browser on the Elastic Beanstalk page where you should see your project. The health may be in red, which is alright, as it should be green after the end of this setup process)
4.	A database will be setup automatically at this point.
5.	Set up the AWS S3 bucket:
  a.	Connecting the bucket with the project will store files including images, CSS, and Javascript. Open https://console.aws.amazon.com in your browser and choose "S3" in the Services drop down under the "Storage" section. 
  Follow the directions here: https://www.codingforentrepreneurs.com/blog/s3-static-media-files-for-django/ , starting from step 3, all the way until you reach the section called Django Setup (you do not need to do follow Django Setup, as that has already been done in the project). 
  Your bucket name can be anything you want, but it will not allow you to choose a name that has previously been created by someone else in AWS S3. 
  **IMPORTANT**: After creating the bucket, note the bucket name and the region.
  b.	Notes: You may skip step 4, as we have already added the AWSElasticBeanstalkFullAccess policy.
  In step 5, after clicking Create Policy, click on the JSON tab to set the Policy Document.
  After setting the Policy Document and the CORS policy, you will be able to set the Policy Name once you click on Review Policy.

  Be sure to add your newly created policy to your user’s permissions, by clicking Attach existing policies directly, and searching for your policy name.

  c.	Open the file located in cryptocoin/aws/conf.py and change:
  `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` - to the values in your cybercoin user’s downloaded .csv file.
  `AWS_STORAGE_BUCKET_NAME` - to the bucket name you created when you followed the instructions from the link above.
  `AWS_S3_REGION_NAME` - to the region where your bucket is in (e.g. ‘us-east-2’).
  (Just in case, you can find the region’s name if you open Amazon S3 page from https://console.aws.amazon.com and  note the Region Name in the top right corner. After that, go to                                       https://docs.aws.amazon.com/general/latest/gr/rande.html and you can scroll down to see the list of Regions and  their corresponding Region Names.
  d.	Open the file located in cryptocoin/.ebextensions/02_python.config and change SECRET_KEY value to the one   generated on this website https://www.miniwebtool.com/django-secret-key-generator/ (click on Generate Django  Secret Key button). Remember to keep double quotes around the SECRET_KEY value in 02_python.config file.
  e.	In the command prompt / terminal, navigate again to the cryptocoin folder where you can see manage.py file and  type the following command: `python manage.py collectstatic`
  	This command will collect all static files like images, CSS, Javascript, and load them to the AWS S3 bucket   that you have previously connected with this project. If that did not happen, then something went wrong with the  previous steps and your S3 bucket was not connected with the project (make sure that you correctly entered   AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in cryptocoin/aws/conf.py file as well as make sure that  AWS_STORAGE_BUCKET_NAME and AWS_S3_REGION_NAME are actually updated with the appropriate names from your S3).
6.	Navigate to the directory where manage.py is located in and type: `eb deploy`
    In a few minutes your GenCyberCoin project should be running on AWS Elastic Beanstalk that you can find either by typing `eb console` or navigating to [AWS Console](https://console.aws.amazon.com/console/home "AWS Console") in your browser and selecting `Elastic Beanstalk` among the `AWS Services`.