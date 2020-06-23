# SANH_SEAsia_BGCsetup

This repository details the configuration of the Biogeochemistry component of the SANH (South Asian Nitrogen Hub) project, funded by UKRI (UK Research and Innovation) under a Global Challenges Research Fund.

The set up expands on the physical configuration provided here: *****PATH TO PHYS SETUP*****

The configuration requires the execution of three scripts to create the initial conditions (IC), lateral boundaries (OBC) and surface boundaries (SBC). All three require the paths defined in *set_paths.sh*

## Initial Conditions
*create_IC.sh*
Create the initial conditions using data from the World Ocean Atlas (Nutrients + Oxygen), Global Ocean Data Analysis Project (Alkalinity + DIC), Ocean Color Climate Change Initiative (Chloraphyll and Light Attenuation) and the Integrated Global Biogeochemical Modelling Network (Zooplankton and POM). The data has been extracted to the region to reduction interpolation compute time. 

## Lateral Boundary Condtions
*create_OBC.sh*

## Surface Conditions
*create_SBC.sh*


