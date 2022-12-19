import datetime, os

url="https://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod"
file_initial_name = "gfs.t00z.pgrb2.0p25.f"


dirpath = os.getcwd()
download_dir = (dirpath+"/Download")
ConvertToNetcdf_dir = (dirpath+"/ConvertToNetcdf")
ConvertToHdf5_dir = (dirpath+"/ConvertToHdf5")
backup_path = (dirpath+"/Backup")

#To avoid problems with cron in Linux define the entire path to python exe"
python_path = "python"

#Always forecast
#forecast_mode = 1
refday_to_start = 0
number_of_runs = 2

download = 0
#Tempo de espera para uma nova tentativa de download do arquivo (em segundos)
wait_time = 300
#Tempo de espera total em s para o download do arquivo (em segundos) 
wait_total_time = 1800
#Tamanho mínimo do arquivo em bits
min_file_size = 3000000


ConvertToHdf5 = 1

telegram_messages = 0
#TOKEN = "YOUR TELEGRAM BOT TOKEN"
#chat_id = "YOUR CHAT ID"


#Apaga arquivos grib2 antigos da pasta download_dir
remove_old_files = 0
days_to_remove = 7
