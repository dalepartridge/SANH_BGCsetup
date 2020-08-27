# SANH_SAsia_BGCsetup

This repository details the configuration of the Biogeochemistry component of the SANH (South Asian Nitrogen Hub) project, funded by UKRI (UK Research and Innovation) under a Global Challenges Research Fund.

The set up expands on the physical configuration provided here: *****PATH TO PHYS SETUP*****

The configuration requires the execution of three scripts to create the initial conditions (IC), lateral boundaries (OBC) and surface boundaries (SBC). All three require the paths defined in *set_paths.sh*

## Initial Conditions
*create_IC.sh*  
Create the initial conditions using data from:  
- World Ocean Atlas (Montly climatology files for phosphate, silicate, nitrate and oxygen. Extracted files are the mean of December and January for a run start at the beginning of the year), https://www.nodc.noaa.gov/OC5/woa18/  
- Global Ocean Data Analysis Project (Mapped fields of Total Alkalinity and DIC. Extracted files were reordered across the dateline before extracting the region), https://www.glodap.info/  
- Ocean Color Climate Change Initiative (Montly composites of Chlorophyll-a and a filled climatology of the Gelbstoff absorption coefficient), http://www.esa-oceancolour-cci.org  
- Integrated Global Biogeochemical Modelling Network (Model output of Zooplankton and POM), provided directly from Lee de Mora (ledm@pml.ac.uk)  

## Lateral Boundary Condtions
*create_OBC.sh*  

Create OBC conditions using data from CMEMS (Monthly averages of nitrate, phosphate, silicate and oxygen from GLOBAL_REANALYSIS_BIO_001_029), https://resources.marine.copernicus.eu/?option=com_csw&view=details&product_id=GLOBAL_REANALYSIS_BIO_001_029


## Surface Conditions
*create_SBC.sh*  

Create surface boundary conditions using data from:  
- Ocean Color Climate Change Initiative (Filled climatology of the Gelbstoff absorption coefficient), http://www.esa-oceancolour-cci.org  
- University of Minnesota (Global wet and dry Nitrogen deposition provided for the years 1984-1986, 1994-1996, 2004-2006, and 2014-2016), https://conservancy.umn.edu/handle/11299/197613  
- CMIP5 (pCO2 data under scenario RCP8.5), https://www.iiasa.ac.at/web-apps/tnt/RcpDb/  

## Rivers
*create_RIV.sh*  

River nitrate, phosphate and silicate provided through GLOBALNEWS with the physical river values.This script adds the additional fields for Oxygen, DIC and TAlk based on:  
- Oxygen values are calculate at saturation using surface air temperature and the formula provided here https://www.waterontheweb.org/under/waterquality/oxygen.html  
- TAlk assumed to be a constant value of 1500 mmol/m3, based upon GEMS/GLORI project
- DIC calculated from carbonate equilibruum equation found in the ERSEM carbonate module (ICALC=4) using surface air temperature, pCO2, TAlk above and salinity at zero.  



