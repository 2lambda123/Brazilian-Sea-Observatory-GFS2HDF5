import re, sys
import datetime
import time
import glob, os, shutil
import subprocess
from ftplib import FTP
import requests
from Input_GFS2HDF5 import *


#####################################################
def download_file(path,filename):       
        f_exists = os.path.exists(filename + '.grib2')
        if f_exists:
                f_size = os.path.getsize(filename + '.grib2')
        else:
                f_size = 0.
        
        tempoIni = time.time()
        
        url_inv = path+filename+".idx"
        url_grb = path+filename+""
        print (url_inv)
        print (url_grb)
                
        while not f_exists or f_size < min_file_size:

                print("Downloading: ", url_grb)
                #Windows
                out = os.system('PERL ../get_inv.pl '+url_inv+'|egrep "(:TMP:2 m above|:UGRD:10 m above|:VGRD:10 m above|:RH:2 m above|:PRMSL:|:LAND:|:TCDC:entire atmosphere|:DLWRF:surface|:DSWRF:surface|:HPBL:surface|:ALBDO:surface|:APCP:surface)" | PERL ../get_grib.pl '+ url_grb + " " + filename + ".grib2")
                
                #Linux
                #out = os.system(download_dir+ '/get_inv.pl '+url_inv+'|egrep "(:TMP:2 m above|:UGRD:10 m above|:VGRD:10 m above|:RH:2 m above|:PRMSL:|:LAND:|:TCDC:entire atmosphere|:DLWRF:surface|:DSWRF:surface|:HPBL:surface|:ALBDO:surface|:APCP:surface)" |'+ download_dir + '/get_grib.pl '+ url_grb + " " + filename + ".grib2")                

                if out != 0: 
                        print ("File not found")
                        print ("Trying again in ", wait_time, " s...")
                        ## aguarda
                        time.sleep(wait_time)
                        tempoAtual = time.time()
                        tempoTotal = tempoAtual-tempoIni

                        if tempoTotal > wait_total_time: 
                                msg = 'Failed to download GFS files \n' + url_grb + ' not found after ' + wait_total_time + ' s'
                                print(msg)
                                telegram_msg(msg) 
                                break #encerra o loop
                
                f_exists = os.path.exists(filename + '.grib2')
                f_size = os.path.getsize(filename + '.grib2')
#####################################################
def copy_file(filename):
        global f_missing
        f_exists = os.path.exists(filename)
        
        if f_exists:
                f_size = os.path.getsize(filename)

        else:
                f_size = 0.

        if f_exists and f_size > min_file_size:
                
                print(filename)         
                shutil.copy(filename, ConvertToNetcdf_dir)
        else:
                print(filename, "is missing or is too small.")
                f_missing = True
#####################################################
#Funcao para envio de mensagem pelo Bot do Telegram
def telegram_msg(message):
        if telegram_messages == 1:
                #message = "hello from your telegram bot"
                urlbot = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                print(requests.get(urlbot).json()) # this sends the message
#####################################################

initial_date = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min) + datetime.timedelta(days = refday_to_start)

#Download
if download == 1:
        
        download_dir_date = download_dir+"/"+str(initial_date.strftime("%Y%m%d"))
        if not os.path.exists(download_dir_date):
            os.makedirs(download_dir_date)
                        
        os.chdir(download_dir_date)
                
        number_of_downloads = number_of_runs * 24 + 2
        
        path = url+"/gfs." + str(initial_date.strftime("%Y%m%d")) + "/00/atmos/"
        
        if requests.head(path).status_code < 400:
                for hour in range (0,number_of_downloads):
                        
                        filename = file_initial_name + str(hour).rjust(3,'0')

                        download_file(path,filename)
        else:
                msg = 'Failed to download GFS files \n' + path + ' does not exist.'
                print(msg)
                telegram_msg(msg) 

                                
