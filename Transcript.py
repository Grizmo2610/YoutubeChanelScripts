import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import openpyxl
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from Model import GeminiModel

def get_channel_videos_information(youtube_id: str = ..., save_path: str = ..., save_data: bool = True) -> pd.DataFrame:
    """
    Retrieves information about videos from a YouTube channel.

    Args:
        youtube_id (str, optional): The ID of the YouTube channel. Defaults to ... (placeholder).
        save_path (str, optional): Path to save the CSV file. Defaults to ... (placeholder).
        save_data (bool, optional): Whether to save the data to a file. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame containing video details.
    """

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()

    # URL of the YouTube channel's video page
    channel_url = f"https://www.youtube.com/@{youtube_id}/videos"

    # Navigate to the YouTube channel's video page
    driver.get(channel_url)

    # Wait for the page to fully load
    time.sleep(3)

    # Scroll down the page to load more videos
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Extract the page source after JavaScript has run
    page_source = driver.page_source

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Close the browser
    driver.quit()

    # List to hold video details
    videos = []

    # Extract information for each video on the page
    for video in soup.find_all('ytd-rich-item-renderer', class_='style-scope ytd-rich-grid-renderer'):
        try:
            link = video.find('a', id='thumbnail')['href']
            title = video.find('yt-formatted-string', id='video-title').text

            video_info = {
                'Title': title,
                'Link': f"https://www.youtube.com{link}",
            }

            videos.append(video_info)
        except Exception as e:
            print(f"Error processing video: {e}")

    # Set folder path for saving data
    data_folder_path = save_path.removesuffix('.csv', '').strip() if save_path != ... else 'Data'

    # Create folder if it doesn't exist
    if not os.path.exists(data_folder_path):
        os.makedirs(data_folder_path)
        print(f"Folder '{data_folder_path}' has been created.")
    else:
        print(f"Folder '{data_folder_path}' already exists.")

    # Specify the file name
    csv_file = f"{data_folder_path}/{youtube_id}.csv"

    # Define CSV header
    header = ['Title', 'Link']

    # Write video details to CSV file
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(videos)

    # Load data into a DataFrame
    data = pd.read_csv(csv_file)

    # Print save confirmation or remove the file based on the `save_data` flag
    if save_data:
        print(f"Data saved to {csv_file}")
    else:
        os.remove(csv_file)

    return data

def get_transcript(video_url: str) -> str:
    """
    Retrieves the transcript for a given YouTube video.

    Args:
        video_url (str): URL of the YouTube video.

    Returns:
        str: Transcript text.
    """
    # Extract the video ID from the URL
    video_id = video_url.split('v=')[1]

    # Get the transcript using YouTubeTranscriptApi
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # Combine the text from the transcript
    transcript_text = "\n".join([entry['text'] for entry in transcript])

    return transcript_text

def get_script_framework(scripts: pd.DataFrame, language: str = 'vietnamese', save_data: bool = True):
    """
    Processes a DataFrame of video scripts and edits them using a prompt.

    Args:
        scripts (pd.DataFrame): DataFrame containing video titles and scripts.
        language (str, optional): Language to be used in the prompt. Defaults to 'vietnamese'.
        save_data (bool, optional): Whether to save the result to a file. Defaults to True.

    Returns:
        list: List of scripts that caused exceptions during processing.
        str: Combined result of processed scripts.
    """
    if scripts.shape[1] < 2:
        raise ValueError('DataFrame must have at least 2 fields: "Title" and "Script".')

    # Define the prompt format
    prompt = 'Edit the Vlog script based on the following content in {language}: {script}'

    # Initialize the model
    model = GeminiModel()

    result = ''
    exception_videos = []
    overload_videos = []

    # Iterate through each script in the DataFrame
    for idx, row in scripts.iterrows():
        title = row['Title']
        script = row['Script']
        item = {'Title': title, 'Script': script}

        print(f'Processing: {title} - ({idx + 1}/{scripts.shape[0]})')

        # Format the prompt
        text = prompt.format(language=language, script=script)

        # Check for input overload
        if len(text) >= 100_000:
            overload_videos.append(item)
            print('Overload input!')
        else:
            try:
                # Get the model response
                response = model.response(text, '')
                result += f'## {title}\n + {response}\n\n'
            except Exception as e:
                print(f'Exception at - {title}: {e}')
                exception_videos.append(item)

    # Save the result if `save_data` is True
    if save_data:
        file_path = 'Script/result.txt'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, 'w+', encoding='utf-8') as f:
                f.write(result)
            print('Save data succesfully ' + file_path)
        except Exception as e:
            print(f'Error {e} when saving file')

    return result, exception_videos, overload_videos
