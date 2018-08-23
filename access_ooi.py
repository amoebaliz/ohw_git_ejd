
import requests, re, os, warnings, json, time
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt


# Load your credentials
with open("credentials.json", "r") as read_file:
     data = json.load(read_file)
token = data['token']
username = data['username']

# Build API Query
DATA_API_BASE_URL = 'https://ooinet.oceanobservatories.org/api/m2m/12576/sensor/inv/'
data_request_url = DATA_API_BASE_URL+\
                    'GS01SUMO/'+\
                    'RID16/'+\
                    '03-CTDBPF000/'+\
                    'telemetered/'+\
                    'ctdbp_cdef_dcl_instrument'+'?'

r = requests.get(data_request_url, params=None, auth=(username, token)) # Request data
data = r.json() # verify request

print(data)

check_complete = data['allURLs'][1] + '/status.txt'
for i in range(1800): 
    r = requests.get(check_complete)
    if r.status_code == requests.codes.ok:
        print('request completed')
        break
    else:
        time.sleep(1)

url = data['allURLs'][0]
tds_url = 'https://opendap.oceanobservatories.org/thredds/dodsC'
datasets = requests.get(url).text
urls = re.findall(r'href=[\'"]?([^\'" >]+)', datasets)
x = re.findall(r'(ooi/.*?.nc)', datasets)
for i in x:
    if i.endswith('.nc') == False:
        x.remove(i)
for i in x:
    try:
        float(i[-4])
    except:
        x.remove(i)
datasets = [os.path.join(tds_url, i) for i in x]
datasets

ds = xr.open_mfdataset(datasets)
ds = ds.swap_dims({'obs': 'time'})
ds = ds.sortby('time') # data from different deployments can overlap so we want to sort all data by time stamp.
for var in ds.variables:
    try:
        print(ds[var].standard_name + ':', var)
    except: #hack to only print variables that have a standard name attribute
        pass

fig, (ax, ax_qc) = plt.subplots(2,sharex=True,gridspec_kw={'height_ratios':[3, 1]})
fig.set_size_inches(8,8)
ax.plot(ds['time'], ds['temp'], marker='.', linewidth=0)
ax.set_ylabel('Temperature')
ax_qc.plot(ds['time'], ds['temp_qc_executed'],marker='.', linewidth=0)
ax_qc.plot(ds['time'], ds['temp_qc_results'],marker='.', linewidth=0)
ax_qc.legend()

fig.autofmt_xdate()
fig.tight_layout()

print 'MEEP'




