import os
import io
import time
import random
import requests

# Speech Recognition Imports
import pydub
import speech_recognition as sr

# Selenium
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium import webdriver

# Firefox / Gecko Driver Related
FIREFOX_BIN_PATH = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
GECKODRIVER_BIN = r"C:\geckodriver.exe"

# Randomization Related
MIN_RAND        = 0.64
MAX_RAND        = 1.27
LONG_MIN_RAND   = 4.78
LONG_MAX_RAND   = 11.1
REAL_LONG_MIN_RAND   = 6.78 * 60
REAL_LONG_MAX_RAND   = 9.1 * 60

NUMBER_OF_ITERATIONS = 100
RECAPTCHA_PAGE_URL = "https://www.google.com/recaptcha/api2/demo"
                
class rerebreakcaptcha(object):
    def __init__(self):
        os.environ["PATH"] += os.pathsep + GECKODRIVER_BIN
        ops = Options()
        ops.binary_location = FIREFOX_BIN_PATH
        #ops.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0")

        serv = Service(GECKODRIVER_BIN)

        self.driver = webdriver.Firefox(service=serv, options=ops)
        self.driver.implicitly_wait(30) # seconds
        
    def is_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True
    
    def is_interactable_by_id(self, element_id):
        try:
            self.driver.find_element(By.ID, element_id)
            self.driver.find_element(By.ID, element_id).send_keys(Keys.DELETE)
        except NoSuchElementException:
            return False
        except ElementNotInteractableException:
            return False
        return True
        
    def get_recaptcha_challenge(self):
        for _ in range(3):
            try:
                # Navigate to a ReCaptcha page
                self.driver.get(RECAPTCHA_PAGE_URL)
                time.sleep(random.uniform(MIN_RAND, MAX_RAND))
                
                # Get all the iframes on the page
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                
                # Switch focus to ReCaptcha iframe
                self.driver.switch_to.frame(iframes[0])
                time.sleep(random.uniform(MIN_RAND, MAX_RAND))
                
                # Verify ReCaptcha checkbox is present
                if not self.is_exists_by_xpath('//div[@class="recaptcha-checkbox-border" and @role="presentation"]'):
                    print(f"[{self.current_iteration}] No element in the frame!!")
                    continue
                
                # Click on ReCaptcha checkbox
                self.driver.find_element(By.XPATH, '//div[@class="recaptcha-checkbox-border" and @role="presentation"]').click()
                time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))
            
                # Check if the ReCaptcha has no challenge
                if self.is_exists_by_xpath('//span[@aria-checked="true"]'):
                    print(f"[{self.current_iteration}] ReCaptcha has no challenge. Trying again!")
                else:
                    return
            except NoSuchElementException:
                print(f"[{self.current_iteration}] Exception no such element. Trying again!")
                time.sleep(random.uniform(MIN_RAND, MAX_RAND))
            
    def get_audio_challenge(self, iframes):
        # Switch to the last iframe (the new one)
        self.driver.switch_to.frame(iframes[-1])
        
        # Check if the audio challenge button is present
        if not self.is_exists_by_xpath('//button[@id="recaptcha-audio-button"]'):
            print("[{0}] No element of audio challenge!!".format(self.current_iteration))
            return False
        
        print("[{0}] Clicking on audio challenge".format(self.current_iteration))
        # Click on the audio challenge button
        self.driver.find_element(By.XPATH, '//button[@id="recaptcha-audio-button"]').click()
        time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))
        return True
    
    def get_challenge_audio(self, url):
        # Download the challenge audio and store in memory
        request = requests.get(url)
        audio_file = io.BytesIO(request.content)
        
        # Convert the audio to a compatible format in memory
        try:
            converted_audio = io.BytesIO()
            sound = pydub.AudioSegment.from_mp3(audio_file)
            sound.export(converted_audio, format="wav")
            converted_audio.seek(0)
            
            return converted_audio
        except pydub.exceptions.CouldntDecodeError:
            return None
    
    def speech_to_text(self, audio_source):
        # Initialize a new recognizer with the audio in memory as source
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_source) as source:
            audio = recognizer.record(source) # read the entire audio file

        audio_output = ""
        # recognize speech using Google Speech Recognition
        try:
            audio_output = recognizer.recognize_google(audio)
            print(f"[{self.current_iteration}] Google Speech Recognition: {audio_output}")
        except sr.UnknownValueError:
            print(f"[{self.current_iteration}] Google Speech Recognition could not understand audio")
            # audio_output = "this is a placeholder"
        except sr.RequestError as e:
            print(f"[{self.current_iteration}] Could not request results from Google Speech Recognition service; {e}")
            
        return audio_output
    
    def solve_audio_challenge(self):
        # Verify audio challenge download button is present
        if not self.is_exists_by_xpath('//a[@class="rc-audiochallenge-tdownload-link"]') and \
                not self.is_exists_by_xpath('//div[@class="rc-textchallenge-control"]'):
            print(f"[{self.current_iteration}] No element in audio challenge download link!!")

            # Navigate to a ReCaptcha page
            self.driver.get(RECAPTCHA_PAGE_URL)

            print(f"[{self.current_iteration}] Sleeping for a while now (6 to 9 minutes)")
            random_sleep = random.uniform(REAL_LONG_MIN_RAND, REAL_LONG_MAX_RAND)
            time.sleep(random_sleep)

            minutes, seconds = divmod(round(random_sleep), 60)
            print(f"[{self.current_iteration}] Slept for {minutes:d} minutes and {seconds:d} seconds")
            
            return False

        # Get the audio challenge URI from the download link
        download_object = self.driver.find_element(By.XPATH, '//a[@class="rc-audiochallenge-tdownload-link"]')
        download_link = download_object.get_attribute('href')
        
        # Get the challenge audio to send to Google
        converted_audio = self.get_challenge_audio(download_link)
        if converted_audio is None :
            return False
        
        # Send the audio to Google Speech Recognition API and get the output
        audio_output = self.speech_to_text(converted_audio)
        if len(audio_output) == 0:
            return False

        # Enter the audio challenge solution
        if not self.is_interactable_by_id('audio-response'):
            return False

        self.driver.find_element(By.ID, 'audio-response').send_keys(audio_output)
        time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))

        # Click on verify
        self.driver.find_element(By.ID, 'recaptcha-verify-button').click()
        time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))
        
        return True
            
    def solve(self, current_iteration):
        self.current_iteration = current_iteration + 1

        if self.current_iteration % 20 == 0 and self.current_iteration != NUMBER_OF_ITERATIONS:
            # Navigate to a ReCaptcha page
            self.driver.get(RECAPTCHA_PAGE_URL)

            print(f"[{self.current_iteration}] Sleeping for a while now (6 to 9 minutes)")
            random_sleep = random.uniform(REAL_LONG_MIN_RAND, REAL_LONG_MAX_RAND)
            time.sleep(random_sleep)

            minutes, seconds = divmod(round(random_sleep), 60)
            print(f"[{self.current_iteration}] Slept for {minutes:d} minutes and {seconds:d} seconds")

        
        # Get a ReCaptcha Challenge
        self.get_recaptcha_challenge()
        
        # Switch to page's main frame
        self.driver.switch_to.default_content()
        
        # Get all the iframes on the page again- there is a new one with a challenge
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        
        # Get audio challenge
        if not self.get_audio_challenge(iframes):
            return False
        
        # Solve the audio challenge
        if not self.solve_audio_challenge():
            return False
        
        solve_more_count = 3
        for _ in range(solve_more_count):
            # Switch to the ReCaptcha iframe to verify it is solved
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(iframes[0])
            
            if self.is_exists_by_xpath('//span[@aria-checked="true"]'):
                return True
            
            # Switch to page's main frame
            self.driver.switch_to.default_content()
            
            # Get all the iframes on the page again- there is a new one with a challenge
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            # Switch to the ReCaptcha iframe
            self.driver.switch_to.frame(iframes[-1])
            
            # Check if there is another audio challenge and solve it too
            if self.is_exists_by_xpath('//div[@class="rc-audiochallenge-error-message"]') and \
                    self.is_exists_by_xpath('//div[contains(text(), "Multiple correct solutions required")]'):
                print(f"[{self.current_iteration}] Need to solve more. Let's do this!")
                self.solve_audio_challenge()
            else:
                return False
                
def main():
    rerebreakcaptcha_obj = rerebreakcaptcha()
    
    counter = 0
    for i in range(NUMBER_OF_ITERATIONS):
        if rerebreakcaptcha_obj.solve(i):
            counter += 1
            
        time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))
        print(f"Successful breaks: {counter}")
        
    print(f"Total successful breaks: {counter}\{NUMBER_OF_ITERATIONS}")

if __name__ == '__main__':
    main()
