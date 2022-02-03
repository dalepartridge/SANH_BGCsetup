# SANH_SAsia_BGCsetup

This repository details the configuration of the Biogeochemistry component of the SANH (South Asian Nitrogen Hub) project, funded by UKRI (UK Research and Innovation) under a Global Challenges Research Fund.

The set up expands on the physical configuration provided here: *****PATH TO PHYS SETUP*****

The configuration requires the execution of four scripts to create the initial conditions (IC), lateral boundaries (OBC), surface boundaries (SBC) and to add addition river nutrients to the existing files from the physical setup. All scripts require the paths defined in *set_paths.sh*

## Initial Conditions
*create_IC.sh*  
Create the initial conditions using data from:  
- World Ocean Atlas (Montly climatology files for phosphate, silicate, nitrate and oxygen. Extracted files are the mean of December and January for a run start at the beginning of the year), https://www.nodc.noaa.gov/OC5/woa18/  
- Global Ocean Data Analysis Project (Mapped fields of Total Alkalinity and DIC. Extracted files were reordered across the dateline before extracting the region), https://www.glodap.info/  
- Ocean Color Climate Change Initiative (Montly composites of Chlorophyll-a and a filled climatology of the Gelbstoff absorption coefficient), http://www.esa-oceancolour-cci.org  
- Integrated Global Biogeochemical Modelling Network (Model output of Zooplankton and POM), provided directly from Lee de Mora (ledm@pml.ac.uk)  

## Lateral Boundary Condtions
*create_OBC.sh*  

Lateral boundary conditions are provided using monthly climatological data, with DIC and Total Alkalinity provided by GLODAP, and nutrients (nitrate, phosphate, silicate and oxygen) provided by World Ocean Atlas (WOA). 
- For WOA data the monthly fields are available down to a maximum depth of 800m, whilst their annual dataset contains data down to depth of 5500m. To achieve both a full depth profile and keep the seasonal variability, the annual fields below 800m have been added to the monthly records before extracting the boundary forcings. 
- GLODAP data is available as an annual field. To enable seasonal variability we assume that DIC/Alkalinity seasonality is driven by biogeochemical processes only. Therefore approximate seasonal fields can be defined in terms of nitrate anomalies, making use of the the Redfield ratio to convert from nitrogen to carbon for DIC

## Surface Conditions
*create_SBC.sh*  

Create surface boundary conditions using data from:
- Ocean Color Climate Change Initiative (Filled climatology of the Gelbstoff absorption coefficient), http://www.esa-oceancolour-cci.org
- Wet and Dry Nitrogen deposition https://data.isimip.org/
- CMIP5 (pCO2 data under scenario RCP8.5), https://www.iiasa.ac.at/web-apps/tnt/RcpDb/

## Rivers
*create_RIV.sh*  

River nitrate, phosphate and silicate provided through GLOBALNEWS with the physical river values, along with fields for DOM and POM. DOM take up is estimated to be 25%, and POM is around 35%. This script also adds the additional fields for Oxygen, DIC and TAlk based on:  
- Oxygen values are calculate at saturation using surface air temperature and the formula provided here https://www.waterontheweb.org/under/waterquality/oxygen.html  
- TAlk assumed to be a constant value of 1500 mmol/m3, based upon GEMS/GLORI project
- DIC calculated from carbonate equilibruum equation found in the ERSEM carbonate module (ICALC=4) using surface air temperature, pCO2, TAlk above and salinity at zero.  



