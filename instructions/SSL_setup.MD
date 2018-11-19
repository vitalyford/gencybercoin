## Setup AWS SSL Certificate

1. Sign in to the [AWS Console](https://console.aws.amazon.com)

2. Under the Services drop-down, search for "Certificate Manager" which is also located under the "Security, Identity & Compliance" section.

    <img src="img-readme/SSL_setup/SSL_certSearch.JPG" width="250">

    a. Click "Get started" under the Provision certificates section.
    
    b. Click on "Request a certificate". Select "Request a public certificate".
    
    <img src="img-readme/SSL_setup/SSL_certRequest.JPG" width="250">

    c. Add your domain name and click "Next".
    
    <img src="img-readme/SSL_setup/SSL_certDomain.JPG" width="250">

    d. Select "DNS validation" as the validation method, and click "Review".
    
    <img src="img-readme/SSL_setup/SSL_certValidation.JPG" width="250">

    e. Review your selections, and click "Confirm and request".

    <img src="img-readme/SSL_setup/SSL_certReview.JPG" width="250">

    f. For the validation, click the "Create record in Route 53" button to save this DNS configuration.

    <img src="img-readme/SSL_setup/SSL_certRecord.JPG" width="250">

3. Navigate to your Elastic Beanstalk environment. 
    
    a. Select "Configuration" on the left-hand side.

    <img src="img-readme/SSL_setup/SSL_configEB.JPG" width="250">

    b. Under the Load balancer section, click "Modify".

    c. Click the "Add listener" button located on the right-hand side.

    <img src="img-readme/SSL_setup/SSL_listenerButton.JPG" width="250">

    d. Set the fields to:
        Listener port:      443
        Listener protocol:  HTTPS
        Instance port:      80
        Instance protocol:  HTTP
        SSL certificate: _the certificate you          previously created_

    <img src="img-readme/SSL_setup/SSL_listenerFields.JPG" width="250">

    e. After adding the new listener, you should see it listed as Pending.

    <img src="img-readme/SSL_setup/SSL_listenerPending.JPG" width="250">

    f. **IMPORTANT:** Be sure to scroll down to the bottom of the page and click "Apply".

    <img src="img-readme/SSL_setup/SSL_listenerApply.JPG" width="250">

    g. Navigate back to your Elastic Beanstalk Dashboard and wait for the environment to finish updating.

    h. Once your environment is done updating, rename the gencybercoin\cryptocoin\.ebextensions\04_ssl_apache_config file so that its extension is .config.

    i. Navigate to the first cryptocoin directory in the command prompt / terminal. You should be able to see the manage.py file in this directory.

    j. Run the following command:
    
    `eb deploy`

    k. In your web browser, go to your new url (i.e. "https://yourdomainname").