if ConvertToHdf5 == 1:

        for run in range (0,number_of_runs):    
                f_missing = False
                #Clean up folders       
                os.chdir(ConvertToNetcdf_dir)
                        
                files = glob.glob("*.nc")
                for filename in files:
                        os.remove(filename)
                        
                files = glob.glob("*.grib*")
                for filename in files:
                        os.remove(filename)     
                        
                os.chdir(ConvertToHdf5_dir)
                
                files = glob.glob("*.hdf*")
                for filename in files:
                        os.remove(filename)
                        
                files = glob.glob("*.nc")       
                for filename in files:
                        os.remove(filename)

                #ConvertToNetcdf
                print("ConvertToNetcdf")
                #os.chdir(download_dir)
                
                for hour in range (0,26):
                        #Vai buscar o arquivo 024 do dia anterior e substitui como 000, pois no arquivo 000 faltam os parâmetros DLWRF e DSWRF
                        if run == 0 and hour == 0:
                                download_date_before = initial_date + datetime.timedelta(days = -1)
                                
                                download_dir_date = download_dir+"/"+str(download_date_before.strftime("%Y%m%d"))
                                
                                os.chdir(download_dir_date)
                                filename = file_initial_name + "023" + ".grib2"
                                copy_file(filename)
                                os.chdir(ConvertToNetcdf_dir)
                                os.rename(filename, filename.replace("023","000"))
                                
                                os.chdir(download_dir_date)
                                filename = file_initial_name + "024" + ".grib2"
                                copy_file(filename)    
                                os.chdir(ConvertToNetcdf_dir)
                                os.rename(filename, filename.replace("024","0000"))
                                
                        else:
                                download_dir_date = download_dir+"/"+str(initial_date.strftime("%Y%m%d"))
                                os.chdir(download_dir_date)
                                        
                                fcst_hour = hour + run*24
                                if hour == 0:
                                
                                        filename = file_initial_name + str(fcst_hour-1).rjust(3,'0')+".grib2"
                                        copy_file(filename)
                                        
                                        filename = file_initial_name + str(fcst_hour).rjust(3,'0')+".grib2"
                                        copy_file(filename)

                                else:
                                        
                                        filename = file_initial_name + str(fcst_hour).rjust(3,'0')+".grib2"
                                        copy_file(filename)
                                

                
                if f_missing == False:
                        os.chdir(ConvertToNetcdf_dir)

                        os.system(python_path + " " +ConvertToNetcdf_dir+"/Convert2Netcdf.py")
                        
                        nc_files = glob.iglob(os.path.join(ConvertToNetcdf_dir,"*.nc"))
                        for file in nc_files:
                                shutil.move(file, ConvertToHdf5_dir)
                                
                        #ConvertToHdf5
                        os.chdir(ConvertToHdf5_dir)
                        
                        #Linux (use sh to define the env paths to run with cron)
                        #os.system(ConvertToHdf5_dir+"/ConvertToHDF5.sh")

                        #Windows
                        os.system(ConvertToHdf5_dir+"/ConvertToHdf5_release_single.exe")
                        
                        start_date = initial_date + datetime.timedelta(days = run)
                        end_date = start_date + datetime.timedelta(days = 1)
                        output_dir = backup_path+"//"+str(start_date.strftime("%Y%m%d")) + "_" + str(end_date.strftime("%Y%m%d"))
                                
                        if not os.path.exists(output_dir):
                                os.makedirs(output_dir)
                        
                        hdf_files = glob.iglob(os.path.join(ConvertToHdf5_dir,"*.hdf*"))
                        for file in hdf_files:
                                shutil.copy(file, output_dir)
                else:
                        msg = 'Failed to convert GFS files to HDF5 on date: ' + str(download_date.strftime("%Y%m%d"))
                        print(msg)
                        telegram_msg(msg)    

if remove_old_files == 1:
        for file in glob.glob(download_dir+'/*/'): 
                file_age = os.path.getctime(os.path.join(download_dir,file))
                if (time.time() - file_age) // 86400 >= days_to_remove:
                        #os.remove(file)
                        shutil.rmtree(file)
                        print('{} removed'.format(file))
        
