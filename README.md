# Re-ReBreakCaptcha

A logic vulnerability, dubbed Re-ReBreakCaptcha, which lets you easily bypass Google's ReCaptcha v2 anywhere on the web.


More details in the post: https://east-ee.com/2022/02/28/1367/

## Installation

 - Requires Python 3.7+, Firefox and GeckoDriver.
 - Install the required dependencies using [pip](https://pip.pypa.io/en/stable/):  
 
 ```bash
 pip3 install -r requirements.txt
 ```

  - Change the 'FIREFOX_BIN_PATH' and 'GECKODRIVER_BIN' paths in the code. 
  - Then, to run the POC: 
 
 ```bash
 python re-rebreakcaptcha.py
 ```
 
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
