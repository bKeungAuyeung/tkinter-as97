# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import subplots

# periods considered
as97_const = pd.read_excel("as97_const.xls", sheet_name="const") # constants from as97
periods = np.asarray(as97_const["period"], "float") # seconds

# collect eq parameters from user inputs
## currently, using loma prieta as an example. 
magnitude = 6.94 # moment magnitude 
r_rup = 9.64 # distance to rupture in km
site_type = 0 # site class. 0 for rock site, 1 for soil site
mechanism = 0.5 # rupture mechanism. 1 for revserse, 0.5 for reverse-oblique, 0 otherwise
hanging_wall = 0 # 1 for sites over a hanging wall, 0 otherwise
n = 2 # vertical = 3, horizontal = 2 (AS97)

# collect factors on rock from as97 model 

# collect R values
R = np.zeros(len(as97_const["period"])) # initialize R
for i in range(len(as97_const["period"])): # for each period
    R[i] = (r_rup**2 + as97_const["c4"][i]**2)**0.5

# collect f1 values
f1_rock = np.zeros(len(as97_const["period"])) # initialize f1
for i in range(len(as97_const["period"])): # for each period
    if magnitude<= as97_const["c1"][i]: # if M <= c1...
        f1_rock[i] = as97_const["a1"][i] + (as97_const["a2"][i] * (magnitude - as97_const["c1"][i])) + (as97_const["a12"][i]*(8.5 - magnitude)**n) + \
            (as97_const["a3"][i] +(as97_const["a13"][i] * (magnitude-as97_const["c1"][i])))*np.log(R[i]) # collect f1 value
    else: # if M > c1...
        f1_rock[i] = as97_const["a1"][i] + (as97_const["a4"][i] * (magnitude - as97_const["c1"][i])) + (as97_const["a12"][i]*(8.5 - magnitude)**n) + \
            (as97_const["a3"][i] +(as97_const["a13"][i] * (magnitude-as97_const["c1"][i])))*np.log(R[i]) # collect f1 value
            
# collect f3 values
f3_rock = np.zeros(len(as97_const["period"])) # initialize f3
for i in range(len(as97_const["period"])): # for each period
    if magnitude <= 5.8: # if M <= 5.8...
        f3_rock[i] = as97_const["a5"][i] # collect f3 value
    elif 5.8 < magnitude  <= as97_const["c1"][i]: # if M > 5.8 and M <= 6.2...
        f3_rock[i] = as97_const["a5"][i] + (((as97_const["a6"][i] - as97_const["a5"][i])*(magnitude-5.8))/(as97_const["c1"][i]-5.8)) # collect f3 value
    else: # if M > 6.2...
        f3_rock[i] = as97_const["a6"][i] # collect f3 value

# in order to get f4, we need fHW_hw and fHW_r 
fHW_hw_rock = np.zeros(len(as97_const["period"])) # initialize fHW_hw
for i in range(len(as97_const["period"])): # for each period
    if magnitude <= 5.5: # if if M <= 5.5
        fHW_hw_rock[i] = 0 # collect fHW_hw value
    elif 5.5 < magnitude  <= 6.5: # if 5.5 < M <= 6.5...
        fHW_hw_rock[i] = magnitude - 5.5 # collect fHW_hw value
    else: # if M > 6.5
        fHW_hw_rock[i] = 1 # collect fHW_hw value

fHW_r_rock = np.zeros(len(as97_const["period"])) # initialize fHW_r
for i in range(len(as97_const["period"])): # for each period
    if r_rup < 4: 
        fHW_r_rock[i] = 0 # collect fHW_r value
    elif 4 <= r_rup < 8: 
        fHW_r_rock[i] = (as97_const["a9"][i] * (r_rup - 4))/4 # collect fHW_r value
    elif 8 <= r_rup < 18: 
        fHW_r_rock[i] = as97_const["a9"][i] # collect fHW_r value
    elif 18 <= r_rup < 25: 
        fHW_r_rock[i] = as97_const["a9"][i] * (((1-(r_rup - 18))/7))  # collect fHW_r value
    else:
        fHW_r_rock[i] = 0 # collect fHW_r value

# finally we can get f4...
f4_rock = fHW_hw_rock * fHW_r_rock

# collect f5 values. must ignore f5 first, then run again
f5_rock = np.zeros(len(as97_const["period"])) # initialize f5, we will collect this later

# factors_rock = pd.DataFrame({"f1": f1_rock, "f3": f3_rock, "f4": f4_rock})
factors_rock = pd.DataFrame({"f1": f1_rock, "f3": f3_rock, "f4": f4_rock, "f5": f5_rock})

