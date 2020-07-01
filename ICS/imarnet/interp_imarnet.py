import fileinput
import os
import re
import sys

def create_namelists(template_dir,dat):
    templates = ['1_initcd_source_to_source_var.namelist.template',
                 '2_source_weights_var.namelist.template',
                 '3_initcd_source_to_nemo_var.namelist.template']
    namelists = ['1_initcd_{}_to_{}_{}.namelist'.format(dat['SOURCEID'],dat['SOURCEID'],dat['VAR']),
                 '2_{}_weights_{}.namelist'.format(dat['SOURCEID'],dat['VAR']),
                 '3_initcd_{}_to_nemo_{}.namelist'.format(dat['SOURCEID'],dat['VAR'])]
    for t,n in zip(templates,namelists):
        with open(template_dir+t) as fin, \
             open(n,'w') as fout:
            for l in fin.readlines():
                a = l 
                for d in dat:
                    a = re.sub('__'+d+'__',dat[d],a)
                fout.write(a)
            fin.close()
            fout.close()
    return

data = {
        'SOURCEID':'imarnet',
        'STIMEVAR':'time',
        'SLONVAR':'longitude',
        'SLATVAR':'latitude',
        'SZVAR':'depth',
        'TARGETID': 'SANH',
        'TAG': 'IC',
        'DOMAIN': 'domain_cfg.nc'
       }

meso_zoo = ['TRNZ4_c']
micro_zoo = ['TRNZ5_c','TRNZ5_n','TRNZ5_p']
heteroflagellates = ['TRNZ6_c','TRNZ6_n','TRNZ6_p']
small_pom = ['TRNR4_c','TRNR4_n','TRNR4_p']
med_pom = ['TRNR6_c','TRNR6_n','TRNR6_p','TRNR6_s']
large_pom = ['TRNR8_c','TRNR8_n','TRNR8_p','TRNR8_s']

vars={}
for v in meso_zoo + micro_zoo + heteroflagellates:
    vars[v.replace('_','')] = {'SFILE': 'iMarNet_data.nc',
                         'VARL': 'Zooplankton',
                         'OVAR': v,
                         'SCALE': '1.0'
                         }
for v in small_pom + med_pom + large_pom:
    vars[v.replace('_','')] = {'SFILE': 'iMarNet_data.nc',
                         'VARL': 'POM',
                         'OVAR': v,
                         'SCALE': '1.0'
                         }

for i,v in enumerate(vars):
    create_namelists(sys.argv[1],{'VAR':v, **data, **vars[v]})
    
    if i == 0:
        os.system('sh ./interp_IC_initial.sh {} {} {} {}'.format(v, vars[v]['SFILE'], data['SOURCEID'], data['STIMEVAR']))
    else:
        os.system('sh ./interp_IC_additional.sh {} {} {}'.format(v, vars[v]['SFILE'], data['SOURCEID']))
