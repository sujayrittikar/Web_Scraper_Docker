def export_data():
    # Function to extract some data
    def extract_data():
        from bs4 import BeautifulSoup
        import requests

        url = 'https://www.imdb.com/list/ls036417104/'
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        # //div[@class='lister-item mode-detail']
        entities = soup.find_all('div', {'class': 'lister-item mode-detail'})
        list_of_dicts = []
        for entity in entities:
            anime = entity.find('h3').find('a').text.strip()
            rank = entity.find('h3').find_all('span')[0].text.strip()
            years = entity.find('h3').find_all('span')[1].text.strip()

            certificate = ''
            try:
                certificate = entity.find('span', {'class': 'certificate'}).text.strip()
                certificate = certificate.replace('\n', '')
            except:
                pass

            runtime = ''
            try:
                runtime = entity.find('span', {'class': 'runtime'}).text.strip()
            except:
                pass

            genre = ''
            try:
                genre = entity.find('span', {'class': 'genre'}).text.strip()
                genre = genre.replace(',', ';')
            except:
                pass
            
            rating = ''
            try:
                rating = entity.find('span', {'class': 'ipl-rating-star__rating'}).text.strip()
            except:
                pass

            story = str(entity.find_all('p')[1].text).strip()
            story = story.replace('See full summary\xa0»', '')
            while story.count('  ')>0:
                story = story.replace('  ', ' ')

            stars = str(entity.find_all('p')[2].text).strip()
            stars = stars.replace('\n', '')
            stars = stars.replace('Stars:', '')
            stars = stars.replace('Directors:', '')
            stars = stars.replace('|', '')
            while stars.count('  ')>0:
                stars = stars.replace('  ', ' ')
            stars = stars.replace(',', ';')

            votes = str(entity.find_all('p')[3].text).strip()
            votes = votes.replace('\n', '')
            votes = votes.replace('Votes:', '')
            votes = votes.strip()
            
            d = {}
            d['anime'] = anime
            d['rank'] = rank
            d['years'] = years
            d['certificate'] = certificate
            d['runtime'] = runtime
            d['genre'] = genre
            d['rating'] = rating
            d['summary'] = story
            d['stars'] = stars
            d['votes'] = votes

            list_of_dicts.append(d)

        return list_of_dicts

    # Function to perform some transformation of extracted data
    def transform_data(list_of_dicts):
        if len(list_of_dicts)>0:
            for d in range(len(list_of_dicts)):
                if 'rank' in list_of_dicts[d].keys():
                    # Cleaning the Rank: 1. -> 1
                    # Changing data type of rank to int
                    rank = list_of_dicts[d]['rank']
                    rank = rank.replace('.', '').strip()
                    rank = int(rank)
                    list_of_dicts[d]['rank'] = rank
                if 'rating' in list_of_dicts[d].keys():
                    # Changing data type of rating to float
                    list_of_dicts[d]['rating'] = float(list_of_dicts[d]['rating'])
                if 'votes' in list_of_dicts[d].keys():
                    list_of_dicts[d]['votes'] = list_of_dicts[d]['votes'].replace(',', '')
                    list_of_dicts[d]['votes'] = int(list_of_dicts[d]['votes'])
            return list_of_dicts
        else:
            raise Exception("Empty data list")


    def upload_to_s3(filename, resp, debug=True):
        '''
            Upload a file to s3
        '''
        import os
        import boto3
        import logging
        from traceback import print_exc
        import botocore.exceptions as boto_exc

        ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
        SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
        AWS_REGION = ""
        # filename = f'{filename}'
        S3_CLIENT = boto3.client("s3", region_name=AWS_REGION, aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
        try:
            S3_CLIENT.put_object(
                Bucket='', 
                Key=filename,
                Body=resp)
            logging.info(
                "UPLOADED FILE TO S3, FILE PATH : %s", filename)
            print(f"Uploaded {filename}....................................")
        except boto_exc:
            print_exc()
        except Exception:
            print_exc()


    # Load the transformed data on s3
    import pandas as pd
    from io import StringIO

    extracted_data = extract_data()
    transformed_data = transform_data(extracted_data)
    dataframe = pd.DataFrame(transformed_data)

    csv_buf = StringIO()
    dataframe.to_csv(csv_buf, header=True, index=False)
    csv_buf.seek(0)
    upload_to_s3(filename='top_50_animes.csv', resp=csv_buf.getvalue())

if __name__=='__main__':
    export_data()