# combine factors with flags to get ln(S_a) and by extension, S_a
loma_pga = 0 # we will collect this later

lnSa_rock_median = np.zeros(len(as97_const["period"])) # initialize lnSa
for i in range(len(as97_const["period"])): # for each period
    if i == 0:
        loma_pga = np.exp(f1_rock[i] + mechanism * f3_rock[i] + hanging_wall * f4_rock[i])  # collect lnSa value
        f5_rock[i] = as97_const["a10"][i] + as97_const["a11"][i] * np.log(loma_pga + as97_const["c5"][i]) # collect f5 value
        lnSa_rock_median[i] = f1_rock[i] + mechanism * f3_rock[i] + hanging_wall * f4_rock[i] + site_type*f5_rock[i]  # collect lnSa value
    else:
        for i in range(len(as97_const["period"])): # for each period
            f5_rock[i] = as97_const["a10"][i] + as97_const["a11"][i] * np.log(loma_pga + as97_const["c5"][i]) # collect f5 value
            lnSa_rock_median[i] = f1_rock[i] + mechanism * f3_rock[i] + hanging_wall * f4_rock[i] + site_type*f5_rock[i]  # collect lnSa value

Sa_rock_mean = np.exp(lnSa_rock_median)

# update rock factor f5
factors_rock["f5"] = f5_rock

# determine +/- 1σ 
sigma = np.zeros(len(as97_const['period']))
for i in range(len(as97_const['period'])):
    if magnitude <= 5:
        sigma[i] = as97_const["b5"][i]
    elif 5 < magnitude <= 7:
        sigma[i] = as97_const['b5'][i] - (as97_const['b6'][i] *( magnitude -5))
    else:
        sigma[i] = as97_const['b5'][i] - 2*as97_const['b6'][i]
# print(sigma)
factors_rock['sigma'] = sigma

lnSa_rock_high = np.zeros(len(as97_const['period']))
lnSa_rock_low = np.zeros(len(as97_const['period']))

for i in range(len(as97_const["period"])): # for each period
    lnSa_rock_high[i] = f1_rock[i] + mechanism * f3_rock[i] + hanging_wall * f4_rock[i] + site_type*f5_rock[i] + sigma[i] # collect lnSa value
    lnSa_rock_low[i] = f1_rock[i] + mechanism * f3_rock[i] + hanging_wall * f4_rock[i] + site_type*f5_rock[i] - sigma[i] # collect lnSa value

Sa_rock_high = np.exp(lnSa_rock_high)
Sa_rock_low = np.exp(lnSa_rock_low)

R = np.zeros(len(as97_const["period"])) # initialize R
for i in range(len(as97_const["period"])): # for each period
    R[i] = (r_rup**2 + as97_const["c4"][i]**2)**0.5

f1_soil = np.zeros(len(as97_const["period"])) # initialize f1
for i in range(len(as97_const["period"])): # for each period
    if magnitude <= as97_const["c1"][i]: # if M <= c1...
        f1_soil[i] = as97_const["a1"][i] + (as97_const["a2"][i] * (magnitude - as97_const["c1"][i])) + (as97_const["a12"][i]*(8.5 - magnitude)**n) + \
            (as97_const["a3"][i] +(as97_const["a13"][i] * (magnitude-as97_const["c1"][i])))*np.log(R[i]) # collect f1 value
    else: # if M > c1...
        f1_soil[i] = as97_const["a1"][i] + (as97_const["a4"][i] * (magnitude - as97_const["c1"][i])) + (as97_const["a12"][i]*(8.5 - magnitude)**n) + \
            (as97_const["a3"][i] +(as97_const["a13"][i] * (magnitude-as97_const["c1"][i])))*np.log(R[i]) # collect f1 value

# collect f3 values
f3_soil = np.zeros(len(as97_const["period"])) # initialize f3
for i in range(len(as97_const["period"])): # for each period
    if magnitude <= 5.8: # if M <= 5.8...
        f3_soil[i] = as97_const["a5"][i] # collect f3 value
    elif 5.8 < magnitude  <= as97_const["c1"][i]: # if M > 5.8 and M <= 6.2...
        f3_soil[i] = as97_const["a5"][i] + (((as97_const["a6"][i] - as97_const["a5"][i])*(magnitude-5.8))/(as97_const["c1"][i]-5.8)) # collect f3 value
    else: # if M > 6.2...
        f3_soil[i] = as97_const["a6"][i] # collect f3 value

