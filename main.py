import pandas as pd
import urllib
import requests

#data is currently in ./data.tsv

data = pd.read_csv('./data.tsv', sep='\t')

#print headers
#print(data.columns)

#we want the lat and long of each location from the location column

localities = data['Location']

print(localities)

#format of column is Region / Country / State / City / County / Airport, where everything after state is optional
# Example: North America / USA / California / San Mateo County / San Francisco International Airport
#we want the lat and long of our best guess airport for each location

output_df = pd.DataFrame(columns=['Region', 'Country', 'State', 'City', 'County', 'Airport', 'Latitude', 'Longitude'])

#output_df['Location'] = localities.apply(lambda x: [i.strip() for i in x.split('/') if i][-1])
# Create a dictionary to store queried locations
queried_locations = {}

for i in range(len(localities)):
    output_df['Region'][i] = localities[i].split('/')[0].strip()
    output_df['Country'][i] = localities[i].split('/')[1].strip()
    output_df['State'][i] = localities[i].split('/')[2].strip()
    output_df['City'][i] = localities[i].split('/')[3].strip() if len(localities[i].split('/')) > 3 else ''
    output_df['County'][i] = localities[i].split('/')[4].strip() if len(localities[i].split('/')) > 4 else ''
    output_df['Airport'][i] = localities[i].split('/')[-1].strip() if len(localities[i].split('/')) > 5 else ''

    query = output_df['Airport'][i] if output_df['Airport'][i] else output_df['City'][i] + ", " + output_df['State'][i] if output_df['City'][i] else output_df['State'][i]
    query += ' Airport' if 'Airport' not in query else ''

    # Check if the location has already been queried
    if query in queried_locations:
        print('Latitude: '+queried_locations[query]['lat']+', Longitude: '+queried_locations[query]['lon'])
        output_df['Latitude'][i] = queried_locations[query]['lat']
        output_df['Longitude'][i] = queried_locations[query]['lon']
    else:
        url = 'https://nominatim.openstreetmap.org/search?q=' + urllib.parse.quote(query) + '&format=json'
        response = requests.get(url).json()

        if response:
            print('Latitude: '+response[0]['lat']+', Longitude: '+response[0]['lon'])
            output_df['Latitude'][i] = response[0]['lat']
            output_df['Longitude'][i] = response[0]['lon']

            # Store the location in the dictionary
            queried_locations[query] = {'lat': response[0]['lat'], 'lon': response[0]['lon']}
        else:
            print('No results found for query: ' + query)

output_df.to_csv('output.tsv', sep='\t', index=False)