# in order to get f4, we need fHW_hw and fHW_r 
fHW_hw_soil = np.zeros(len(as97_const["period"])) # initialize fHW_hw
for i in range(len(as97_const["period"])): # for each period
    if magnitude <= 5.5: # if if M <= 5.5
        fHW_hw_soil[i] = 0 # collect fHW_hw value
    elif 5.5 < magnitude  <= 6.5: # if 5.5 < M <= 6.5...
        fHW_hw_soil[i] = magnitude - 5.5 # collect fHW_hw value
    else: # if M > 6.5
        fHW_hw_soil[i] = 1 # collect fHW_hw value

fHW_r_soil = np.zeros(len(as97_const["period"])) # initialize fHW_r
for i in range(len(as97_const["period"])): # for each period
    if r_rup < 4: 
        fHW_r_soil[i] = 0 # collect fHW_r value
    elif 4 <= r_rup < 8: 
        fHW_r_soil[i] = (as97_const["a9"][i] * (r_rup - 4))/4 # collect fHW_r value
    elif 8 <= r_rup < 18: 
        fHW_r_soil[i] = as97_const["a9"][i] # collect fHW_r value
    elif 18 <= r_rup < 25: 
        fHW_r_soil[i] = as97_const["a9"][i] * (((1-(r_rup - 18))/7))  # collect fHW_r value
    else:
        fHW_r_soil[i] = 0 # collect soilr value

# finally we can get f4...
f4_soil = fHW_hw_soil * fHW_r_soil

# collect f5 values
f5_soil = np.zeros(len(as97_const["period"])) # initialize f5

factors_soil = pd.DataFrame({"f1": f1_soil, "f3": f3_soil, "f4": f4_soil, "f5": f5_soil})

# combine factors with flags to get ln(S_a) and by extension, S_a

lnSa_soil_median = np.zeros(len(as97_const["period"])) # initialize lnSa
for i in range(len(as97_const["period"])): # for each period
    if i == 0:
        loma_pga = np.exp(f1_soil[i] + mechanism * f3_soil[i] + hanging_wall * f4_soil[i])  # collect lnSa value
        f5_soil[i] = as97_const["a10"][i] + as97_const["a11"][i] * np.log(loma_pga + as97_const["c5"][i]) # collect f5 value
        lnSa_soil_median[i] = f1_soil[i] + mechanism * f3_soil[i] + hanging_wall * f4_soil[i] + site_type*f5_soil[i]  # collect lnSa value
    else:
        for i in range(len(as97_const["period"])): # for each period
            f5_soil[i] = as97_const["a10"][i] + as97_const["a11"][i] * np.log(loma_pga + as97_const["c5"][i]) # collect f5 value
            lnSa_soil_median[i] = f1_soil[i] + mechanism * f3_soil[i] + hanging_wall * f4_soil[i] + site_type*f5_soil[i]  # collect lnSa value
        
Sa_soil_mean = np.exp(lnSa_soil_median)

# determine +/- 1σ 

lnSa_soil_high = np.zeros(len(as97_const['period']))
lnSa_soil_low = np.zeros(len(as97_const['period']))

for i in range(len(as97_const["period"])): # for each period
    lnSa_soil_high[i] = f1_soil[i] + mechanism * f3_soil[i] + hanging_wall * f4_soil[i] + site_type*f5_soil[i] + sigma[i] # collect lnSa value
    lnSa_soil_low[i] = f1_soil[i] + mechanism * f3_soil[i] + hanging_wall * f4_soil[i] + site_type*f5_soil[i] - sigma[i] # collect lnSa value

Sa_soil_high = np.exp(lnSa_soil_high)
Sa_soil_low = np.exp(lnSa_soil_low)

factors_soil["f5"] = f5_soil

fig, ax = subplots(figsize=(4,3), tight_layout=True, dpi=300)
if site_type == 1: # if site type is soil
    ax.semilogx(periods, Sa_soil_mean, color = "#980043", label="Soil Spectra", linestyle = "-")
    ax.fill_between(periods, Sa_soil_low, Sa_soil_high, color = "#980043", alpha = 0.2, linestyle = ":")
else: # if site type is rock
    ax.semilogx(periods, Sa_rock_mean, color = "#810f7c", label="Rock Spectra", linestyle ="-")
    ax.fill_between(periods, Sa_rock_low, Sa_rock_high, color = "#810f7c", alpha = 0.2, linestyle = "--")

ax.set_xlabel("Structural Period [sec]", fontsize = 8)
ax.set_xbound(0.01, 5.2)
ax.set_ylabel("$S_a$ [g]", fontsize =8)
ax.set_ybound(0, 2)
ax.tick_params(which="both", direction = "in", labelsize = 8)
plt.legend(frameon = False, fontsize = 8, loc = "best")
plt.show()